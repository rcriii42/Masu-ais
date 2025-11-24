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

import datetime
import os
import sqlite3

import pandas as pd

port_data_loc = os.path.join(os.getcwd(), 'AIS_RBWeeks_Magdalen')
ais_database = os.path.join(os.getcwd(), 'Matsu_AIS.sqlite')

debug = False

def load_port_data_to_db(port_data_fname: str, ais_database_fname: str):
    """Load a file of data in Port Houston format to the DB"""
    connection = sqlite3.connect(ais_database_fname)
    cursor = connection.cursor()
    if debug:
        cursor.execute("DROP TABLE IF EXISTS uploaded_files")
        connection.commit()
        cursor.execute("""create table uploaded_files (filename    TEXT,
                                                       upload_date TEXT,
                                                       file_id     INTEGER not null constraint 
                                                                   uploaded_files_pk primary key
                                                      );""")
        connection.commit()
    cursor.execute("SELECT * FROM uploaded_files WHERE filename=?", (port_data_fname,))
    rows = cursor.fetchall()
    print(rows)
    if len(rows) > 0:
        print(f'load_port_data_to_db: file {port_data_fname} already loaded on {rows[0][1]}')
        return
    else:
        cursor.execute("INSERT INTO uploaded_files (filename, upload_date, file_id) VALUES (?, ?, ?)",
                       (port_data_fname, datetime.datetime.now(), None))
        connection.commit()
        cursor.execute("SELECT last_insert_rowid()")
        rows = cursor.fetchall()
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
    df.to_sql(name='ais_data', con=connection, if_exists='append', index=False)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    load_port_data_to_db('202506-0.csv', ais_database)
