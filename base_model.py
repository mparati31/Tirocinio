import itertools

from lib.format_text import textf
from mip import (
    OptimizationStatus,
    Model,
    SearchEmphasis,
    BINARY,
    minimize,
    xsum
)


def run_instance(data, verbose=False):
    try:
        K, A, T = set(range(data['nK'])), set(range(data['nA'])), set(range(data['nT']))
        alpha, beta = data['alpha'], data['beta']
        C = data['C']
        d, m, l = data['d'], data['m'], data['l']
    except KeyError as e:
        raise Exception('The input data must have value {}'.format(e))

    model = Model()

    model.threads = -1
    model.emphasis = SearchEmphasis.OPTIMALITY

    if not verbose:
        model.verbose = 0

    # Variables

    x = [[[model.add_var('x_{}_{}_{}'.format(t, i, k), var_type=BINARY)
            for k in K] for i in A] for t in T]

    y = [[[[model.add_var('y_{}_{}_{}_{}'.format(t, i, k1, k2), var_type=BINARY)
            for k2 in K] for k1 in K] for i in A] for t in T]

    # Objective
    model.objective = minimize(
        alpha * xsum(d[i][t] * l[j][k] * y[t][i][j][k] for t in T for i in A for j, k in itertools.product(K, K)) +
        beta  * xsum(d[i][t] * m[i][k] * x[t][i][k] for t in T for i in A for k in K)
    )

    # Constraints

    for t, k in [(t, k) for t in T for k in K]:
        model += xsum(d[i][t] * x[t][i][k] for i in A) <= C[k], 'C2_{}_{}'.format(t, k)

    for t, i in [(t, i) for t in T for i in A]:
        model += xsum(x[t][i][k] for k in K) == 1, 'C3_{}_{}'.format(t, i)

    for t, i, k in [(t, i, k) for t in T - {min(T)} for i in A for k in K]:
        model += x[t][i][k] == xsum(y[t][i][l][k] for l in K), 'C4_{}_{}_{}'.format(t, i, k)

    for t, i, k in [(t, i, k) for t in T - {max(T)} for i in A for k in K]:
        model += x[t][i][k] == xsum(y[t+1][i][k][l] for l in K), 'C5_{}_{}_{}'.format(t, i, k)

    status = model.optimize()

    result = {
        'status': status,
        'obj_value': model.objective_value,
        'x': x,
        'y': y
    }

    return result
