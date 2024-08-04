import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
import psutil

import utils as ut
import plots

def run_model(Ni, N0, L, v, food_energy, angle, size, K, r, dt, sight_radius, alpha, max_energy, dispersal, nsteps, plot_frequency, mutatables: list, print_memory = False):

    pos = np.array([0, 10])
    vel = np.array([v*np.cos(angle), v*np.sin(angle)])

    food = np.random.uniform(0, L, (N0,2))

    positions = {}
    positions[0] = np.ones((Ni, 2))*pos

    angles = {}
    angles[0] = np.ones(Ni)*angle

    velocities = {}
    velocities[0] = np.ones(Ni)*v

    energy = {}
    energy[0] = np.ones(Ni)*max_energy/2

    food_pos = {}
    food_pos[0] = food

    size_vec = {}
    size_vec[0] = np.ones(Ni)*size
    sight_vec = {}
    sight_vec[0] = np.ones(Ni)*sight_radius

    life = {}
    life[0] = np.ones(Ni)
    
    steps = {}
    steps[0] = np.round(np.random.pareto(a = alpha, size = Ni), 0)
    
    alphas = {}
    alphas[0] = np.ones(Ni)*alpha

    for i in range(1, nsteps):
        t = dt*i
        # print("---------------------------------")
        # print(f"i = {i}")
        ram_usage = psutil.virtual_memory()[3]/1000000000
        if print_memory:
            if 13.4 >= ram_usage > 11.5:
                print(f"Frame: {i} - Memory RAM usage: {ram_usage:.2f}", end = '\r')
        if ram_usage > 13.5:
            print("Breaking simulation due to memory usage")
            break
        food_pos[i] = ut.food_growth(
            food_pos[i-1],
            dt,
            r,
            K,
            L,
            dispersal)
        # pos = positions[i-1]
        # print("Before reproduction")
        # print("i-1: ", positions[i-1])
        food_population = []

        for j in range(i):
            food_population.append(len(food_pos[j]))

        population = []

        for j in range(i):
            population.append(len(np.where(life[j] == 1)[0]))
            
        mean_sight_vec = []

        for j in range(i):
            mean_sight_vec.append(np.mean(sight_vec[j]))
            
        mean_vel_vec = []

        for j in range(i):
            mean_vel_vec.append(np.mean(velocities[j]))
            
        mean_alphas_vec = []
        
        for j in range(i):
            mean_alphas_vec.append(np.mean(alphas[j]))
        
        positions[i], velocities[i], alphas[i], size_vec[i], angles[i], energy[i], sight_vec[i], life[i], steps[i] = ut.reproduction(
            x = positions[i-1],
            v = velocities[i-1],
            alpha = alphas[i-1],
            size = size_vec[i-1],
            angle = angles[i-1],
            energy = energy[i-1],
            sight_radius = sight_vec[i-1],
            reproduction_threshold = 0.8*max_energy,
            reproduction_cost = 0.4*max_energy,
            life = life[i-1],
            steps = steps[i-1],
            mutatables = mutatables
        )
        # print("After reproduction and before position update")
        # print("i: ", positions[i])
        # print("i-1: ", positions[i-1])
        positions[i], angles[i], energy[i], food_pos[i], life[i], steps[i] = ut.update_position(
            x = positions[i],
            v = velocities[i],
            alpha = alphas[i],
            dt = dt,
            size = size_vec[i],
            L = L,
            angle = angles[i],
            rand = np.pi/6,
            energy = energy[i],
            food = food_pos[i],
            food_energy = food_energy,
            sight_radius = sight_vec[i],
            max_energy = max_energy,
            life = life[i],
            metabolic_rate = 3,
            steps = steps[i]
        )
        # print("After position update")
        # print("i: ", positions[i])
        # print("i-1: ", positions[i-1])
        if len(np.where(life[i] == 1)[0]) == 0:
            print("Everybody died")
            break
        
        if i % plot_frequency == 0:
            # print(f"{i}/{nsteps} - {100*i/nsteps:.1f}%", end = '\r')
            print(f"Plotting... {i}/{nsteps}", end = '\r')
            fig, axs = plt.subplots(3, 2, figsize=(8,12), gridspec_kw={'width_ratios': [1, 1]})
            ax = axs.flatten()
            plots.plot(
                fig,
                ax,
                i-1,
                L,
                positions,
                velocities,
                food_pos,
                life,
                food_population,
                population,
                nsteps,
                sight_vec,
                mean_sight_vec,
                mean_vel_vec,
                plot_frequency,
                save = True,
                show = False
            )
    
    return positions, velocities, energy, life, size_vec, sight_vec, food_pos, alphas