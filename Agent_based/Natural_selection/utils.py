import numpy as np
from numba import njit
import math

@njit
def sample_truncnorm(loc, scale, bounds):
    """
    Normal distribution truncated at two ends to avoid sampling values outside a given range

    Ex: loc = 2, scale = 3, bounds = [0,5] will yield a normal distribution with mean 2,
    standard deviation 3, confined to the interval [0,5]
    """
    while True:
        s = np.random.normal(loc, scale)
        if bounds[0] <= s <= bounds[1]:
            break
    return s


@njit
def delete_workaround(arr, num):
    mask = np.zeros(arr.shape[0], dtype=np.int64) == 0
    mask[np.where(arr == num)[0]] = False
    return arr[mask]


@njit
def food_growth(food, dt, r, K, L, dispersal):
    """
    Dispersal range distribution is modelled as a truncated normal
    to resemble the shape of seed dispersal range distributions observed
    in real life
    
    Gelmi-Candusso A. T., et al. (2019). Ecology and Evolution.
    https://doi.org/10.1002/ece3.5422
    
    Trees compete to resources on the ground which limits the growth
    of trees on a given region. Suggested model to add later
    
    Berger U. & Hildenbrandt H. (2000). Ecological Modelling.
    https://doi.org/10.1016/S0304-3800(00)00298-2
    """
    N = len(food)
    
    if K > N > 0:
        for i in range(N):
            rand = np.random.uniform(0, 1)
            if rand <= r - N*r/K: # reproduction probability decreases as N increases, until it reaches zero at N = K
                R = sample_truncnorm(L/10, dispersal, [0, L])
                angle = np.random.uniform(0, 2*np.pi)
                x = R*np.sin(angle)
                y = R*np.cos(angle)
                newX = food[i,0] + x
                newY = food[i,1] + y
                while 0 > newX or newX > L or newY < 0 or newY > L:
                    R = sample_truncnorm(L/10, dispersal, [0, L])
                    angle = np.random.uniform(0, 2*np.pi)
                    x = R*np.sin(angle)
                    y = R*np.cos(angle)
                    newX = food[i,0] + x
                    newY = food[i,1] + y

                food_new = np.array([[newX, newY]])
                food = np.concatenate((food, food_new), axis = 0)
    elif N == 0:
        food = np.zeros((2,2))
        for i in range(2):
            x = np.random.uniform(0, L)
            y = np.random.uniform(0, L)
            food[i] = np.array([x,y])
        
    return food


@njit
def reproduction(x, v, size, angle, energy, sight_radius, reproduction_threshold, reproduction_cost, life):
    for i in range(len(x)):
        if energy[i] >= reproduction_threshold:
            # print("Depois de 9 meses você vê o resultado")
            new_x = x[i]
            new_life = np.array([1])
            # print(new_x)
            new_v = v[i]
            # new_v = np.random.normal(v[i], 0.2)
            # while new_v < 0.1:
            #     new_v = np.random.normal(v[i], 0.2)
                
            new_angle = np.array([np.random.uniform(0, 2*np.pi)])
            
            # new_sight_radius = sight_radius[i]
            new_sight_radius = np.random.normal(sight_radius[i], 0.3)
            while new_sight_radius < 0.5:
                new_sight_radius = np.random.normal(sight_radius[i], 0.3)
            
            new_size = np.array([size[i]])
            
            energy[i] -= reproduction_cost
            
            new_x = new_x.reshape(1,2)
            # new_size = new_size.reshape(1)
            new_sight_radius = np.array([new_sight_radius])
            # new_sight_radius = new_sight_radius.reshape(1)
            x = np.concatenate((x, new_x), axis = 0)
            new_v = np.array([new_v])
            # new_v = new_v.reshape(1)
            v = np.concatenate((v, new_v))
            
            size = np.concatenate((size, new_size))
            # print(sight_radius.shape, new_sight_radius.shape)
            angle = np.concatenate((angle, new_angle))
            sight_radius = np.concatenate((sight_radius, new_sight_radius))
            energy = np.concatenate((energy, np.array([min(energy[i], reproduction_cost)])))
            life = np.concatenate((life, new_life))
            
    return x, v, size, angle, energy, sight_radius, life


@njit
def delete_rows(arr, indices):
    mask = np.ones(arr.shape[0], dtype=np.bool_)
    for index in indices:
        mask[index] = False
    
    new_size = np.sum(mask)
    new_arr = np.empty((new_size, arr.shape[1]), dtype=arr.dtype)
    new_index = 0
    
    for i in range(arr.shape[0]):
        if mask[i]:
            new_arr[new_index] = arr[i]
            new_index += 1
    
    return new_arr


@njit
def update_position(x, v, dt, size, L, angle, rand, energy, food, food_energy, sight_radius, max_energy, life, metabolic_rate):
    """
    Individuals move completely following a random walk until food comes inside their
    perception area (defined by the sight_radius). Once food is in sight, individuals
    move directly on a straight line to the nearest food source that has been sighted.

    At each time step, upon movement, an individual loses energy due to its metabolism
    and the square of it's sight radius. Thus

    Energy_cost = metabolism + A*r²

    where r is the sight_radius and A is a proportionality constant
    """
    # print("Len: ", len(x))
    for i in range(len(x)):
        # print(i)
        if energy[i] <= 0:
            x[i] = x[i]
            # print(i)
            life[i] = 0
        else:
            distance = np.sqrt((food[:,0] - x[i][0])**2 + (food[:,1] - x[i][1])**2)
            food_eaten = np.where(distance <= size[i])[0]
            food_in_sight = np.where(distance <= sight_radius[i])[0]
            energy[i] += len(food_eaten)*food_energy
            energy[i] = min(max_energy, energy[i])
            food = delete_rows(food, food_eaten)

            distance_to_food = []
            if len(food_in_sight) > 0 and len(food_eaten) == 0:
                for j in food_in_sight:
                    distance = np.sqrt((food[j,0] - x[i][0])**2 + (food[j,1] - x[i][1])**2)
                    distance_to_food.append(distance)

                closest_food = np.argmin(np.array(distance_to_food))
                angle[i] = np.arctan2(
                            food[food_in_sight[closest_food],1] - x[i,1],
                            food[food_in_sight[closest_food],0] - x[i,0]
                            )
            else:

                angle[i] += np.random.uniform(-rand, rand)

            if x[i,0] <= 0 and angle[i] != 0:
                dx = 0
                dy = 1
                nx = - dy
                ny = dx
                px = v[i]*np.cos(angle[i])
                py = v[i]*np.sin(angle[i])
                dott = px * nx + py * ny
                rx = px - 2 * dott * nx
                ry = py - 2 * dott * ny
                theta_reflected = math.atan2(ry, rx)
                angle[i] = theta_reflected
                x[i,0] = 0

            elif x[i,0] >= L:
                dx = 0
                dy = 1
                nx = - dy
                ny = dx
                px = v[i]*np.cos(angle[i])
                py = v[i]*np.sin(angle[i])
                dott = px * nx + py * ny
                rx = px - 2 * dott * nx
                ry = py - 2 * dott * ny
                theta_reflected = math.atan2(ry, rx)
                angle[i] = theta_reflected
                x[i,0] = L

            elif x[i,1] <= 0:
                dx = 1
                dy = 0
                nx = - dy
                ny = dx
                px = v[i]*np.cos(angle[i])
                py = v[i]*np.sin(angle[i])
                dott = px * nx + py * ny
                rx = px - 2 * dott * nx
                ry = py - 2 * dott * ny
                theta_reflected = math.atan2(ry, rx)
                angle[i] = theta_reflected
                x[i,1] = 0

            elif x[i,1] >= L:
                dx = 1
                dy = 0
                nx = - dy
                ny = dx
                px = v[i]*np.cos(angle[i])
                py = v[i]*np.sin(angle[i])
                dott = px * nx + py * ny
                rx = px - 2 * dott * nx
                ry = py - 2 * dott * ny
                theta_reflected = math.atan2(ry, rx)
                angle[i] = theta_reflected
                x[i,1] = L

            energy[i] -= metabolic_rate
            energy[i] -= 0.1*sight_radius[i]**2
            
            # print(x)
            # print(angle)

            x[i,0] = x[i,0] + v[i]*np.cos(angle[i])*dt
            x[i,1] = x[i,1] + v[i]*np.sin(angle[i])*dt
    
    return x, angle, energy, food, life