import numpy as np

# Parameters
r_list = [1, 5, 1, 4, 4, 2]
N = len(r_list)
lam = 0.9

# This is the f(x, a) function that finds the next state
def next_x(xk, a, N):
    return (xk + a)%N

# This is the recursive action-value function, that goes on to find the next
# value too
def Qfunc(xk, rewards, L, k, N, thres):
    """
    xk is the current state, rewards it he r_list, L is the lambda, 
    k is the current state number, which allows safe recursion,
    N is a parameter
    """

    # This stops infinite recursion
    #if L**k < 0.1:
    #    return 0

    if k >= thres:
        return 0

    rk = rewards[xk]

    options = [L * Qfunc(next_x(xk, i, N), rewards, L, k + 1, N, thres) for i in (1, -1)]
    chosen = max(options)
    

    reward = rk + chosen

    print(chosen)

    return reward

Qfunc(0, r_list, lam, 0, N, )