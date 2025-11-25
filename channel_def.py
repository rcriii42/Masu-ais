"""
channel_def.py - Define the channel shapes
"""
from dataclasses import dataclass
from glob import glob
import os.path

import geopandas
import pandas
from shapely.geometry import Polygon, LineString

# The folder with project specific coordinate files
# Includes csv files with N, E coordinates of channel centerlines ("cl_*.csv"), dig areas ("dig_*.csv"),
# and disposal areas ("disp_*.csv")
project_folder = os.path.join(os.getcwd(), 'W912HY24B0007')


# Temporarily put any dredge tracks (from Marine Traffic) that you want to show on the map in gray
names_tracks = []  # ['Break of Dawn 20230509']
coords_tracks = []  # ['Break_of_Dawn_positions_Export_2023-05-09.csv'

# Manually including coordinate files TODO: Just grab all the coord files in the directory
geo_input = {'name':       ['CL HSC',     'CL BSC',     'CL BCC'],
             'coord_file': ['cl_HSC.csv', 'cl_BSC.csv', 'cl_BCC.csv'],
             'geometry':   [],
             'color':      [],
             'stations':   [],
             }

for name, fname in zip(geo_input['name'], geo_input['coord_file']):
    if '.csv' in fname:
        coords = pandas.read_csv(os.path.join(project_folder, fname))
    elif '.dxf' in fname:
        dxf_gdf = geopandas.read_file(os.path.join(project_folder, fname))
        print(dxf_gdf)
    else:
        print(f'WARNING File type not recognized for file {fname}, removing from the project files')
        geo_input['name'].remove(name)
        geo_input['coord_file'].remove(fname)
    if fname[:2] == 'cl':       # Channel centerline
        geo_input['geometry'].append(LineString(list(zip(coords.E, coords.N))))
        geo_input['stations'].append(list(coords.Station))
        geo_input['color'].append('black')
    elif fname[:4] == 'disp':   # Disposal area
        if '.csv' in fname:
            geo_input['geometry'].append(LineString(list(zip(coords.E, coords.N))))
        else:
            geo_input['geometry'].append(dxf_gdf.geometry)
        geo_input['stations'].append(None)
        geo_input['color'].append('magenta')
    elif 'positions_Export' in fname:  # Marine Traffic position export
        # Marine traffic gives lat/long, so we have to convert it to (E, N) for the agent creation
        track = geopandas.geodataframe.GeoDataFrame(coords,
                                                    geometry=geopandas.points_from_xy(coords.Longitude, coords.Latitude,
                                                                         crs="EPSG:4326"),
                                                    crs="EPSG:4326")
        track.to_crs(epsg=2278, inplace=True)
        geo_input['geometry'].append(LineString(track.geometry.to_list()))
        geo_input['stations'].append(None)
        geo_input['color'].append('gray')  # Show tracks in gray
    else:                       # Red/Green side dig areas
        geo_input['geometry'].append(Polygon(list(zip(coords.E, coords.N))))
        geo_input['stations'].append(None)
        geo_input['color'].append(fname.split('_')[0])  # assume that the first word of the filename is the color


channel_sections = geopandas.GeoDataFrame(geo_input, crs='epsg:2278').to_crs(epsg=4326)
# channel_sections.set_crs(crs='epsg:2278', inplace=True)  # 2278 is the crs for HSC north/east
# channel_sections.to_file("channel_sections.shp", engine="pyogrio")
