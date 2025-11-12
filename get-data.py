"""Get AIS data from the NOAA website"""
import os

base_url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler'


def get_ais_url(date: str) -> str:
    """Generate the AIS data url for the given date

    date: A date in ISO format ('2025-06-26')

    Returns the url for the file:
    https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2025/ais-2025-06-26.csv.zst
    """
    year = date.split('-')[0]
    fname = f'ais-{date}.csv.zst'
    return os.path.join(base_url, year, fname)
