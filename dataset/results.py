import json
import numpy as np
import pandas as pd

from dataset.data import *
from typing import Dict


def load_data(filename: str) -> Dict:
    """Returns a dictionary containing the computation result organized
    by slot times and facility, loader from the specified file."""

    indexes_to_int = lambda d: {int(k) if k.lstrip('-').isdigit() \
        else k: v for k, v in d.items()}
    ret = json.load(open(filename), object_hook=indexes_to_int)

    time = ret['time']
    h, m, s = time.split(':')
    ret['time'] = int(h)*60 + int(m) + round(float(s))/60

    return ret

def convert_to_csv(filename: str, new_filename: str, nT: int) -> None:
    res = load_data(filename)
    T = np.arange(nT)

    arrays = [
        np.concatenate([np.full(len(K), i) for i in T]),
        np.concatenate([K for _ in T]),
    ]
    tuples = list(zip(*arrays))

    index = pd.MultiIndex.from_tuples(tuples, names=['t', 'k'])

    res = {k: res[k] for k in res if isinstance(k, int)}
    s = pd.DataFrame(
        [[res[t][k]['g'], res[t][k]['v'], res[t][k]['z'], res[t][k]['conn'],] for t in T for k in K],
        columns=['g', 'v', 'z', 'conn'],
        index=index
    )
    s.to_csv(open(new_filename, 'w'))
