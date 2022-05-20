import math

from typing import List, Tuple


def load_data(filename: str) -> List[Tuple[float, float]]:
    """Returns a list containing the coordinates of each facility."""

    lines = open(filename, 'r').readlines()

    coords = list()
    for line in lines[1:]:
        x, y = line.split(',')
        coords.append((float(x), float(y)))

    return coords


def load_distances(filename: str, center: Tuple[float, float]) -> List[int]:
    """Returns a list containing the Euclidean distance of each facility
    from the specified `center`."""

    def eucl_dist(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((y1-y2)**2 + (x1-x2)**2)

    coords = load_data(filename)

    dists = list()
    for coord in coords:
        dists.append(eucl_dist(coord, center))

    return dists
