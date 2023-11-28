from gpx_converter import Converter
import csv

#list = [["latitude","longitude","time"],[30,60,"время"]] - формат списка

def create_gpx(list: list, name: str):
    list.insert(0, ["latitude", "longitude", "time"])
    with open(f"{name}.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list)
    Converter(input_file=f"{name}.csv").csv_to_gpx(lats_colname='latitude', longs_colname='longitude', times_colname='time', output_file=f'{name}.gpx')




