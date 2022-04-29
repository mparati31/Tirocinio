import json

from dataset import add_energy_data_1, add_energy_data_2, extract_data
from energy_model import convert_result, run_instance

data = extract_data('../datasets/dataset_B_12t_1.dat')
add_energy_data_1(data)

result = convert_result(run_instance(data, verbose=True), data['nA'], data['nK'], data['nT'])
result['status'] = str(result['status'])

json.dump(result, open('result.json', 'w'))
