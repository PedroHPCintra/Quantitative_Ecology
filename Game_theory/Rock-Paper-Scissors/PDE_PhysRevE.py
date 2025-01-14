import warnings
warnings.filterwarnings("ignore")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import ternary
import math
from tqdm import tqdm
import sys
import os
import argparse

parser = argparse.ArgumentParser("PDE solution")
parser.add_argument("plot", help="If 'yes' snapshots of the simulation will be saved according to the number of snapshots (default=400). Otherwise no plot will be generated.", type=str)
parser.add_argument("final_time", help="Final time for the simulation to stop.", type=float)
parser.add_argument("dt", help="Time step size for each simulation step. The total number of steps in the simulation will equal final_time/dt.", type=float)
parser.add_argument("beta", help="Reproduction rate.", type=float)
parser.add_argument("sigma", help="Dominance-removal rate.", type=float)
parser.add_argument("zeta", help="Dominance-replacement rate.", type=float)
parser.add_argument("mu", help="Mutation rate.", type=float)
parser.add_argument("delta_D", help="Hopping rate. Hopping is the movement an individual has when it moves from it's local site to a neighboring empty one.", type=float)
parser.add_argument("delta_E", help="Pair-exchange rate. Pair-exchange is the movement an in individual has when it switches it's local site with it's neighbor's. Compared to hopping, this is understood as movement through crowded areas where the movement of one must displace the other.", type=float)
parser.add_argument("snapshots", help="(Optional argument) Number of snapshots to save during the simulation.", type=int,
                    nargs='?', default=400)
args = parser.parse_args()

""""
    Reference:
        - Szczesny, B., Mobilia, M. & Rucklidge, A. M. (2014). Characterization of spiraling patterns in spatial rock-paper-scissors games. Physical Review E. 90, 032704.
"""

plot = args.plot

if plot == 'y' or plot == 'yes':
    try:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
    except Exception as e:
        print("LaTeX not found or not uploaded, using Matplotlib default font.")
        print(f"Error type: {type(e)}\nError message: {e}")

def color_point(x, y, z, scale):
    w = 255
    x_color = x * w / float(scale)
    y_color = y * w / float(scale)
    z_color = z * w / float(scale)
    r = math.fabs(w - y_color) / w
    g = math.fabs(w - x_color) / w
    b = math.fabs(w - z_color) / w
    return (r, g, b, 1.)


def generate_heatmap_data(scale=5):
    from ternary.helpers import simplex_iterator
    d = dict()
    for (i, j, k) in simplex_iterator(scale):
        d[(i, j, k)] = color_point(i, j, k, scale)
    return d

# Helper functions for Laplacian with periodic boundaries
def laplacian(Z):
    return (
        np.roll(Z, 1, axis=0) + np.roll(Z, -1, axis=0) +
        np.roll(Z, 1, axis=1) + np.roll(Z, -1, axis=1) -
        4 * Z
    ) / dx**2

# Parameters
beta, sigma, zeta, mu = args.beta, args.sigma, args.zeta, args.mu
deltaD, deltaE = args.delta_D, args.delta_E
L = 128  # Grid size (LxL)
dx = 1.0  # Spatial step
dt = args.dt  # Time step
T_final = args.final_time # total time
T = int(T_final/dt)  # Total time steps

# Grid and initial conditions
x = np.arange(0, L)
y = np.arange(0, L)
X, Y = np.meshgrid(x, y)

# Initialize densities (small random perturbations around coexistence fixed point)
s1 = beta / (3 * beta + sigma) + 0.01 * np.random.rand(L, L)
s2 = beta / (3 * beta + sigma) + 0.01 * np.random.rand(L, L)
s3 = beta / (3 * beta + sigma) + 0.01 * np.random.rand(L, L)

colors = [(0, 1, 1), (1, 0, 1), (1, 1, 0)]  # Cyan, Magenta, Yellow
ternary_cmap = LinearSegmentedColormap.from_list("TernaryMap", colors, N=256)

# Initialize plot
fig, axs = plt.subplots(2,2, figsize=(10, 10))
ax = axs.flatten()
cbar = None  # Placeholder for the colorbar
ims = []  # Store images for animation

scale = 100
data = generate_heatmap_data(scale)

frame = 0
# Time evolution
total_density_s1 = []
total_density_s2 = []
total_density_s3 = []

if plot == 'y' or plot == 'yes':
    isExist = os.path.exists('./Frames_PDE')
    if isExist == False:
        os.mkdir('./Frames_PDE')


for t in tqdm(range(T)):
    # Total density
    r = s1 + s2 + s3

    # Compute Laplacians
    lap_s1 = laplacian(s1)
    lap_s2 = laplacian(s2)
    lap_s3 = laplacian(s3)
    lap_r = laplacian(r)

    # Update equations
    ds1_dt = (
        s1 * (beta * (1 - r) - sigma * s3) +
        zeta * s1 * (s2 - s3) +
        mu * (s3 + s2 - 2 * s1) +
        (deltaE - deltaD) * (r * lap_s1 - s1 * lap_r) +
        deltaD * lap_s1
    )
    ds2_dt = (
        s2 * (beta * (1 - r) - sigma * s1) +
        zeta * s2 * (s3 - s1) +
        mu * (s1 + s3 - 2 * s2) +
        (deltaE - deltaD) * (r * lap_s2 - s2 * lap_r) +
        deltaD * lap_s2
    )
    ds3_dt = (
        s3 * (beta * (1 - r) - sigma * s2) +
        zeta * s3 * (s1 - s2) +
        mu * (s2 + s1 - 2 * s3) +
        (deltaE - deltaD) * (r * lap_s3 - s3 * lap_r) +
        deltaD * lap_s3
    )

    # Euler update
    s1 += dt * ds1_dt
    s2 += dt * ds2_dt
    s3 += dt * ds3_dt

    # Ensure densities remain non-negative
    s1 = np.clip(s1, 0, 1)
    s2 = np.clip(s2, 0, 1)
    s3 = np.clip(s3, 0, 1)
    
    total_density_s1.append(np.sum(s1)/np.sum(r))
    total_density_s2.append(np.sum(s2)/np.sum(r))
    total_density_s3.append(np.sum(s3)/np.sum(r))

    # Visualization
    if plot == 'y' or plot == 'yes':
        if t % (T/args.snapshots) == 0:
            ax[0].clear()
            ax[3].clear()
            
            total = s1 + s2 + s3
            norm_s1 = s1 / total
            norm_s2 = s2 / total
            norm_s3 = s3 / total

            # Create RGB image
            ternary_image = np.stack((norm_s1, norm_s2, norm_s3), axis=-1)
            ternary_image = ternary_image @ np.array(colors)

            # Plot
            ax[0].imshow(ternary_image, interpolation='nearest')
            ax[0].set_title(f"Species Densities at t={t * dt:.1f}", fontsize = 14)
            ax[0].axis('off')
            
            ax[3].plot([i*dt for i in range(t+1)], total_density_s1, color = 'cyan', lw = 2, label = 'Type 1')
            ax[3].plot([i*dt for i in range(t+1)], total_density_s2, color = 'magenta', lw = 2, label = 'Type 2')
            ax[3].plot([i*dt for i in range(t+1)], total_density_s3, color = 'yellow', lw = 2, label = 'Type 3')
            ax[3].set_ylim(0, 1)
            ax[3].set_xlim(0, T_final)
            ax[3].set_title("Total densities", fontsize = 14)
            ax[3].set_xlabel("Time", fontsize = 12)
            ax[3].set_ylabel("Fraction of total", fontsize = 12)
            ax[3].legend(loc = 'upper center', ncol = 3)
            ax[3].patch.set_facecolor("gray")
            
            if frame == 0:
                figure, tax = ternary.figure(scale=scale, ax = ax[1])
                tax.heatmap(data, style="hexagonal", use_rgba=True, colorbar = False)
                tax.ticks(axis='lbr', multiple=20, linewidth=1, tick_formats="%.0f", offset=0.02,
                        fontsize = 9)
                tax.left_axis_label("Type 3 [\%]", fontsize=12, offset = 0.12)
                tax.right_axis_label("Type 1 [\%]", fontsize=12, offset = 0.12)
                tax.bottom_axis_label("Type 2 [\%]", fontsize=12, offset = 0.12)
                tax.boundary()
                tax.get_axes().axis('off')
                
                ax[2].set_ylim(0, 1)
                ax[2].set_xlim(0, 1)
                ax[2].axis('off')
                ax[2].text(0.05, 0.95, r'$\displaystyle \partial_t s_i = s_i [ \underbrace{\beta \left( 1 - r \right)}_{\mathrm{reproduction}} - \underbrace{\sigma s_{i-1}}_{\mathrm{dominance-removal}} ]$',
                        ha = 'left', fontsize = 14)
                ax[2].text(0.05, 0.8, r'$+ \underbrace{\xi s_i \left( s_{i+1} − s_{i−1} \right)}_{\mathrm{dominance-replacement}}$', ha = 'left', fontsize = 14)
                ax[2].text(0.05, 0.65, r'$+ \underbrace{\mu \left( s_{i−1} + s_{i+1} − 2 s_i \right)}_{\mathrm{mutation}}$',
                        ha = 'left', fontsize = 14)
                ax[2].text(0.05, 0.5, r'$+ \underbrace{\left(\delta_E − \delta_D \right) \left[r \nabla^2 s_i − s_i \nabla^2 r \right]}_{\mathrm{non-linear-mobility}}$',
                        ha = 'left', fontsize = 14)
                ax[2].text(0.05, 0.35, r'$+ \underbrace{\delta_D \nabla^2 s_i}_{\mathrm{diffusion}}$',
                        ha = 'left', fontsize = 12)
                ax[2].text(0.05, 0.2, r'$r = s_1 + s_2 + s_3$',
                        ha = 'left', fontsize = 12)
                
                ax[2].patch.set_facecolor('#cfcfcf')

            fig.patch.set_facecolor('#cfcfcf')

            plt.savefig(f'./Frames_PDE/PDE_frame_{frame}.png', dpi = 90, bbox_inches = 'tight')
            frame += 1

final_lattice = np.array([s1,s2,s3])
result_densities = np.array([total_density_s1,total_density_s2,total_density_s3])

print("\nSimulation finished!")
print("\n")
print(f"Lattice file shape: {final_lattice.shape}")
print(f"Densities file shape: {result_densities.shape}")

np.savetxt('Result_densities_PDE.txt', result_densities)
np.savetxt('Result_lattice_1_PDE.txt', final_lattice[0])
np.savetxt('Result_lattice_2_PDE.txt', final_lattice[1])
np.savetxt('Result_lattice_3_PDE.txt', final_lattice[2])