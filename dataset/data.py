from pathlib import Path


A = range(1419)
K = range(10)

DATASETS = ['A', 'B']
INSTS = [1, 2, 3, 4, 5]
ENERGIES = [1, 2]
TIMES = [12, 24, 48, 96]
FUNCS = ['constant', 'linear', 'quadratic']
CENTER = (514962, 5034533)


INSTANCES_PATH = Path('data/instances')
IRRADIATIONS_PATH = Path('data/irradiation')
FACILITIES_COORDS = Path('data/facilities_coord_umt.csv')
RESULTS_PATH_JSON = Path('data/results/json')
RESULTS_PATH_CSV = Path('data/results/csv')
RESULTS_STATIC_ENERGY_PATH_JSON = RESULTS_PATH_JSON / 'static_energy'
RESULTS_DISTANCES_ENERGY_PATH_JSON = RESULTS_PATH_JSON / 'distances_energy'
RESULTS_DISTANCES_ENERGY_PATH_CSV = RESULTS_PATH_CSV / 'distances_energy'


# INSTANCES[dataset][slots][instance]
INSTANCES = {dset: {t: {inst: INSTANCES_PATH / 'dataset_{}_{}t_{}.dat'.format(dset, t, inst) \
    for inst in INSTS} for t in TIMES} for dset in DATASETS}

# IRRADIATIONS[facility]
IRRADIATIONS = {k: IRRADIATIONS_PATH / 'k{}.json'.format(k) for k in K}

# RESULTS_STATIC_ENERGY[slots][instance][energy]
RESULTS_STATIC_ENERGY = {t: {inst: {energy: RESULTS_STATIC_ENERGY_PATH_JSON /'result_B_{}t_{}_{}.json'.format(t, inst, energy) \
    for energy in ENERGIES} for inst in INSTS} for t in TIMES}

# RESULTS_DISTANCES_ENERGY[slots][instance][energy][function]
RESULTS_DISTANCES_ENERGY = {t: {inst: {energy: {func: RESULTS_DISTANCES_ENERGY_PATH_JSON / 'result_B_{}t_{}_{}_{}.json'.format(t, inst, energy, func) \
    for func in FUNCS} for energy in ENERGIES} for inst in INSTS} for t in TIMES}

# RESULTS_DISTANCES_ENERGY[slots][instance][energy][function]
RESULTS_DISTANCES_ENERGY_CSV = {t: {inst: {energy: {func: RESULTS_DISTANCES_ENERGY_PATH_CSV / 'result_B_{}t_{}_{}_{}.csv'.format(t, inst, energy, func) \
    for func in FUNCS} for energy in ENERGIES} for inst in INSTS} for t in TIMES}
