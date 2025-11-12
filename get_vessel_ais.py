"""Extract the AIS data for a given vessel"""
import os

import polars as pl

from get_data import ais_storage_loc, get_storage_fname
from vessel_mmsi import mmsi_from_name, name_from_mmsi


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
        extract_vessel_ais(mmsi, '2025-06-09')
        print(f'Extracted AIS data for {name_from_mmsi[mmsi]}')
