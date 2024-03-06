from copy import deepcopy
from createGPX import create_gpx

from utility import bearing, find_distance
from boatfunction import boat_speed_function, boat_properties
from weather import read_wind_functions, wind_function, download_gfs_forecasts
from geovectorslib import geod

import numpy as np

vectorized_boat_speed_f = np.vectorize(boat_speed_function)

class WrongStepValue(Exception):
    pass


class point:
    def __init__(self, latitude, longtitude, origin_lat, origin_lon, previous_points = []):
        self.latitude = latitude
        self.longtitude = longtitude
        self.bearing = bearing(origin_lat, origin_lon, latitude, longtitude)
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.previous_points = previous_points


    def move_boats_from(self, step, wind, boat, time, dt):
        new_lat = np.repeat(self.latitude, 360//step)
        new_lon = np.repeat(self.longtitude, 360//step)
        brngs = np.linspace(0, 360, 360//step)
        wind = wind_function(wind, [(self.latitude, self.longtitude)], time*10)
        bs = vectorized_boat_speed_f(boat, brngs - wind) * dt
        geod.direct(new_lat, new_lon, brngs, bs)
        new_coords = geod.direct(new_lat, new_lon, brngs, bs)
        new_lat = new_coords['lat2']
        new_lon = new_coords['lon2']
        allpoints = [point(lat, lon, self.origin_lat, self.origin_lon, self.previous_points) for lat, lon in zip(new_lat, new_lon)]
        return allpoints


class isochrone:
    def __init__(self, origin_lat, origin_lon, destination_lat, destination_lon, sector_angle):
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.destination_lat = destination_lat
        self.destination_lon = destination_lon
        self.isochrone_points = []

        start_point = point(origin_lat, origin_lon, origin_lat, origin_lon)
        start_point.previous_points.append(start_point)
        for _ in range(360//sector_angle):
            self.isochrone_points.append(deepcopy(start_point))
        if 360 % sector_angle != 0:
            raise WrongStepValue("360 must be divisible by a step")
        self.sector_angle = sector_angle
        download_gfs_forecasts(10)
        self.wind = read_wind_functions(10)
        self.time = 0
        self.dt = 60

        self.boat = boat_properties()

    def find_optimal_way(self):
        dist_to_dest = min(self.isochrone_points, key=lambda point: find_distance(point.latitude, point.longtitude, self.destination_lat, self.destination_lon))
        while find_distance(dist_to_dest.latitude, dist_to_dest.longtitude, self.destination_lat, self.destination_lon) > 1.0:

            # вывод расстояния от изохроны до точки назначения
            print(find_distance(dist_to_dest.latitude, dist_to_dest.longtitude, self.destination_lat, self.destination_lon))

            self.time_tick()
            dist_to_dest = min(self.isochrone_points, key=lambda point: find_distance(point.latitude, point.longtitude, self.destination_lat, self.destination_lon))
        return dist_to_dest, self.isochrone_points

    def time_tick(self):
        all_points = []
        for point in self.isochrone_points:
            all_points.extend(point.move_boats_from(self.sector_angle, self.wind, self.boat, self.time, self.dt))
        for degree in range(self.sector_angle, 361, self.sector_angle):
            sector = [point for point in all_points if point.bearing >= degree - self.sector_angle and point.bearing <= degree]
            if sector != []:
                farthest_point = deepcopy(max(sector, key=lambda point: find_distance(point.latitude, point.longtitude, self.origin_lat, self.origin_lon)))
                farthest_point.previous_points.append(farthest_point)
                self.isochrone_points[(degree//self.sector_angle)-1] = deepcopy(farthest_point)
        self.time += self.dt

def create_optimal_gpx(opti_track, isochrone_tracks, Isochrone = False):
    track = []
    for point in opti_track.previous_points:
        track.append([point.latitude, point.longtitude])
    create_gpx(track, "Optimized_track")
    if Isochrone is True:
        for i in range(len(isochrone_tracks)):
            track = []
            for point in isochrone_tracks[i].previous_points:
                track.append([point.latitude, point.longtitude])
            create_gpx(track, "Isochrone_track{Number}".format(Number = i))


if __name__ == "__main__":  
    testiso = isochrone(59.95222983291799, 30.184248506383703, 59.9927421613013, 29.70604781109711, 4)
    opti_track, isochrone_tracks = testiso.find_optimal_way()
    create_optimal_gpx(opti_track, isochrone_tracks, True)