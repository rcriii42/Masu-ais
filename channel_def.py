"""
channel_def.py - Define the channel shapes
"""
from glob import glob
import os.path

import geopandas
import pandas
from shapely.geometry import LineString

# The folder with project specific coordinate files
# Includes csv files with N, E coordinates of channel centerlines ("cl_*.csv"), dig areas ("dig_*.csv"),
# and disposal areas ("disp_*.csv")
project_folder = os.path.join(os.getcwd(), 'W912HY24B0007')

# Temporarily put any dredge tracks (from Marine Traffic) that you want to show on the map in gray
names_tracks = []  # ['Break of Dawn 20230509']
coords_tracks = []  # ['Break_of_Dawn_positions_Export_2023-05-09.csv'

names = []
coord_files = []

# The keys of the colors dict are the allowed shape types to display
# Coord files must have 'key_' in the filename, or they will be ignored
colors = {'cl': 'black',
          'dig': 'green',
          'disp': 'magenta',
          'track': 'gray'}
loc_types = ['dig', 'disp']  # These are the section types the dredge can be inside

for fname in glob(os.path.join(project_folder, '*.csv')):
    coord_files.append(fname)
    names.append(os.path.splitext(os.path.basename(fname))[0])

geo_inputs = {}
for s in colors.keys():
    geo_inputs[s] = {'name':       [],  # ['CL HSC',     'CL BSC',     'CL BCC'],
                     'coord_file': [],  # ['cl_HSC.csv', 'cl_BSC.csv', 'cl_BCC.csv'],
                     'geometry':   [],
                     'color':      [],
                     'stations':   [],
                     }

removed: list[tuple[str:str]] = []
for name, fname in zip(names, coord_files):
    if '.csv' in fname:
        coords = pandas.read_csv(os.path.join(project_folder, fname))
        geom = LineString(list(zip(coords.E, coords.N)))
    elif '.dxf' in fname:
        dxf_gdf = geopandas.read_file(os.path.join(project_folder, fname))
        geom = dxf_gdf.geometry
    else:
        print(f'WARNING File type not recognized for file {fname}, removing from the project files')
        removed.append((name, fname))
        continue
    ftype = os.path.basename(fname).split('_')[0]
    if ftype not in colors.keys():
        print(f'WARNING Feature type not recognized for file {fname}, removing from the project files')
        removed.append((name, fname))
        continue
    geo_inputs[ftype]['name'].append(name)
    geo_inputs[ftype]['coord_file'].append(fname)
    geo_inputs[ftype]['geometry'].append(geom)
    geo_inputs[ftype]['color'].append(colors[ftype])
    if ftype == 'cl':
        geo_inputs[ftype]['stations'].append(list(coords.Station))
    else:
        geo_inputs[ftype]['stations'].append(None)
    # Keeping the following in case I need to know how to convert coord files that are in lat/long
    # elif 'positions_Export' in fname:  # Marine Traffic position export
    #     # Marine traffic gives lat/long, so we have to convert it to (E, N) for the agent creation
    #     track = geopandas.geodataframe.GeoDataFrame(coords,
    #                                                 geometry=geopandas.points_from_xy(coords.Longitude, coords.Latitude,
    #                                                                                   crs="EPSG:4326"),
    #                                                 crs="EPSG:4326")
    #     track.to_crs(epsg=2278, inplace=True)
    #     geo_input['geometry'].append(LineString(track.geometry.to_list()))
    #     geo_input['stations'].append(None)
    #     geo_input['color'].append('gray')  # Show tracks in gray

for name, fname in removed:
    names.pop(name)
    coord_files.pop(fname)
print('Loaded the following files:')
for fname in coord_files:
    print(fname)
print()

project_sections = {}
for gtype in geo_inputs.keys():
    project_sections[gtype] = geopandas.GeoDataFrame(geo_inputs[gtype], crs='epsg:2278').to_crs(epsg=4326)
