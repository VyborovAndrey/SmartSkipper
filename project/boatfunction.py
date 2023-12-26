import numpy as np
from scipy.interpolate import RegularGridInterpolator


def boat_properties():
    polars = np.genfromtxt('polars/polar-ITA70.csv', delimiter=';')
    polars = np.nan_to_num(polars)

    ws = polars[0, 1:]
    wa = polars[1:, 0]
    values = polars[1:, 1:]

    f = RegularGridInterpolator(
        (ws, wa), values.T,
        bounds_error=False,
        fill_value=None
    )
    return f


def boat_speed_function(boat, brng):
    brng = np.abs(brng)
    if brng > 180:
        brng = 360. - brng
    brng = int(np.abs(brng))
    boat_speed = boat((5, brng))
    return boat_speed