"""Determine discrete loads and classify AIS data points.

A load starts when the dredge enters the dig area and maintains <=2.5 knots for an extended period. It ends at the start
of the next load. AIS points are classified as:

loading - In dig area at <2.5 knots for at least 5 min
sailing - Sustained speed > 2.5 knots
discharge - In disposal area and speed < 2.5 knots for at least 5 min
delay - speed <=0.5 knots for at least 5 min"""
from datetime import datetime, timedelta
import os
import sqlite3

import geopandas as gpd
import pandas as pd
import shapely

from channel_def import project_sections, loc_types

ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')


def set_location(ais_gdf: gpd.GeoDataFrame, sections_geo: dict[str: gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Determine where the dredge is in the project

    ais_df : Geopandas dataframe with AIS positions
    sections_geo: dict of geodataframes with sections the dredge can enter

    returns: Dataframe with ais locations and an added column with dredge locations"""
    if 'section' not in ais_gdf.columns:
        ais_gdf['section'] = None
    for sec_type in sections_geo.keys():
        for g in sections_geo[sec_type].geometry:
            p = shapely.geometry.Polygon(g.coords)
            inters = ais_gdf.intersects(p)
            ais_gdf.loc[inters, 'section'] = sec_type

    return ais_gdf


def classify_delays(ais_df, min_speed=0.5, min_time=5):
    """Classify the delay points in the ais data

    delay -> speed <=0.5 knots for at least 5 min

    ais_df: Pandas or geopandas dataframe with ais data and a date field
    min_speed: minimum speed in knots
    min_time: minimum time in minutes

    returns The df with a rolling speed column and delay rows classified
    """
    time_window = timedelta(minutes=min_time)
    ais_df['rolling_speed'] = ais_df['sog'].rolling(window=time_window,
                                                    closed='both',
                                                    center=True,
                                                    min_periods=1).mean()

    ais_df.loc[ais_df['rolling_speed'] <= min_speed, 'activity'] = 'delay'
    return ais_df


def classify_cycle(ais_gdf, dig_speed=2.5, disp_speed=2.5):
    """Classify the cycle elements in the ais data"""
    ais_gdf.loc[((ais_gdf['activity'].isnull()) &
                 (ais_gdf['rolling_speed'] <= dig_speed) &
                 (ais_gdf['section'] == 'dig')), 'activity'] = 'dig'
    ais_gdf.loc[((ais_gdf['activity'].isnull()) &
                 (ais_gdf['rolling_speed'] <= disp_speed) &
                 (ais_gdf['section'] == 'disp')), 'activity'] = 'disp'
    ais_gdf.loc[ais_gdf['activity'].isnull(), 'activity'] = 'sail'
    return ais_gdf


def load_ais_data(conn: sqlite3.Connection, mmsi: int, start_ts: float, end_ts: float) -> pd.DataFrame:
    """Load AIS data between the start and end timestamps

    Adds a date column, sorts by date, and set date as index

    :param conn: Connection to the DB with AIS data
    :param mmsi: Vessel MMSI number
    :param start_ts: start timestamp in UTC ms
    :param end_ts: end timestamp in UTC ms

    :return: Pandas dataframe with AIS data
    """
    qry = f"""SELECT * FROM ais_data WHERE utc_timestamp_ms>={start_ts} AND
                                           utc_timestamp_ms<={end_ts} AND
                                           mmsi={mmsi};
           """

    new_df = pd.read_sql(qry, connection)
    new_df['date'] = new_df.apply(lambda row: datetime.fromtimestamp(row.utc_timestamp_ms / 1000), axis=1)
    new_df.sort_values(by=['date'], ascending=True, inplace=True)
    new_df.set_index('date', inplace=True)
    return new_df

if __name__ == "__main__":
    connection = sqlite3.connect(ais_database)
    cursor = connection.cursor()

    vessel_mmsi = 368349000

    start_date = datetime(2025, 6, 2, 0, 0)
    start_timestamp = start_date.timestamp() * 1000
    end_date = datetime(2025, 10, 22, 23, 59, 59)
    end_timestamp = end_date.timestamp() * 1000

    df = load_ais_data(connection, vessel_mmsi, start_timestamp, end_timestamp)
    df['activity'] = None
    df['duration'] = df.index.diff()

    gdf = gpd.GeoDataFrame(df,
                           geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
    gdf = classify_delays(gdf)
    gdf = set_location(gdf,
                       dict([(k, v) for k, v in project_sections.items() if k in loc_types]))
    gdf = classify_cycle(gdf)

    print(f'Data between {start_timestamp} and {end_timestamp} is {gdf.shape[0]} rows')
    print(f'There are {gdf[gdf["activity"]=="delay"]["duration"].sum()} delays')
    for sec_type in ['dig', 'disp', 'sail']:
        action = {"dig": "digging",
                  "disp": "dumping",
                  "sail": "sailing"}[sec_type]
        print(f'The dredge spent {gdf[gdf["section"]==sec_type]["duration"].sum()} in the {sec_type} area')
        print(f'The dredge spent {gdf[gdf["activity"]==sec_type]["duration"].sum()} '
              f'{action}')
    print(gdf.head())

    gdf.to_csv('ais_data.csv')
