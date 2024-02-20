import numpy as np
from numba import njit

@njit
def G(index, v, x, R, L):
    """
    G function to compute the contribution of neighbors on the movement of the focal
    individual from paper: Buhl, Jerome, et al. 2006. Science, 312(5778), 1402-1406.

    G(u) = {
    (u + 1)/2, if u > 0
    (u - 1)/2, if u <= 0
    }
    """
    in_range = np.where((np.abs(x)%L - np.abs(x[index])%L <= R) & (x != x[index]))[0]
    if len(in_range) > 0:
        mean = np.mean(v[in_range])
        if mean > 0:
            return (mean + 1)/2
        else:
            return (mean - 1)/2
    else:
        return 0
    
@njit
def SPP(T, N, x, v, v0, R, eta, alpha, L, alpha_prob = False):
    """
    Self-Propelled Particles model
    x_i(t+1) = x_i(t) + v_0*u_i(t)
    u_i(t+1) = alpha*u_i(t) + (1-alpha)*G(mean[u(t)]_i) + eta
    """
    order = []
    for i in range(T):
        order.append(np.mean(v))
        xnew = x.copy()
        vnew = v.copy()
        for j in range(N):
            # Update position
            xnew[j] = x[j] + v0*v[j]
            
            # Update velocity
            if alpha_prob:
                rand = np.random.uniform(0, 1)
                if rand <= alpha:
                    vnew[j] = v[j] + np.random.uniform(-eta/2, eta/2)
                else:
                    vnew[j] = G(j, v, x, R, L) + np.random.uniform(-eta/2, eta/2)
            else:
                vnew[j] = alpha*v[j] + (1-alpha)*G(j, v, x, R, L) + np.random.uniform(-eta/2, eta/2)

            # Periodic boundary conditions
            if xnew[j] < 0:
                xnew[j] += L
            elif xnew[j] > L:
                xnew[j] -= L

        x = xnew
        v = vnew
        
    return np.array(order)