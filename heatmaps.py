"""
Downloads heatmap data from Discover and exports to a shapefile in the specified folder.
"""
from datetime import datetime
from pathlib import Path
import getpass
import json

import geopandas as gpd
import psycopg2
import requests


def get_heatmap(user, base_url, discover_args, out_folder_path, layer):
    #: Open a session to stay authenticated
    #: TODO: Gracefully handle failed logins, errors when downloading data
    with requests.Session() as s:
        print('Logging in...')
        s.post('https://discover.agrc.utah.gov/login', data={'user': user, 'password': getpass.getpass()})
        print('Downloading data...')
        r = s.get(base_url, params=discover_args, timeout=None)
        r.raise_for_status()
        if 'login' in r.text:
            raise ValueError('Not Logged In')
        json_data = json.loads(r.text)

    #: Get the state boundary from Open SGID as a GeoDataFrame
    print('Getting State boundary from Open SGID...')
    opensgid = psycopg2.connect(database='opensgid', user='agrc', password='agrc', host='opensgid.agrc.utah.gov')
    sql = 'select * from opensgid.boundaries.state_boundary'
    state_boundary = gpd.GeoDataFrame.from_postgis(sql, opensgid, geom_col='shape')

    #: Convert heatmap to GeoDataFrame, clip to state boundary, save to shapefile
    print('Converting to GeoDataFrame...')
    full_response = gpd.GeoDataFrame.from_features(json_data['features'])
    full_response.set_crs(epsg=4326, inplace=True)
    full_response.to_crs(crs=state_boundary.crs, inplace=True)

    utah_only = gpd.clip(full_response, state_boundary[state_boundary['state'] == 'Utah'])

    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    shapefile_path = out_folder_path / f'{layer}_{discover_args["zoom"]}_{now}.shp'

    print(f'Saving to {shapefile_path}...')
    out_folder_path.mkdir(exist_ok=True)
    utah_only.to_file(shapefile_path)


if __name__ == '__main__':

    #: Zoom: output scale (15 = ~1km squares)
    #: minzoom: get requests at this level and lower (18 = 18, 19, 20)
    discover_args = {'zoom': 15, 'prefix': '02'}
    layer = 'utah'
    out_folder_path = Path(r'c:\temp\discover_heatmaps')
    discover_login_user = ''
    if layer == 'all':
        base_url = 'https://discover.agrc.utah.gov/heatmap/api'
    else:
        base_url = f'https://discover.agrc.utah.gov/heatmap/api/{layer}'

    get_heatmap(discover_login_user, base_url, discover_args, out_folder_path, layer)
