from os import path


def save_map(map, file, unit):
    with open(file, "w") as f:
        for point in map:
            x, y = point
            f.write(f"{x // unit} {y // unit}\n")


def load_map(file, unit):
    if not path.exists(file):
        return

    map = []

    with open(file, "r") as f:
        for line in f.readlines():
            x, y = (int(i) for i in line.split())
            map.append((x * unit, y * unit))

    return map
