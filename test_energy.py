import json

from dataset import get_energy_data_1, get_energy_data_2, extract_data
from energy_model import convert_result, run_instance


if __name__ == '__main__':
    data = get_energy_data_1('../datasets/dataset_B_12t_1.dat')

    result = convert_result(run_instance(data, verbose=True), data['nA'], data['nK'], data['nT'])
    result['status'] = str(result['status'])

    json.dump(result, open('result.json', 'w'))

    print('\nGAP:')
    print(int(result['obj_value'] - result['obj_bound']))
    print(result['obj_value'])
