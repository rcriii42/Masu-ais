"""Collect mmsi numbers for dredges

Vessel names are all caps and match those in the AIS data"""
mmsi_from_name = {'RB WEEKS': 368349000,
                  'MAGDALEN': 369305000}

name_from_mmsi = dict([(v, k) for k, v in mmsi_from_name.items()])
