"""Get AIS data from the NOAA website"""
import os

import urllib3


base_url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler'
storage_loc = os.path.join(os.getcwd(), 'ais_data')


def get_ais_url(date: str) -> str:
    """Generate the AIS data url for the given date

    date: A date in ISO format ('2025-06-26')

    Returns the url for the file:
    https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2025/ais-2025-06-26.csv.zst
    """
    year = date.split('-')[0]
    fname = f'ais-{date}.csv.zst'
    return '/'.join([base_url, year, fname])


def get_storage_fname(date: str) -> str:
    """Return the storage filename including path for the given date"""
    return os.path.join(storage_loc, f'ais-{date}.csv.zst')


def download_ais_data(date: str) -> None:
    """Download the AIS data file for the given date

    from: https://stackoverflow.com/a/77577568/1072246"""
    ais_url = get_ais_url(date)
    resp = urllib3.request('GET', ais_url, preload_content=False,
                           headers={'User-Agent': 'Customer User Agent If Needed'})
    fname = get_storage_fname(date)
    print(f'>>> Downloading AIS data from {ais_url} to {fname}')
    with open(fname, 'wb') as f:
        for chunk in resp.stream(65536):
            f.write(chunk)
            print('.')

    resp.release_conn()
    print(f'||| Downloaded AIS data from {ais_url} to {fname}')


if __name__ == '__main__':
    date = '2025-06-03'
    download_ais_data(date)