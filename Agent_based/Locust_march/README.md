# Replication of the SPP model

**Reference**

Buhl, J., Sumpter, D. J., Couzin, I. D., Hale, J. J., Despland, E., Miller, E. R., & Simpson, S. J. (2006). From disorder to order in marching locusts. _Science, 312(5778)_, 1402-1406. DOI: [10.1126/science.1125142](https://doi.org/10.1126/science.1125142)

**Model**

A Self-Propelled Particle (SPP) model for the collective behavior in marching locusts of the species _Schistocerca gregaria_.

Each locust has its position $i$ altered between the time step $t$ and $t+ \Delta t$ according to the function

$$
\begin{align}
    x_i(t + \Delta t) = x_i(t) + v_0 u_i(t)
\end{align}
$$

where $u_i$ is a dimensionless velocity that scales according to the presence of neighbors around the focal locust

$$
\begin{align}
    u(t + \Delta t) = \alpha u_i(t) + (1 - \alpha)G\left( \left\langle u \right\rangle_i \right) + \eta_i
\end{align}
$$

and

$$
\begin{align}
    G(u) =
    \begin{cases}
        \frac{u+1}{2}, \, \text{ if } u > 0 \\
        \frac{u-1}{2}, \, \text{ if } u < 0
    \end{cases}
\end{align}
$$

Here $\alpha$ is a constant that states how much one individual prefers to follow it's own path, instead of following the group. If $\alpha = 1$, the individual velocity is independent of the group behavior. $\eta_i$ is a random variable to induce noise and stochasticity on the locust movement.