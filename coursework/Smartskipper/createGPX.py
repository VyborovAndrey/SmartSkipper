from gpx_converter import Converter
import csv

#list = [["latitude","longitude","time"],[30,60,"время"]] - формат списка

def create_gpx(list):
    with open('out.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list)
    Converter(input_file="out.csv").csv_to_gpx(lats_colname='latitude', longs_colname='longitude', times_colname='time', output_file='your_input.gpx')




