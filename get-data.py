"""Get AIS data from the NOAA website"""
import os

import urllib3


base_url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler'
ais_storage_loc = os.path.join(os.getcwd(), 'ais_data')


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
    return os.path.join(ais_storage_loc, f'ais-{date}.csv.zst')


def download_ais_data(date: str) -> None:
    """Download the AIS data file for the given date

    from: https://stackoverflow.com/a/77577568/1072246"""
    ais_url = get_ais_url(date)
    resp = urllib3.request('GET', ais_url, preload_content=False,
                           headers={'User-Agent': 'Customer User Agent If Needed'})
    chunk_size = 65536
    size = int(resp.headers['Content-Length'])
    total_chunks = int(size / chunk_size)
    fname = get_storage_fname(date)
    if os.path.isfile(fname):
        print(f'--- AIS data already downloaded from {ais_url}')
    else:
        print(f'>>> Downloading {size} of AIS data from {ais_url} to {fname}')
        with open(fname, 'wb') as f:
            numchunks = 0
            i = 9
            for chunk in resp.stream(chunk_size):
                f.write(chunk)
                numchunks += 1
                if numchunks >= total_chunks/10:
                    print(i, end='', flush=True)
                    numchunks = 0
                    i -= 1

        resp.release_conn()
        print(f'\n||| Downloaded AIS data from {ais_url} to {fname}')


if __name__ == '__main__':
    date = '2025-06-05'
    download_ais_data(date)
