import datetime as dt
import xarray as xr
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from time import gmtime, strftime
import requests
import os


def download_grib(forecast_hour):
    date = strftime("%Y%m%d", gmtime())
    hour = int(strftime("%H", gmtime())) + forecast_hour
    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?'
    fileurl = 'dir=%2Fgfs.{}%2F00%2Fatmos&file=gfs.t00z.pgrb2.0p25.f{:03d}&var_UGRD=on&var_VGRD=on&lev_10_m_above_ground=on()'.format(date,hour)
    url = url + fileurl
    folder = '{}'.format(date)
    filename = folder + 'f{:03d}'.format(hour)
    path = os.path.join("weatherdata", folder, filename)
    try:
        os.mkdir("weatherdata")
    except:
        pass
    try:
        os.mkdir(os.path.join("weatherdata", folder))
    except:
        pass
    try:
        r = requests.get(url)
    except:
        pass
    with open(path, 'wb') as f:
        f.write(r.content)


def download_gfs_forecasts(forecast_hours):
    """Donwload gfs with a given number of forecast files."""
    for forecast_hour in range(forecast_hours):
        download_grib(forecast_hour)
    return


def grib_to_wind_function(filename):
    ds = xr.open_dataset(filename, engine='cfgrib')
    u = ds.u10.to_numpy()
    v = ds.v10.to_numpy()
    twa = 180.0 / np.pi * np.arctan2(u, v) + 180.0
    lats_grid = np.linspace(-90, 90, 721)
    lons_grid = np.linspace(-180, 180, 1441)


    f_twa = RegularGridInterpolator(
        (lats_grid, lons_grid),
        np.flip(np.hstack((twa, twa[:, 0].reshape(721, 1))), axis=0),
    )
    return f_twa


def read_wind_functions(hours_ahead):
    wind_functions = [None]*(hours_ahead)

    date = strftime("%Y%m%d", gmtime())
    hour = int(strftime("%H", gmtime()))

    folder = '{}'.format(date)
    for i in range(hours_ahead):
        filename = folder + 'f{:03d}'.format(hour + i)
        path = os.path.join("weatherdata", folder, filename)
        wind_functions[i] = grib_to_wind_function(path)
    return wind_functions


def wind_function(winds, coordinate, time):
    forecast = min(time // 3600, len(winds)-1)
    wind = winds[forecast]
    twa = wind(coordinate)
    return twa