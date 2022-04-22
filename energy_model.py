from lib.format_text import textf

from mip import (
    OptimizationStatus,
    Model,
    BINARY,
    CONTINUOUS,
    minimize,
    xsum
)


def run_instance(data, verbose=False):
    """Runs the energy model using the input data instance and returns
    a dictionary that contains all the variables and info about the solution.

    If verbose is True it shows the mip output while searching for the solution."""

    try:
        A, K, T = set(range(data['nA'])), set(range(data['nK'])), set(range(data['nT']))
        alpha, beta, gamma = data['alpha'], data['beta'], data['gamma']
        delta = data['delta']
        C, G = data['C'], data['G']
        m, l, c, d, e = data['m'], data['l'], data['c'], data['d'], data['e']
    except KeyError as ex:
        raise Exception('The input data must have the {} value'.format(ex))

    model = Model('energy_model')

    if not verbose:
        model.verbose = 0

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
        model += xsum(d[i][t] * x[t][i][k] for i in A) == v[t][k], 'C1_{}_{}'.format(t, k)

    for i, t in [(i, t) for i in A for t in T]:
        model += xsum(x[t][i][k] for k in K) == 1, 'C2_{}_{}'.format(t, i)

    for i, k, t in [(i, k, t) for i in A for k in K for t in T - {min(T)}]:
        model += x[t][i][k] == xsum(y[t][i][l][k] for l in K), 'C3_{}_{}_{}'.format(t, i, k)

    for i, k, t in [(i, k, t) for i in A for k in K for t in T - {max(T)}]:
        model += x[t][i][k] == xsum(y[t+1][i][k][l] for l in K), 'C4_{}_{}_{}'.format(t, i, k)

    for k in K:
        model += z[min(T)][k] + e[k][min(T)] + delta * G[k] >= v[min(T)][k] + g[min(T)][k], 'C7_{}'.format(k)

    for k, t in [(k, t) for k in K for t in T - {min(T)}]:
        model += z[t][k] + e[k][t] + g[t-1][k] >= v[t][k] + g[t][k], 'C8_{}_{}'.format(t, k)

    status = model.optimize()

    ret = {
        'status': status,
        'obj_value': model.objective_value,
        'x': x,
        'y': y,
        'g': g,
        'v': v,
        'z': z
    }

    return ret


def convert_result(result, nA, nK, nT):
    """Converts the result into a better interpretable dictionary organized
    by time slots and MEC facilities.

    The args nX indicates the size of the X set."""

    ret = dict()
    ret['status'] = result['status']
    ret['obj_value'] = result['obj_value']

    if not ret['status'] == OptimizationStatus.OPTIMAL and not ret['status'] == OptimizationStatus.FEASIBLE:
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


def show_result(result, data):
    """Return a string that represent the human-readable result.

    The input args are the result and data of same problem instance."""

    A = ['A{}'.format(x) for x in range(data['nA'])]
    K = ['K{}'.format(x) for x in range(data['nK'])]
    T = [x + 1 for x in range(data['nT'])]

    status = result['status']
    status_text = str(result['status'])[len('OptimizationStatus.'):]

    text = 'Status: {}\n'.format(status_text)

    if not status == OptimizationStatus.OPTIMAL and not status == OptimizationStatus.FEASIBLE:
        return text

    objective_value = round(result['obj_value'], 2)

    delta = data['delta']
    G0= data['G'][0]

    text += 'Objective Value: {}\n'.format(objective_value)
    text += '\nInitial Batteries Charge: {} ({}%)\n\n'.format(delta * G0, delta * 100)

    total_cost = 0

    for t in range(data['nT']):
        text += textf.style('TIME {}\n\n'.format(T[t]), textf.UNDERLINE)

        for k in range(data['nK']):
            C, G = data['C'][k], data['G'][k]
            c, e = data['c'][k][t], data['e'][k][t]
            g, v, z = round(result[t][k]['g'], 2), round(result[t][k]['v'], 2), round(result[t][k]['z'], 2)

            cost = round(c * z, 2)
            total_cost += cost

            text += '  ' + textf.style('FACILITY {}:\n'.format(K[k]), textf.BOLD)
            text += '    Energy Used:          {}\n'.format(v)
            text += '    Facility Capacity:    {}\n'.format(C)
            text += '    Energy Produced:      {}\n'.format(e)
            text += '    Purchased Energy (€): {} ({})\n'.format(z, cost)
            text += '    Battery Charge:       {} / {}\n'.format(g, G)
            text += '    AP connected (Energy Used):\n'

            ap_connected = result[t][k]['conn']
            for a in ap_connected:
                d = data['d'][a][t]
                new_conn = t > 0 and not a in result[t-1][k]['conn']
                text += '\t{} ({}) {}\n'.format(A[a], d, '+' if new_conn else '')

            text += '\n'

    text += 'Total Energy Cost: {}\n'.format(round(total_cost, 2))

    return text
