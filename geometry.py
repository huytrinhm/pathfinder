def snap_point(x, y, unit):
    snapped_x = round(x / unit) * unit
    snapped_y = round(y / unit) * unit
    return snapped_x, snapped_y


def in_polygon(map, x, y):
    inside = False
    for u in range(len(map) - 1):
        xu, yv = map[u]
        xv, yu = map[u + 1]

        if yv > yu:
            xu, xv = xv, xu
            yv, yu = yu, yv

        if y > yv and y <= yu and x <= xu + (xv - xu) * (y - yv) / (yu - yv):
            inside = not inside

    return inside


def orientation(a, b, c):
    xa, ya = a
    xb, yb = b
    xc, yc = c
    val = (xc - xb) * (yb - ya) - (xb - xa) * (yc - yb)
    return 1 if val > 0 else 2 if val < 0 else 0


def on_segment(a, b, c):
    xa, ya = a
    xb, yb = b
    xc, yc = c
    return (
        xb <= max(xa, xc)
        and xb >= min(xa, xc)
        and yb <= max(ya, yc)
        and yb >= min(ya, yc)
    )


def intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, p2, q1):
        return True

    if o2 == 0 and on_segment(p1, q2, q1):
        return True

    if o3 == 0 and on_segment(p2, p1, q2):
        return True

    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False
