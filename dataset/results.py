import json

from typing import Dict


def load_data(filename: str) -> Dict:
    """Restituisce un dizionario contenente il l'esito della computazione
    organizzato per slot times e facility, caricato dal file specificato."""

    indexes_to_int = lambda d: {int(k) if k.lstrip('-').isdigit() \
        else k: v for k, v in d.items()}
    ret = json.load(open(filename), object_hook=indexes_to_int)

    time = ret['time']
    h, m, s = time.split(':')
    ret['time'] = int(h)*60 + int(m) + round(float(s))/60

    return ret
