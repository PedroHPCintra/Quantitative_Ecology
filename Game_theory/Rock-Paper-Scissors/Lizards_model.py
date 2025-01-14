import numpy as np
from numba import njit

@njit
def stochastic_run(space, probabilities, size):
    positions = np.where(space != 0)
    # print('positions: ', len(positions[0]))
    for p in range(len(positions[0])):
        # print(p)
        focal = p
        type_focal = int(space[positions[0][focal],positions[1][focal]])
        # print('focal position: ', positions[0][focal], positions[1][focal])
        # print('focal type: ', type_focal)
        
        location = np.random.randint(-1, 2, 2)
        while location[0] == 0 and location[1] == 0:
            location = np.random.randint(-1, 2, 2)
            
        neighbor_position = np.array([(positions[0][focal] + location[0])%size, (positions[1][focal] + location[1])%size])
        type_competitor = int(space[neighbor_position[0],neighbor_position[1]])
        # print('competitor position: ', neighbor_position)
        # print('competitor type: ', type_competitor)

        if type_competitor != 0:
            result_focal = probabilities[type_focal, type_competitor]
            result_competitor = probabilities[type_competitor, type_focal]
            # print('focal payoff: ', result_focal)
            # print('competitor payoff: ', result_competitor)
            rand = np.random.uniform(0, 1)
            if probabilities[type_focal, type_competitor] > 0:
                if rand > probabilities[type_focal, type_competitor]:
                    # print('filling space with: ', type_focal)
                    space[neighbor_position[0],neighbor_position[1]] = type_focal
                
            if probabilities[type_competitor, type_focal] > 0:
                rand = np.random.uniform(0, 1)
                if rand > probabilities[type_competitor, type_focal]:
                    # print('filling space with: ', type_competitor)
                    space[positions[0][focal],positions[1][focal]] = type_competitor
        else:
            # print('empty site!')
            rand = np.random.uniform(0, 1)
            if rand > probabilities[type_focal, type_competitor]:
                # print('filling space with: ', type_focal)
                space[neighbor_position[0],neighbor_position[1]] = type_focal

        # print('----------------------------')

    return space

def exec_sim(r = 0.6, p1 = 0.6, p2 = 0.8, p3 = 0.5, mu = 0.01, S = 30, years = 10, x0 = 10, proportion = (1/3,1/3,1/3)):
    mutation = mu

    probabilities = np.array([
        [r, r, r, r],
        [r, 1, p1, 0],
        [r, 0, 1, p2],
        [r, p3, 0, 1]])
    size = 30

    space = np.zeros((size, size))

    init = x0

    if proportion == (1/3,1/3,1/3):
        N = np.concatenate((
            [1 for _ in range(init)],
            [2 for _ in range(init)],
            [3 for _ in range(init)]
        ))
    else:
        N = np.concatenate((
            [1 for _ in range(int(init*proportion[0]))],
            [2 for _ in range(int(init*proportion[1]))],
            [3 for _ in range(int(init*proportion[2]))]
        ))

    N1 = [init]
    N2 = [init]
    N3 = [init]

    for n in range(len(N)):
        ij = np.random.randint(0, size, 2)
        while space[ij[0], ij[1]] != 0:
            ij = np.random.randint(0, size, 2)
        
        space[ij[0], ij[1]] = N[n]


    final_fracN1 = []
    final_fracN2 = []
    final_fracN3 = []

    for y in range(years):
        # print(f"Year: {y}")
        if y%2 == 0:
            N_females = 110
        else:
            N_females = 80
            
        total_eggs = 6*N_females
        if y == 0:
            init = 10
            N = np.concatenate((
                [1 for _ in range(init)],
                [2 for _ in range(init)],
                [3 for _ in range(init)]
            ))
            N1 = [init]
            N2 = [init]
            N3 = [init]
        
        else:
            init = 20
            N = np.concatenate((
                [1 for _ in range(int(np.round(total_eggs*final_fracN1[-1])))],
                [2 for _ in range(int(np.round(total_eggs*final_fracN2[-1])))],
                [3 for _ in range(int(np.round(total_eggs*final_fracN3[-1])))]
            ))
            N1 = [int(np.round(total_eggs*final_fracN1[-1]))]
            N2 = [int(np.round(total_eggs*final_fracN2[-1]))]
            N3 = [int(np.round(total_eggs*final_fracN3[-1]))]
        
        # print(len(N))
        
        space = np.zeros((size, size))
        
        for n in range(len(N)):
            ij = np.random.randint(0, size, 2)
            while space[ij[0], ij[1]] != 0:
                ij = np.random.randint(0, size, 2)

            r = np.random.uniform(0, 1)
            # Check if mutation occurs
            if r < mutation:
                new_type = np.random.randint(1, 4)
                while new_type == N[n]:
                    new_type = np.random.randint(1, 4)
                    
                space[ij[0], ij[1]] = new_type
            else:
                space[ij[0], ij[1]] = N[n]
            
        for t in range(1,13):
            space = stochastic_run(space, probabilities, S)
            if t%12 == 0:
                N1.append(len(np.where(space == 1)[0]))
                N2.append(len(np.where(space == 2)[0]))
                N3.append(len(np.where(space == 3)[0]))

            if len(np.where(space == 1)[0]) == size**2 or len(np.where(space == 2)[0]) == size**2 or len(np.where(space == 3)[0]) == size**2:
                break
                
        N1 = np.array(N1)
        N2 = np.array(N2)
        N3 = np.array(N3)

        total = N1+N2+N3

        y = np.array([N1/total, N2/total, N3/total]).T
        
        final_fracN1.append(y[-1,0])
        final_fracN2.append(y[-1,1])
        final_fracN3.append(y[-1,2])

    final_fracN1 = np.array(final_fracN1)
    final_fracN2 = np.array(final_fracN2)
    final_fracN3 = np.array(final_fracN3)

    total = final_fracN1+final_fracN2+final_fracN3

    y = np.array([final_fracN1/total, final_fracN2/total, final_fracN3/total]).T

    return space, y