"""
    Reference:
    - Reichenbach, T., Mobilia, M. & Frey, E. Mobility promotes and jeopardizes biodiversity in rock–paper–scissors games. Nature 448, 1046–1049 (2007).
    - Reichenbach, T., Mobilia, M., & Frey, E. (2007). Noise and correlations in a spatial population model with cyclic competition. Physical review letters, 99(23), 238105.
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns
import ternary
from numba import njit
from tqdm import tqdm
import argparse
import os

parser = argparse.ArgumentParser("PDE solution")
parser.add_argument("plot", help="If 'yes' snapshots of the simulation will be saved according to the number of snapshots (default=300). Otherwise no plot will be generated.", type=str)
parser.add_argument("size", help="Size of the lattice.", type=int)
parser.add_argument("total_steps", help="Number of simulation steps.", type=int)
parser.add_argument("mu", help="Reproduction rate.", type=float)
parser.add_argument("sigma", help="Dominance-removal rate.", type=float)
parser.add_argument("D", help="Hopping rate. Hopping is the movement an individual has when it moves from it's local site to a neighboring empty one.", type=float)
parser.add_argument("epsilon", help="Pair-exchange rate. Pair-exchange is the movement an in individual has when it switches it's local site with it's neighbor's. Compared to hopping, this is understood as movement through crowded areas where the movement of one must displace the other.", type=float)
parser.add_argument("snapshots", help="(Optional argument) Number of snapshots to save during the simulation.", type=int,
                    nargs='?', default=300)
args = parser.parse_args()

plot = args.plot

# if plot == 'y' or plot == 'yes':
#     try:
#         plt.rc('text', usetex=True)
#         plt.rc('font', family='serif')
#     except Exception as e:
#         print("LaTeX not found or not uploaded, using Matplotlib default font.")
#         print(f"Error type: {type(e)}\nError message: {e}")

@njit
def numba_choice(n, p):
    """
    Numba-compatible version of np.random.choice
    
    Parameters:
    - n: Number of possible choices
    - p: Probability weights (will be normalized)
    
    Returns:
    - Selected index
    """
    # Normalize probabilities
    p_norm = p / np.sum(p)
    
    # Generate cumulative probabilities
    cumulative_p = np.cumsum(p_norm)
    
    # Random uniform draw
    r = np.random.random()
    
    # Find the first index where cumulative prob exceeds random draw
    for i in range(n):
        if r <= cumulative_p[i]:
            return i
    
    # Fallback (should rarely happen due to normalization)
    return n - 1

@njit
def compute_global_rates(space, sigma=1.0, epsilon=5.0, mu=1.0, D=5.0):
    """
    Compute global reaction rates based on pair types and empty spaces
    
    Parameters:
    - space: Lattice grid
    - sigma: Competition rate
    - epsilon: Pair-exchange rate
    - mu: Reproduction rate
    - D: Hopping rate
    
    Returns:
    - Global reaction rates and corresponding reactions
    """
    size = space.shape[0]
    rates = np.zeros(4) # Reaction orders: competition, pair-exchange, reproduction, hopping
    reactions = []
    
    # Precompute pair counting
    pair_counts = {
        (1, 2): 0, (1, 3): 0,  # A-B, A-C interactions
        (2, 3): 0, (2, 1): 0,  # B-C, B-A interactions
        (3, 1): 0, (3, 2): 0   # C-A, C-B interactions
    }
    empty_count = 0
    
    # Count pair interactions and empty spaces
    for x in range(size):
        for y in range(size):
            if space[x, y] == 0:
                empty_count += 1
                continue
            
            # Check neighbors
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), 
                           (1,1), (1,-1), (-1,1), (-1,-1)]:
                nx, ny = (x + dx) % size, (y + dy) % size
                
                if space[nx, ny] == 0:
                    # Reproduction/Hopping to empty site
                    rates[2] += mu
                    reactions.append(('reproduction', (x, y), (nx, ny)))
                    
                    rates[3] += D
                    reactions.append(('hopping', (x, y), (nx, ny)))
                
                elif space[nx, ny] != space[x, y]:
                    # Pair interaction
                    pair_type = (space[x, y], space[nx, ny])
                    rates[0] += sigma
                    reactions.append(('competition', (x, y), (nx, ny)))
                    
                    rates[1] += epsilon
                    reactions.append(('pair-exchange', (x, y), (nx, ny)))
    
    return rates, reactions

@njit
def gillespie_lattice_step(space, t, mcs, sigma=1.0, mu=1.0, epsilon=5.0, D=5.0):
    """
    Perform a single Gillespie algorithm step on the lattice
    
    Parameters:
    - space: Lattice grid
    - t: Time array
    - sigma: Competition rate
    - mu: Reproduction rate
    - epsilon: Pair-exchange rate
    - D: Hopping rate
    
    Returns:
    - Updated space grid
    - Updated time array
    """
    # Compute global reaction rates
    rates, reactions = compute_global_rates(space, sigma, epsilon, mu, D)
    
    population = float(len(np.where(space != 0)[0]))
    
    if len(rates) == 0:
        return space, t, mcs
    
    # Total rate
    total_rate = np.sum(rates)
    
    # Generate time step
    tau = np.random.exponential(1/total_rate)
    
    # Select reaction
    reaction_index = numba_choice(len(rates), p=rates/total_rate)
    
    if reaction_index == 0:
        selected_reaction = 'competition'
    elif reaction_index == 1:
        selected_reaction = 'pair-exchange'
    elif reaction_index == 2:
        selected_reaction = 'reproduction'
    elif reaction_index == 3:
        selected_reaction = 'hopping'
        
    pair_options = [item for item in reactions
                          if item[0] == selected_reaction]
    selected_pair = np.random.randint(len(pair_options))
    
    # Perform reaction
    reaction_type, (x1, y1), (x2, y2) = pair_options[selected_pair]
    
    if reaction_type == 'competition':
        # Competitive interaction
        winner_matrix = np.array([
            [1, 2, 0],  # A's outcomes against B, C
            [0, 1, 2],  # B's outcomes against C, A
            [2, 0, 1]   # C's outcomes against A, B
        ])
        
        type1, type2 = space[x1, y1], space[x2, y2]
        outcome = winner_matrix[type1-1, type2-1]
        
        if outcome == 2:
            space[x2, y2] = 0  # Loser is removed
        elif outcome == 0:
            space[x1, y1] = 0  # Focal species is removed
    
    elif reaction_type == 'reproduction':
        # Reproduce to empty site
        space[x2, y2] = space[x1, y1]
    
    elif reaction_type == 'hopping' or reaction_type == 'pair-exchange':
        # Exchange species
        space[x2, y2], space[x1, y1] = space[x1, y1], space[x2, y2]
    
    # Update time
    t = np.append(t, t[-1] + tau)
    mcs = np.append(mcs, mcs[-1] + tau/population)
    
    return space, t, mcs

if plot == 'y' or plot == 'yes':
    isExist = os.path.exists('./Frames_Gillespe')
    if isExist == False:
        os.mkdir('./Frames_Gillespe')

# @njit
def run_simulation(size=100, initial_density=0.5, total_steps=1000, sigma=1.0, mu=1.0, epsilon=5.0, D=5.0, palette = 'inferno'):
    """
    Run full lattice Gillespie simulation
    """
    # Initialize space
    space = np.zeros((size, size), dtype=np.int32)
    species = [1, 2, 3]  # A, B, C
    for x in range(size):
        for y in range(size):
            if np.random.uniform(0, 1) < initial_density:
                space[x, y] = np.random.choice(species)
    
    # Initialize time array
    t = np.array([0.0])
    mcs = np.array([0.0])
    populations = np.zeros((3,total_steps+1))
    
    # Run simulation
    frame = 0
    if plot == 'y' or plot == 'yes':
        fig, axs = plt.subplots(2, 2, figsize=(10, 10))
        ax = axs.flatten()
    
    for s in tqdm(range(total_steps+1)):
        space, t, mcs = gillespie_lattice_step(space, t, mcs, sigma, mu, epsilon, D)
        
        populations[0,s] = len(np.where(space == 1)[0])
        populations[1,s] = len(np.where(space == 2)[0])
        populations[2,s] = len(np.where(space == 3)[0])
        
        final_fracN1 = populations[0,:s+1]
        final_fracN2 = populations[1,:s+1]
        final_fracN3 = populations[2,:s+1]

        total = final_fracN1+final_fracN2+final_fracN3

        y = np.array([final_fracN1/total, final_fracN2/total, final_fracN3/total]).T
        
        if plot == 'y' or plot == 'yes':
            if s % (total_steps//args.snapshots) == 0:
                
                cmap = colors.ListedColormap([sns.color_palette(palette, 12)[0],
                                            sns.color_palette(palette, 12)[3],
                                            sns.color_palette(palette, 12)[7],
                                            sns.color_palette(palette, 12)[11]])
                bounds=[-0.5,0.5,1.5,2.5,3.5]
                norm = colors.BoundaryNorm(bounds, cmap.N)
                
                ax[1].clear()
                ax[0].clear()
                ax[2].clear()
                ax[3].clear()
                
                img = ax[0].imshow(space, cmap=cmap, norm=norm, vmin = 0, vmax = 3)
                ax[0].set_title(f'Lattice State at t = {t[-1]:.2f}')
                ax[0].axis('off')
                if frame == 0:
                    cbar = plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0, 1, 2, 3], shrink = 0.85, ax = ax[0])
                    cbar.set_ticklabels([r'$\varnothing$', 'A', 'B', 'C'])
                
                ax[1].plot(t[1:], populations[0,:s+1]/np.sum(populations[:,:s+1], axis = 0), label = 'Type A', color = sns.color_palette(palette, 12)[3], lw = 2)
                ax[1].plot(t[1:], populations[1,:s+1]/np.sum(populations[:,:s+1], axis = 0), label = 'Type B', color = sns.color_palette(palette, 12)[7], lw = 2)
                ax[1].plot(t[1:], populations[2,:s+1]/np.sum(populations[:,:s+1], axis = 0), label = 'Type C', color = sns.color_palette(palette, 12)[11], lw = 2)
                ax[1].set_ylim(0, 1)
                ax[1].legend(loc = 'upper center', ncol = 3)
                ax[1].set_title('Populations Evolution')
                ax[1].set_xlabel('Time')
                ax[1].set_ylabel('Fraction of total')
                ax[1].set_xlim(0, 30)
                ax[1].patch.set_facecolor("gray")
                
                _, tax = ternary.figure(ax = ax[3])

                tax.plot(y, color='black', lw = 1)
                tax.boundary(linewidth=1.0)
                tax.gridlines(color="grey", multiple=0.1, alpha = 0.3)

                tax.left_axis_label("C", fontsize=12, offset = 0.12)
                tax.right_axis_label("B", fontsize=12, offset = 0.12)
                tax.bottom_axis_label("A", fontsize=12, offset = 0.12)

                tax.ticks(axis='lbr', multiple=0.2, linewidth=1, tick_formats="%.1f", offset=0.02,
                        fontsize = 9)
                # tax.lim(0, 1)
                tax.get_axes().axis('off')
                
                
                ax[2].set_ylim(0, 1)
                ax[2].set_xlim(0, 1)
                ax[2].text(0.5, 0.9, r'Lattice size $L$ = ' + f'{size}',
                        ha = 'center', fontsize = 12)
                ax[2].text(0.5, 0.8, 'Reactions',
                        ha = 'center', fontsize = 12, weight = 'bold')
                ax[2].text(0.5, 0.7, r'$A + B \underset{\sigma}{\rightarrow} \varnothing + A$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.6, r'$B + C \underset{\sigma}{\rightarrow} \varnothing + B$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.5, r'$C + A \underset{\sigma}{\rightarrow} \varnothing + C$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.4, r'$X + Y \underset{\epsilon}{\rightarrow} Y + X$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.3, r'$X + \varnothing \underset{D}{\rightarrow} \varnothing + X$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.2, r'$X + \varnothing \underset{\mu}{\rightarrow} X + X$',
                        ha = 'center', fontsize = 11)
                ax[2].text(0.5, 0.01, r'$\sigma = $' + f'{sigma:.1f}, ' + r'$\epsilon = $' + f'{epsilon:.1f}, ' + r'$D = $' + f'{D}, ' + f'$\mu = $' + f'{mu:.1f}',
                        ha = 'center', fontsize = 11)
                ax[2].axis('off')
                ax[2].patch.set_facecolor('#cfcfcf')
                
                fig.patch.set_facecolor('#cfcfcf')
                
                plt.savefig(f'./Frames_Gillespe/frame_{frame}.png', dpi = 100, bbox_inches = 'tight')
                
                frame += 1
    
    return space, t, mcs, populations

# Run the simulation
final_space, times, mcs, populations = run_simulation(
    size=args.size,
    initial_density=0.5,
    total_steps=args.total_steps,
    sigma=args.sigma,
    mu=args.mu,
    epsilon=args.epsilon,
    D=args.D,
    palette='inferno'
)

final_fracN1 = populations[0]
final_fracN2 = populations[1]
final_fracN3 = populations[2]

total = final_fracN1+final_fracN2+final_fracN3

y = np.array([final_fracN1/total, final_fracN2/total, final_fracN3/total]).T

print("\nSimulation finished!")
print("\n")
print(f"Lattice file shape: {final_space.shape}")
print(f"Densities file shape: {y.shape}")

np.savetxt('Result_densities_Gillespe.txt', y)
np.savetxt('Result_lattice_Gillespe.txt', final_space)