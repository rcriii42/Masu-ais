"""Extract the AIS data for a given vessel"""
from datetime import datetime, timedelta
import os

import polars as pl

from get_data import get_storage_fname, download_ais_data
from vessel_mmsi import name_from_mmsi

vessel_ais_storage_loc = os.path.join(os.getcwd(), 'vessel_ais_data')


def extract_vessel_ais(mmsi: int, start_date: datetime | str, end_date: datetime | str | None = None) -> None:
    """Extract the AIS data for the given vessel and store to csv named for the date and vessel name

    mmsi: the mmsi number for the vessel
    start_date: the start date for the data extraction
    end_date: the end date for the data extraction
    """
    if type(start_date) is str:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date_dt = start_date
    if end_date is None:
        end_str = ''
        end_date_dt = start_date_dt
    elif type(end_date) is str:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        end_str = f'_to_{end_date}'
    else:
        end_date_dt = end_date
        end_str = f'_to_{end_date_dt.strftime("%Y-%m-%d")}'
    one_day = timedelta(days=1)
    num_days = (end_date_dt - start_date_dt).days + 1

    vessel_name = name_from_mmsi[mmsi].replace(' ', '_')
    vessel_ais_fname = f'{vessel_name}_{start_date_dt.strftime("%Y-%m-%d")}{end_str}_ais.csv'
    df_list = []

    for i in range(num_days):
        this_date = (start_date_dt + one_day * i).strftime('%Y-%m-%d')
        all_ais_fname = get_storage_fname(this_date)

        try:
            df = pl.scan_csv(all_ais_fname).filter(pl.col("mmsi") == mmsi).collect()
            print(f'Extracted AIS data for {name_from_mmsi[mmsi]} on {this_date}')
        except FileNotFoundError:
            download_ais_data(this_date)
            df = pl.scan_csv(all_ais_fname).filter(pl.col("mmsi") == mmsi).collect()
            print(f'Downloaded and extracted AIS data for {name_from_mmsi[mmsi]} on {this_date}')
        df_list.append(df)
    df_combined = pl.concat(df_list, how="vertical")
    df_sorted = df_combined.sort("base_date_time")
    df_sorted.write_csv(os.path.join(vessel_ais_storage_loc, vessel_ais_fname))


if __name__ == '__main__':
    for mmsi in name_from_mmsi.keys():
        extract_vessel_ais(mmsi,
                           datetime.fromisoformat('2025-06-10'),
                           datetime.fromisoformat('2025-06-10'))

