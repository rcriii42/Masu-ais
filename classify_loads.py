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

import pandas as pd

ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')


def classify_delays(ais_df, min_speed=0.5, min_time=5):
    """Classify the delay points in the ais data

    delay -> speed <=0.5 knots for at least 5 min

    ais_df: pandas dataframe with ais data and a date field
    min_speed: minimum speed in knots
    min_time: minimum time in minutes

    returns The df with delay rows classified
    """
    time_window = timedelta(minutes=min_time)
    ais_df['rolling_speed'] = ais_df['sog'].rolling(window=time_window,
                                                    closed='both',
                                                    center=True,
                                                    min_periods=1).mean()

    ais_df.loc[ais_df['rolling_speed'] <= min_speed, 'activity'] = 'delay'
    return ais_df


if __name__ == "__main__":
    connection = sqlite3.connect(ais_database)
    cursor = connection.cursor()

    vessel_mmsi = 368349000

    start_date = datetime(2025, 6, 2, 0, 0)
    start_timestamp = start_date.timestamp() * 1000
    end_date = datetime(2025, 6, 4, 23, 59, 59)
    end_timestamp = end_date.timestamp() * 1000
    qry = f"""SELECT * FROM ais_data WHERE utc_timestamp_ms>={start_timestamp} AND
                                           utc_timestamp_ms<={end_timestamp} AND
                                           mmsi={vessel_mmsi};
           """

    df = pd.read_sql(qry, connection)
    df['activity'] = None
    df['date'] = df.apply(lambda row: datetime.fromtimestamp(row.utc_timestamp_ms/1000), axis=1)
    df['duration'] = df['date'].diff()
    df.set_index('date', inplace=True)
    df = classify_delays(df)

    print(f'Data between {start_timestamp} and {end_timestamp} is {df.shape[0]} rows')
    print(f'There are {df[df["activity"]=="delay"]["duration"].sum()} delays')
    print(df.head())

    df.to_csv('ais_data.csv')
