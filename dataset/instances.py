from dataset import facilities_positions, irradiation
from dataset.data import *
from typing import Dict, Tuple


def load_data(filename: str) -> Dict:
    """Returns a dictionary that contains the instance loaded from the
    indicated file."""

    def format(data_):
        return [[float(x) for x in el.split(',')] for el in data_]

    lines = open(filename, 'r').readlines()

    ret = dict()

    ret['nA'], ret['nK'], ret['nT'] = [int(x) for x in lines[0:3]]
    ret['alpha'], ret['beta'] = [float(x) for x in lines[3:5]]
    ret['C'] = [int(lines[6]) for _ in range(ret['nK'])]

    lines = lines[7:]
    ret['d'] = format(lines[:ret['nA']])

    lines = lines[ret['nA']:]
    ret['l'] = format(lines[:ret['nK']])

    lines = lines[ret['nK']:]
    ret['m'] = format(lines[:ret['nA']])

    lines = lines[ret['nA']:]
    if len(lines) != 0: raise Exception('Dataset format error')

    return ret


def load_energy_data_1(filename: str, delta=1) -> Dict:
    """Returns a dictionary that contains the instance loaded from the
    indicated file to which energy data 1 has been added.

    The `delta` parameter is a value between 0 and 1 and indicates the
    initial charge percentage of the batteries."""

    instance = load_data(filename)
    T = range(instance['nT'])

    instance['alpha'] = instance['beta'] = instance['gamma'] = 1/3
    instance['delta'] = delta
    instance['G'] = [instance['C'][k] / 2 for k in K]
    instance['c'] = [[1 for _ in T] for _ in K]
    instance['e'] = [[instance['C'][k] / 2 for _ in T] for k in K]

    return instance


def load_energy_data_2(filename: str, delta=1) -> Dict:
    """Returns a dictionary that contains the instance loaded from the
    indicated file to which energy data 1 has been added.

    The `delta` parameter is a value between 0 and 1 and indicates the
    initial charge percentage of the batteries."""

    instance = load_data(filename)
    T = range(instance['nT'])

    instance['alpha'] = instance['beta'] = instance['gamma'] = 1/3
    instance['delta'] = delta
    sigma = sum([instance['d'][i][t] for i in A for t in T]) / (len(K) * len(T))
    instance['G'] = [sigma for _ in K]
    instance['c'] = [[1 for _ in T] for _ in K]
    instance['e'] = [[sigma for _ in T] for _ in K]

    return instance


def load_energy_data_distances(filename: str, month: int, func: str, \
    energy_ref: int, center=(514962,5034533)) -> Tuple[float, Dict]:
    """Returns a tuple formed by the value of the constant mu and by a
    dictionary that contains the instance loaded from the indicated file,
    to which are added the energy data calculated based on the distance
    of the plant from the indicated `center` and the average irradiation
    (in the specified `month`).

    The `energy_ref` parameter indicates whether to calculate the constant
    mu using the energy data 1 or 2, while `func` indicates the
    proportionality with which the energy production increases as one
    moves away from the center: this parameter can assume the values
    `'constant'`, `'linear'` or `'quadratic'`.
    """

    f = {
        'constant': lambda _: 1,
        'linear':   lambda k: d[k] / d_max,
        'quadratic':   lambda k: d[k]**2 / d_max**2
    }

    if month not in range(1, 13):
        raise Exception('The month parameter must be between 1 and 12.')

    if func not in f:
        raise Exception('The func parameter must be \'constant\', \'linear\' \
            or \'quadratic\'.')

    instance = load_energy_data_1(filename) if energy_ref == 1 \
        else load_energy_data_2(filename)

    T = range(instance['nT'])

    alpha = sum([instance['e'][k][t] for t in T for k in K])

    d = facilities_positions.load_distances(FACILITIES_COORDS, center)
    d_max = max(d)

    r = {k: irradiation.load_months_avg(IRRADIATIONS[k]) for k in K}

    time = lambda t: t if len(T) == 24 else t // 2 if len(T) == 48 else t // 4
    mu = alpha / sum([f[func](k) * r[k][month][time(t)] for t in T for k in K])
    P = [mu * f[func](k) for k in K]
    e = [[P[k] * r[k][month][time(t)] for t in T] for k in K]

    instance['e'] = e

    return mu, instance
