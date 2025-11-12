"""Extract the AIS data for a given vessel"""
import os

import polars as pl

from get_data import get_storage_fname, download_ais_data
from vessel_mmsi import name_from_mmsi


def extract_vessel_ais(mmsi: int, start_date: str, end_date: str | None = None) -> None:
    """Extract the AIS data for the given vessel and store to csv named for the date and vessel name

    mmsi: the mmsi number for the vessel
    start_date: the start date for the data extraction
    end_date: the end date for the data extraction
    """
    vessel_name = name_from_mmsi[mmsi]
    all_ais_fname = get_storage_fname(start_date)
    if end_date is None:
        end_str = ''
    else:
        end_str = f'_to_{end_date}'
    vessel_ais_fname = os.path.join(os.path.curdir, f'{vessel_name}_{start_date}{end_str}_ais.csv')
    df = pl.scan_csv(all_ais_fname).filter(pl.col("mmsi") == mmsi).collect()
    df.write_csv(vessel_ais_fname)


if __name__ == '__main__':
    for mmsi in name_from_mmsi.keys():
        start_date = '2025-06-10'
        try:
            extract_vessel_ais(mmsi, start_date)
            print(f'Extracted AIS data for {name_from_mmsi[mmsi]} on {start_date}')
        except FileNotFoundError:
            download_ais_data(start_date)
            extract_vessel_ais(mmsi, start_date)
            print(f'Downloaded and extracted AIS data for {name_from_mmsi[mmsi]} on {start_date}')
