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
    shapefile_path = out_folder_path / f'{layer}_{discover_args["zoom"]}-{discover_args["minzoom"]}_{now}.shp'

    print(f'Saving to {shapefile_path}...')
    out_folder_path.mkdir(exist_ok=True)
    utah_only.to_file(shapefile_path)


if __name__ == '__main__':

    #: Zoom: output scale (15 = ~1km squares)
    #: minzoom: Only report usage from this scale and lower (ie, minzoom=18 returns data for levels 18, 19, & 20).
    #: Prefix: The first few characters in a Bing quadkey, where each place in the number represents a deeper zoom
    #:      level (ie, 021 is tile 1 of tile 2 of tile 0)
    #:      https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system
    #:      We need 02, because the state is split by 021 and 023, and it doesn't look like you can send multiples
    discover_args = {'zoom': 15, 'minzoom': 18}
    layer = 'utah'
    out_folder_path = Path(r'c:\temp\discover_heatmaps')
    discover_login_user = ''  #: set this to your Discover admin user name
    if layer == 'all':
        base_url = 'https://discover.agrc.utah.gov/heatmap/api'
    else:
        base_url = f'https://discover.agrc.utah.gov/heatmap/api/{layer}'

    get_heatmap(discover_login_user, base_url, discover_args, out_folder_path, layer)
