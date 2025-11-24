"""Load data in Port Houston format to the DB

The port format has the following fields:
"longitude","latitude","MMSI","SPEED","HEADING","COURSE","STATUS","TIMESTAMP"

in the DB:
MMSI => mmsi
SPEED  => sog
HEADING  => heading
COURSE  => cog
timeStamp => utc_timestamp_ms
"""

from datetime import datetime, timezone
import glob
import os
import sqlite3

import pandas as pd

port_data_loc = os.path.join(os.getcwd(), 'AIS_RBWeeks_Magdalen')
ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')

AIS_DATA_TABLE_SQL = """create table ais_data(utc_timestamp_ms integer not null,
                                              status           integer,
                                              cargo            integer,
                                              longitude        REAL,
                                              latitude         REAL,
                                              sog              REAL,
                                              cog              REAL,
                                              heading          REAL,
                                              draft            REAL,
                                              file_id          integer,
                                              mmsi             integer not null
                                             );"""

UPLOADED_FILES_TABLE_SQL = """create table uploaded_files(filename    TEXT,
                                                          upload_date TEXT,
                                                          file_id     INTEGER not null
                                                                      constraint uploaded_files_pk
                                                                      primary key
                                                         );"""


def load_port_data_to_db(port_data_fname: str, ais_db_connection: sqlite3.Connection):
    """Load a file of data in Port Houston format to the DB"""
    ais_db_cursor = ais_db_connection.cursor()
    ais_db_cursor.execute("SELECT * FROM uploaded_files WHERE filename=?", (port_data_fname,))
    rows = ais_db_cursor.fetchall()
    if len(rows) > 0:
        print(f'load_port_data_to_db: file {port_data_fname} already loaded on {rows[0][1]}')
        return
    else:
        ais_db_cursor.execute("INSERT INTO uploaded_files (filename, upload_date, file_id) VALUES (?, ?, ?)",
                              (port_data_fname, datetime.now(), None))
        ais_db_connection.commit()
        ais_db_cursor.execute("SELECT last_insert_rowid()")
        rows = ais_db_cursor.fetchall()
        file_id = rows[0][0]

    df = pd.read_csv(os.path.join(port_data_loc, port_data_fname))
    df.rename(columns={"longitude": "longitude",
                       "latitude": "latitude",
                       "MMSI": "mmsi",
                       "SPEED": "sog",
                       "HEADING": "heading",
                       "COURSE": "cog",
                       "STATUS": "status",
                       "TIMESTAMP": "utc_timestamp_ms"}, inplace=True)
    df['file_id'] = file_id
    df.to_sql(name='ais_data', con=ais_db_connection, if_exists='append', index=False)
    ais_db_connection.commit()


if __name__ == '__main__':
    connection = sqlite3.connect(ais_database)
    cursor = connection.cursor()
    if debug := True:  # Set to false once there is good data in the db
        cursor.execute('DROP TABLE IF EXISTS ais_data')
        cursor.execute('DROP TABLE IF EXISTS uploaded_files')
        connection.commit()
        cursor.execute(AIS_DATA_TABLE_SQL)
        cursor.execute(UPLOADED_FILES_TABLE_SQL)
        connection.commit()

    for fname_full in sorted(glob.glob(os.path.join(port_data_loc, "*.csv"))):
        fname = os.path.basename(fname_full)
        print(f'------------ Loading ais data from {fname} --------------------')
        load_port_data_to_db(fname, connection)
        file_id = cursor.execute("SELECT file_id FROM uploaded_files WHERE filename=?",
                                 (fname, )).fetchone()[0]
        ais_df = pd.read_sql(f'SELECT * FROM ais_data WHERE file_id={file_id}', con=connection,)
        start_date = datetime.fromtimestamp(ais_df.utc_timestamp_ms.min()/1000, timezone.utc)
        end_date = datetime.fromtimestamp(ais_df.utc_timestamp_ms.max()/1000, timezone.utc)
        mmsi_list = ais_df.mmsi.unique()

        print(f'AIS data in {fname}: {ais_df.shape} Spanning {start_date} to {end_date}, including vessels:')
        for mmsi in mmsi_list:
            vessel_data = cursor.execute(f'SELECT * FROM vessel_data WHERE mmsi={mmsi}').fetchall()
            print(vessel_data)
