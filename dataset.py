def extract_data(dataset):
    def format(data):
        return [[float(x) for x in el.split(',')] for el in data]

    lines = open(dataset, 'r').readlines()

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


def get_energy_data_1(dataset, delta=1):
    data = extract_data(dataset)

    data['alpha'] = 1/3
    data['beta'] = 1/3
    data['gamma'] = 1/3
    data['delta'] = delta
    data['G'] = [data['C'][k] / 2 for k in range(data['nK'])]
    data['c'] = [[1 for _ in range(data['nT'])] for _ in range(data['nK'])]
    data['e'] = [[data['C'][k] / 2 for _ in range(data['nT'])] for k in range(data['nK'])]

    return data


def get_energy_data_2(dataset, delta=1):
    data = extract_data(dataset)

    data['alpha'] = 1/3
    data['beta'] = 1/3
    data['gamma'] = 1/3
    data['delta'] = delta
    sigma = sum([sum([data['d'][i][t] for i in range(data['nA'])]) for t in range(data['nT'])]) / (data['nA'] * data['nT'])
    data['G'] = [sigma for _ in range(data['nK'])]
    data['c'] = [[1 for _ in range(data['nT'])] for _ in range(data['nK'])]
    data['e'] = [[sigma for _ in range(data['nT'])] for _ in range(data['nK'])]

    return data
