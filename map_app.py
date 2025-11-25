"""Test drawing lines on maps using geopandas"""

from dash import Dash, dcc, html
import numpy as np
import plotly.express as px
import shapely.geometry

from channel_def import channel_sections as geo_df

lats = []
lons = []
names = []

for feature, name in zip(geo_df.geometry, geo_df.name):
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
        lats = np.append(lats, None)
        lons = np.append(lons, None)
        names = np.append(names, None)

fig = px.line_map(lat=lats, lon=lons,
                  hover_name=names,
                  map_style="satellite",
                  zoom=10,
                  center={"lat": 29.49854, "lon": -94.866943},
                  width=1000,
                  height=1000)

app = Dash()
app.layout = html.Div([dcc.Graph(figure=fig)])

app.run(debug=True, use_reloader=False)
