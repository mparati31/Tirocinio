from datetime import datetime
from typing import Dict

from mip import (
    OptimizationStatus,
    Model,
    SearchEmphasis,
    BINARY,
    CONTINUOUS,
    GUROBI,
    minimize,
    xsum
)


def run_instance(data: Dict, gap=0.1, verbose=False) -> Dict:
    """Runs the energy model using the input `data` instance and returns
    a dictionary that contains all the variables and info about the solution.

    If `verbose` is True it shows the mip output while searching for the solution."""

    try:
        A, K, T = set(A), set(K), set(range(data['nT']))
        alpha, beta, gamma = data['alpha'], data['beta'], data['gamma']
        delta = data['delta']
        C, G = data['C'], data['G']
        m, l, c, d, e = data['m'], data['l'], data['c'], data['d'], data['e']
    except KeyError as ex:
        raise Exception('The input data must have the {} value'.format(ex))

    model = Model('energy_model', solver_name=GUROBI)

    if not verbose:
        model.verbose = 0
    model.threads = -1

    model.max_mip_gap = gap
    model.emphasis = SearchEmphasis.OPTIMALITY

    # Variables

    x = [[[model.add_var('x_{}_{}_{}'.format(t, i, k), var_type=BINARY)
            for k in K] for i in A] for t in T]

    y = [[[[model.add_var('y_{}_{}_{}_{}'.format(t, i, k1, k2), var_type=BINARY)
            for k2 in K] for k1 in K] for i in A] for t in T]

    g = [[model.add_var('g_{}_{}'.format(t, k), var_type=CONTINUOUS, lb=0, ub=G[k])
            for k in K] for t in T]

    v = [[model.add_var('v_{}_{}'.format(t, k), var_type=CONTINUOUS, lb=0, ub=C[k])
            for k in K] for t in T]

    z = [[model.add_var('z_{}_{}'.format(t, k), var_type=CONTINUOUS, lb=0)
            for k in K] for t in T]

    # Objective function
    model.objective = minimize(
        alpha * xsum(d[i][t] * l[j][k] * y[t][i][j][k] for t in T for i in A for j in K for k in K) +
        beta  * xsum(d[i][t] * m[i][k] * x[t][i][k]    for t in T for i in A for k in K) +
        gamma * xsum(c[k][t] * z[t][k]                 for t in T for k in K)
    )

    # Constraints

    for k, t in [(k, t) for k in K for t in T]:
        model += xsum(d[i][t] * x[t][i][k] for i in A) == v[t][k], \
            'C1_{}_{}'.format(t, k)

    for i, t in [(i, t) for i in A for t in T]:
        model += xsum(x[t][i][k] for k in K) == 1, \
            'C2_{}_{}'.format(t, i)

    for i, k, t in [(i, k, t) for i in A for k in K for t in T - {min(T)}]:
        model += x[t][i][k] == xsum(y[t][i][l][k] for l in K), '\
            C3_{}_{}_{}'.format(t, i, k)

    for i, k, t in [(i, k, t) for i in A for k in K for t in T - {max(T)}]:
        model += x[t][i][k] == xsum(y[t+1][i][k][l] for l in K), \
            'C4_{}_{}_{}'.format(t, i, k)

    for k in K:
        model += z[min(T)][k] + e[k][min(T)] + delta * G[k] >= v[min(T)][k] + g[min(T)][k], \
            'C7_{}'.format(k)

    for k, t in [(k, t) for k in K for t in T - {min(T)}]:
        model += z[t][k] + e[k][t] + g[t-1][k] >= v[t][k] + g[t][k], \
            'C8_{}_{}'.format(t, k)

    t_start = datetime.now()
    status = model.optimize()
    t_end = datetime.now()

    ret = {
        'status': status,
        'time': t_end - t_start,
        'obj_value': model.objective_value,
        'obj_bound': model.objective_bound,
        'x': x,
        'y': y,
        'g': g,
        'v': v,
        'z': z
    }

    return ret


def convert_result(result: Dict, nA: int, nK: int, nT: int, \
    json_serializable=True) -> Dict:
    """Converts the `result` into a better interpretable dictionary organized
    by time slots and facilities.

    The args nX indicates the size of the X set and `json_serializable` indicates
    if the output must be json serializable."""

    ret = dict()
    ret['status'] = result['status']
    ret['time'] = result['time'] if not json_serializable else str(result['time'])
    ret['obj_value'] = result['obj_value'] if not json_serializable \
        else str(result['obj_value'])
    ret['obj_bound'] = result['obj_bound']

    if not ret['status'] == OptimizationStatus.OPTIMAL and \
        not ret['status'] == OptimizationStatus.FEASIBLE:
        return ret

    for t in range(nT):
        ret[t] = dict()

        for k in range(nK):
            ret[t][k] = {
                'g': result['g'][t][k].x,
                'v': result['v'][t][k].x,
                'z': result['z'][t][k].x,
                'conn': []
            }

            for i in range(nA):
                if result['x'][t][i][k].x >= 0.99:
                    ret[t][k]['conn'].append(i)

    return ret
