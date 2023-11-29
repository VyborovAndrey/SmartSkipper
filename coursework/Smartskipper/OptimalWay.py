from math import sin, cos, atan2, radians, degrees, sqrt

from createGPX import create_gpx

class WrongStepValue(Exception):
    pass

def bearing(origin_lat, origin_lon, destination_lat, destination_lon):
    dLon = (destination_lon - origin_lon)
    x = cos(radians(destination_lat)) * sin(radians(dLon))
    y = cos(radians(origin_lat)) * sin(radians(destination_lat)) - sin(radians(origin_lat)) * cos(radians(destination_lat)) * cos(radians(dLon))
    brng = atan2(x,y)
    brng = degrees(brng)
    if brng < 0:
        brng = 360 + brng
    return brng

def find_distance(origin_lat, origin_lon, destination_lat, destination_lon):
    #радиус земли в километрах
    R = 6373.0
    origin_lat = radians(origin_lat)
    origin_lon = radians(origin_lon)
    destination_lat = radians(destination_lat)
    destination_lon = radians(destination_lon)
    dlon = destination_lon - origin_lon
    dlat = destination_lat - origin_lat
    a = sin(dlat / 2)**2 + cos(origin_lat) * cos(destination_lat) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
    

class point:
    def __init__(self, latitude, longtitude, origin_lat, origin_lon):
        self.latitude = latitude
        self.longtitude = longtitude
        self.bearing = bearing(origin_lat, origin_lon, latitude, longtitude)
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.previous_points = []
        self.wind_speed = 5
        speed_diagram = [9.0005, 0.00006, 0.00007, 0.00008, 0.00009, 0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007,
                            0.0008, 0.0009, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.011,
                            0.022, 0.055, 0.111, 0.222, 0.333, 0.544, 0.735, 0.738, 0.741, 0.744, 0.747, 0.750,
                            0.752, 0.755, 0.758, 0.761, 0.764, 0.770, 0.776, 0.782, 0.788, 0.794, 0.800, 0.805,
                            0.811, 0.817, 0.824, 0.829, 0.835, 0.841, 0.847, 0.853, 0.859, 0.865, 0.871, 0.876,
                            0.882, 0.887, 0.891, 0.896, 0.900, 0.904, 0.909, 0.913, 0.918, 0.922, 0.926, 0.928,
                            0.929, 0.931, 0.932, 0.934, 0.935, 0.937, 0.938, 0.940, 0.941, 0.943, 0.944, 0.946,
                            0.947, 0.949, 0.950, 0.951, 0.953, 0.954, 0.956, 0.958, 0.960, 0.963, 0.965, 0.967,
                            0.969, 0.971, 0.974, 0.976, 0.978, 0.978, 0.979, 0.979, 0.980, 0.980, 0.981, 0.981,
                            0.981, 0.982, 0.982, 0.983, 0.983, 0.984, 0.984, 0.985, 0.985, 0.985, 0.986, 0.986,
                            0.987, 0.988, 0.989, 0.991, 0.992, 0.993, 0.995, 0.996, 0.997, 0.999, 1.000, 0.999,
                            0.997, 0.996, 0.994, 0.993, 0.991, 0.990, 0.988, 0.987, 0.985, 0.979, 0.974, 0.968,
                            0.962, 0.956, 0.950, 0.944, 0.938, 0.932, 0.926, 0.918, 0.909, 0.900, 0.891, 0.882,
                            0.874, 0.865, 0.856, 0.847, 0.838, 0.826, 0.815, 0.803, 0.791, 0.779, 0.768, 0.756,
                            0.744, 0.732, 0.721, 0.649, 0.576, 0.504, 0.432, 0.360, 0.288, 0.216, 0.144, 0.072]
        left_part_of_diagram = [x for x in speed_diagram[::-1]]
        speed_diagram.extend(left_part_of_diagram)
        self.speed_diagram = speed_diagram

    def move_boats_from(self, step, dt):
        #радиус земли в милях
        R = 3432.505
        allpoints = []
        for degree in range(0, 361 - step, step):            
            velocity = (self.speed_diagram[degree - 1]*self.wind_speed)/R
            allpoints.append(point(self.latitude + dt * velocity * cos(radians(degree)),
                                    self.longtitude + dt * velocity * sin(radians(degree)),
                                    self.origin_lat, self.origin_lon))
            # неправильные направления
            # print(point(self.latitude + dt * velocity * cos(radians(degree)),
            #                         self.longtitude + dt * velocity * sin(radians(degree)),
            #                         self.origin_lat, self.origin_lon).bearing)
        return allpoints

class isochrone:
    def __init__(self, origin_lat, origin_lon, destination_lat, destination_lon, step):
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.destination_lat = destination_lat
        self.destination_lon = destination_lon
        self.isochrone_points = [point(origin_lat, origin_lon, origin_lat, origin_lon)]*(360//step)
        if 360 % step != 0:
            raise WrongStepValue("360 must be divisible by a step")
        self.step = step

    def find_optimal_way(self):
        dist_to_dest = min(self.isochrone_points, key=lambda point: find_distance(point.latitude, point.longtitude, self.destination_lat, self.destination_lon))
        while find_distance(dist_to_dest.latitude, dist_to_dest.longtitude, self.destination_lat, self.destination_lon) > 1.05:
            # for point in self.isochrone_points:
            #     print(point.longtitude)
            # вывод расстояния от изохроны до точки назначения
            # print(find_distance(dist_to_dest.latitude, dist_to_dest.longtitude, self.destination_lat, self.destination_lon))
            self.time_tick()
            dist_to_dest = min(self.isochrone_points, key=lambda point: find_distance(point.latitude, point.longtitude, self.destination_lat, self.destination_lon))
        return dist_to_dest.previous_points


    def time_tick(self):
        all_points = []
        for point in self.isochrone_points:
            all_points.extend(point.move_boats_from(self.step, 0.1))
        all_points.sort(key=lambda point: point.bearing)
        # for i in all_points:
        #     print(i.bearing)
        for degree in range(self.step, 361, self.step):
            sector = [point for point in all_points if point.bearing >= degree - self.step and point.bearing <= degree]
            # for i in sector:
            #     print(i.bearing)
            if sector != []:
                farthest_point = max(sector, key=lambda point: find_distance(point.latitude, point.longtitude, self.origin_lat, self.origin_lon))
                farthest_point_index = sector.index(farthest_point)
                current_isopoint = self.isochrone_points[(degree//self.step)-1]
                current_isopoint.previous_points.append(current_isopoint)
                previous_points = current_isopoint.previous_points
                self.isochrone_points[(degree//self.step)-1] = sector[farthest_point_index]
                self.isochrone_points[(degree//self.step)-1].previous_points = previous_points

if __name__ == "__main__":
    testiso = isochrone(59.86624481721071, 30.058030039090198, 59.97570601509731, 30.06934033231806, 10)
    way = testiso.find_optimal_way()
    track = []
    for point in way:
        track.append([point.latitude, point.longtitude])
    create_gpx(track, "Optimized_track")