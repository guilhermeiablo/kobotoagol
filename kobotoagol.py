# import requirements 
import requests
import re
import pandas as pd
import geopandas as gpd
from arcgis.gis import GIS
import os
import numpy as np
from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureSet, GeoAccessor
from arcgis.geometry import Geometry

#Import external files
neighborhoods = gpd.read_file('your_spatial_file.gpkg')


#Read this to know more about how Kobo handles synchronous exports and where to find the right url
#https://support.kobotoolbox.org/synchronous_exports.html

#### FETCH KOBO DATA

# Authentication credentials
username = os.getenv("KOBO_USER")
password = os.getenv("KOBO_PASSWORD")
export_token = os.getenv("KOBO_TOKEN")

#Debris Planning API endpoint
kobo_planning_url = "your Kobo synchronous export API endpoint"


def get_kobo_data(usr, pwd, token, url):

	# Create a session with authentication
	session = requests.Session()
	session.auth = (usr, pwd)

	# Construct the export URL
	kobo_export_url = f"{url}/data.xlsx?format=xlsx&token={token}"

	# Fetch data using the authenticated session
	response = session.get(kobo_export_url)

	# Check if the request was successful
	if response.status_code == 200:
	    # Load data into a pandas DataFrame
	    kobo_df = pd.read_excel(response.content)
	    return kobo_df
	else:
	    print("Error:", response.status_code)

kobo_data = get_kobo_data(username, password, export_token, kobo_planning_url)
kobo_mng_data = get_kobo_data(username, password, export_token, kobo_management_url)

#### INITIAL CLEANING

#Standardize data for municipalities without neighborhoods

def standardize(df):

    kobo_data_0 = df.replace(0, None)  
    return kobo_data_0

kobo_data = standardize(kobo_data)



#### MAKE IT GEOSPATIAL

#Set up the geodataframes and merge then

gdf_exploded = gaza_neighborhoods[['location_id','geometry']].merge(kobo_data, how='inner', left_on='location_id', right_on='location_id')

#Do whatever processing you need with geopandas


#### MAKE IT ARCGIS FRIENDLY

#Force number columns to behave as such
gdf_exploded['example'] = gdf_exploded['example'].astype(float)

#Handle columns so they are not modified by arcgis when uploaded
def makeArcGISfriendly(df):
    df.columns = df.columns.str.replace(r"[ ]", "_", regex=True)
    df.columns = df.columns.str.replace(r"[.]", "_", regex=True)
    df.columns = df.columns.str.replace(r"[?]", "_", regex=True)
    df.columns = df.columns.str.replace(r"[']", "", regex=True)
    df.columns = df.columns.str.replace(r"[(]", "", regex=True)
    df.columns = df.columns.str.replace(r"[)]", "", regex=True)
    df.columns = df.columns.str.replace(r"[[]", "", regex=True)
    df.columns = df.columns.str.replace(r"[]]", "", regex=True)
    df.columns = df.columns.str.replace(r"[%]", "_", regex=True)
    df.columns = map(str.lower, df.columns)
    
    # Remove leading underscores
    df = df.rename(columns={
        '_id':'f_id',
        '_uuid':'f_uuid',
    })
    df.columns = df.columns.str.lstrip('_')
    
    #Truncate and ensure uniqueness
    seen = {}
    final_cols = []
    max_length = 31
    for col in df.columns:
        base = col[:max_length]
        new_col = base
        i = 1
        while new_col in seen:
            suffix = f"_{i}"
            trim_len = max_length - len(suffix)
            new_col = base[:trim_len] + suffix
            i += 1
        seen[new_col] = True
        final_cols.append(new_col)
    
    # Step 4: Apply to DataFrame
    df.columns = final_cols
    return df

gdf_exploded = makeArcGISfriendly(gdf_exploded)

    
def simplifyGeometries(df):
    df['geometry'] = df['geometry'].centroid
    return df
    
gdf_exploded = simplifyGeometries(gdf_exploded)


seen = set()
unique_flags = []

for _, row in gdf_exploded.iterrows():
    if row['f_id'] in seen:
        unique_flags.append('')
    else:
        unique_flags.append('yes')
        seen.add(row['f_id'])

gdf_master['unique_'] = unique_flags

#Run locally and upload manually to ArcGIS the first time!
#gdf_exploded.to_file('exploded.gpkg')

#### UPDATE DATA IN ARCGIS

#Connect to the ArcGIS Enterprise portal

# Authentication credentials
arcgisuser = os.getenv("ARCGIS_USER")
arcgispwd = os.getenv("ARCGIS_PASSWORD")
arcgisportal = os.getenv("ARCGIS_PORTAL")


gis = GIS(arcgisportal, arcgisuser, arcgispwd)

# Access the feature-layer through its URL
file = 'Exploded'

def searchArcgis(keyword):
    search_result = gis.content.search("title:"+keyword, item_type = "Feature Layer")
    return search_result

search_file = searchArcgis(file)

def updateFeature(search_results, gdf):

    item = gis.content.get(search_results[0].id)

    flc = FeatureLayerCollection.fromitem(item)
    layer = flc.layers[0]  # Assuming you're working with the first layer


    # Step 1: Truncate features
    truncate_result = layer.manager.truncate()
    print("Truncate result:", truncate_result)

    # Keep only matching columns
    expected_fields = [f["name"] for f in layer.properties.fields if f["name"] != "fid"]
    gdf = gdf[[col for col in gdf.columns if col in expected_fields or col == "geometry"]]

    gdf = gdf.to_crs(epsg=4326)

    sedf = GeoAccessor.from_geodataframe(gdf)

    fs = FeatureSet.from_dataframe(sedf)

    result = layer.edit_features(adds=fs.features)
    print("Result:", result)
    return(result)

updateFeature(search_file, gdf_exploded)
