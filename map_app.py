"""Test drawing lines on maps using geopandas"""
from datetime import datetime, date, timedelta
import os
import sqlite3

from dash import Dash, dcc, html, Input, Output, callback
import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import shapely.geometry

from channel_def import project_sections, colors
from classify_loads import load_ais_data

ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')
conn = sqlite3.connect(ais_database)
cur = conn.cursor()

min_ts, max_ts = cur.execute('SELECT min(utc_timestamp_ms), max(utc_timestamp_ms) FROM ais_data').fetchall()[0]
first_date = datetime.fromtimestamp(min_ts/1000)
last_date = datetime.fromtimestamp(max_ts/1000)
print(f'Data in DB from {first_date} to {last_date}')

rows = cur.execute('SELECT distinct(mmsi) FROM ais_data').fetchall()
mmsi_list = [x[0] for x in rows]
vessel_names = []
for m in mmsi_list:
    vn = cur.execute('SELECT vessel_name FROM vessel_data WHERE mmsi = ?', (m, )).fetchall()[0][0]
    vessel_names.append(vn)
opts = [{'label': vn, 'value': vmmsi} for vn, vmmsi in zip(vessel_names, mmsi_list)]
vessel_picker = dcc.Dropdown(options=opts,
                             value=mmsi_list[0],
                             id='vessel-picker'
                             )

date_picker = dcc.DatePickerRange(id='my-date-picker-range',
                                  min_date_allowed=first_date,
                                  max_date_allowed=last_date,
                                  # initial_visible_month=date(2025, 6, 2),
                                  start_date=first_date,
                                  end_date=first_date + timedelta(days=2)
                                  )
map_graph = dcc.Graph(id='map-graph')


def get_vessel_track(conn: sqlite3.Connection, vessel_mmsi: int,
                     start_time: datetime, end_time: datetime) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame with the track for the given vessel over a timeframe"""
    start_ts = start_time.timestamp()*1000
    end_ts = end_time.timestamp()*1000
    df = load_ais_data(conn, vessel_mmsi, start_ts, end_ts)
    geo_inputs = {'name': ['dredge_track'],
                  'coord_file': ["from_DB"],
                  'geometry': [shapely.geometry.linestring.LineString(gpd.points_from_xy(df.longitude, df.latitude,
                                                                                         crs="EPSG:4326"))],
                  'color': ['gray'],
                  'stations': [None],
                  'sog': [df['sog']]
                  }
    gdf = gpd.GeoDataFrame(geo_inputs,
                           geometry=geo_inputs['geometry'],
                           crs="EPSG:4326")
    return gdf


@callback(Output('map-graph', 'figure'),
          Input('vessel-picker', 'value'),
          Input('my-date-picker-range', 'start_date'),
          Input('my-date-picker-range', 'end_date'))
def update_map(vessel_mmsi: int, start_date, end_date) -> go.Figure:
    """Update the map widget after changes to vessel or dates"""

    fig = go.Figure()
    traces = dict()
    if start_date > end_date:
        start_dt, end_dt = datetime.fromisoformat(end_date), datetime.fromisoformat(start_date)
    elif start_date == end_date:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = start_dt + timedelta(days=1)
    else:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

    project_sections['track'] = get_vessel_track(sqlite3.connect(ais_database),
                                                 vessel_mmsi,
                                                 start_dt,
                                                 end_dt)
    for feature_type in colors.keys():
        geo_df = project_sections[feature_type]
        for feature, name in zip(geo_df.geometry, geo_df.name):
            lats = []
            lons = []
            names = []
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name]*len(y))
                if feature_type == 'disable color scale':  # 'track':
                    marker = {'color': geo_df['sog'],
                              'colorscale': 'turbo'}
                else:
                    marker = None

                traces[name] = s = go.Scattermap(mode="markers+lines",
                                                 lat=lats,
                                                 lon=lons,
                                                 marker=marker,
                                                 name=names[0],
                                                 line=dict(color=colors[feature_type])
                                                 )
                fig.add_trace(s)
    fig.update_layout(title_text='HSC Maintenance',
                      showlegend=True,
                      map={'style': 'satellite',
                           'zoom': 10,
                           'center': {'lat': 29.49854, 'lon': -94.866943}
                           },
                      width=1000,
                      height=1000,
                      )
    return fig


app = Dash()
app.layout = html.Div([map_graph, vessel_picker, date_picker])

app.run(debug=True, use_reloader=False)
