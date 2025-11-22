"""Extract the AIS data for a given vessel"""
from datetime import datetime, timedelta
import os

import pandas as pd

from get_data_from_noaa import get_storage_fname, download_ais_data
from vessel_mmsi import name_from_mmsi, mmsi_from_name

vessel_ais_storage_loc = os.path.join(os.getcwd(), 'vessel_ais_data')
if not os.path.exists(vessel_ais_storage_loc):
    print(f'{vessel_ais_storage_loc} not found. Creating it.')
    os.makedirs(vessel_ais_storage_loc)


def extract_vessel_ais(mmsi: int | list[int] | None,
                       start_date: datetime | str, end_date: datetime | str | None = None,
                       mmsi_index: int = 2) -> None:
    """Extract the AIS data for the given vessel and store to csv named for the date and vessel name

    mmsi: the mmsi number for the vessel
    start_date: the start date for the data extraction
    end_date: the end date for the data extraction
    mmsi_index: The column number of the mmsi in the data
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

    if isinstance(mmsi, int):
        mmsi_list = [mmsi]
        vessel_name = name_from_mmsi(mmsi).replace(' ', '_')
    elif mmsi is None:
        vessel_name = 'All'
    else:
        vessel_name = 'multiple_vessels'
        mmsi_list = mmsi

    vessel_ais_fname = f'{vessel_name}_{start_date_dt.strftime("%Y-%m-%d")}{end_str}_ais.csv'
    df_list = []

    print(f'Extracting AIS data for vessels {mmsi_list} from {start_date} to {end_date}')
    for i in range(num_days):
        this_date = (start_date_dt + one_day * i).strftime('%Y-%m-%d')
        all_ais_fname = get_storage_fname(this_date)

        try:
            df = pd.read_csv(all_ais_fname)
            print(f'Read data from {all_ais_fname}')
        except FileNotFoundError:
            download_ais_data(this_date)
            df = pd.read_csv(all_ais_fname)
            print(f'Downloaded and read data from {all_ais_fname}')
        df.columns = [c.lower() for c in df.columns]
        if mmsi is None:
            df_list.append(df)
            print(f'Grabbed all data from {all_ais_fname}')
        else:
            df_list.append(df.query('mmsi in @mmsi_list'))
            print(f'Filtered mmsi {mmsi_list} from {all_ais_fname}, leaving {df_list[-1].shape} points of data')
    df_combined = pd.concat(df_list, ignore_index=True)
    df_sorted = df_combined.sort_values(by="base_date_time", inplace=False)
    df_sorted.to_csv(os.path.join(vessel_ais_storage_loc, vessel_ais_fname), index=False)


if __name__ == '__main__':

    extract_vessel_ais(list(mmsi_from_name.values()),
                       datetime.fromisoformat('2025-06-02'),
                       datetime.fromisoformat('2025-06-04'))

