"""Test drawing lines on maps using geopandas"""
from datetime import datetime, date
import os
import sqlite3

from dash import Dash, dcc, html
import numpy as np
import plotly.graph_objects as go
import shapely.geometry

from channel_def import project_sections, colors

ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')
conn = sqlite3.connect(ais_database)
cur = conn.cursor()

min_ts, max_ts = cur.execute('SELECT min(utc_timestamp_ms), max(utc_timestamp_ms) FROM ais_data').fetchall()[0]
first_date = datetime.fromtimestamp(min_ts/1000).date()
last_date = datetime.fromtimestamp(max_ts/1000).date()
print(f'Data in DB from {first_date} to {last_date}')

fig = go.Figure()
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

            fig.add_trace(go.Scattermap(mode="markers+lines",
                                        lat=lats,
                                        lon=lons,
                                        marker=None,
                                        name=names[0],
                                        line=dict(color=colors[feature_type])
                                        )
                          )

fig.update_layout(title_text='HSC Maintenance',
                  showlegend=True,
                  map={'style': 'satellite',
                       'zoom': 10,
                       'center': {'lat': 29.49854, 'lon': -94.866943}
                       },
                  width=1000,
                  height=1000,
                  )

app = Dash()
app.layout = html.Div([dcc.Graph(figure=fig)])

app.run(debug=True, use_reloader=False)
