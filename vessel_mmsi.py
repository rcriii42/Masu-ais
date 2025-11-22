"""Collect mmsi numbers for dredges

Vessel names are all caps and match those in the AIS data"""
mmsi_from_name = {'RB WEEKS': 368349000,
                  'MAGDALEN': 369305000}

name_from_mmsi_dict = dict([(v, k) for k, v in mmsi_from_name.items()])

def name_from_mmsi(mmsi: list[int] | int) -> str:
    """Return the vessel name(s) associated with the mmsi

    mmsi: A single or list of vessel numbers

    returns: The vessel name or a list of vessel names"""
    if isinstance(mmsi, list):
        return [name_from_mmsi_dict[m] for m in mmsi]
    else:
        return name_from_mmsi_dict[mmsi]
