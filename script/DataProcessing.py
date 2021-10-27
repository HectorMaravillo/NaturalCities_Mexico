# -*- coding: utf-8 -*-
"""
Data processing 

@author: Héctor Maravillo
@date:   Oct 2021
"""

# ---------------------- #
# IMPORT LIBRARIES
import pandas as pd              # Library to analyze and manipulate data
import geopandas as gpd          # Library to analyze and manipuated gesopatial data
import os                        # Library to interacting with the operating system (manage file paths)


# ---------------------- #
# DEFINE GLOBAL VARIABLES

# Define projection 
# https://epsg.io/
# EPSG = 6372   (Mexico ITRF2008)
projection                      = 6372


# ---------------------- #
# DEFINING FUNCTIONS

def CCA_by_ConvexEnvelopIntersections(data_polygons, key, projection):
    """
    Group locality data using the City CLustering Algorithm by Convex Envelop Intersections
    
    Parameters:
        data_polygons  --  (GeoDataFrame) Polygons of the empirical data 
        key            --  (String)       Data identifier
        projection     -- (Integer)       Coordinate Reference Systems
        
    Return:
        natural_cities -- (GeoDataFrame)  Returns the polygons of the natural cities (the union of the intersected convex envelopes) 
        data_grouped   -- (GeoDataFrame)  Returns the polygons of the original data grouped according to their containment in a natural city. 
    """
    
    # Build convex envelope from polygons
    geometry_convexhull                = gpd.GeoDataFrame()            
    geometry_convexhull["geometry"]    = data_polygons.convex_hull
    
    # Groups the convex envelopes that intersect and create and index
    data_convexhull                    = gpd.GeoDataFrame()
    data_convexhull["geometry"]        = geometry_convexhull.unary_union.geoms    # Dissolves the Polygons into a MultiPolygon (joining the intersected polygons) and extracts the individual Polygons from the multipolygon 
    data_convexhull.set_crs(epsg = projection, inplace = True)
    data_convexhull["id_convex"]       = data_convexhull.index+1                  # Create an index
    
    # Create a GeoDataFrame with the centroids and key of the original data
    data_centroid                      = gpd.GeoDataFrame()
    data_centroid['geometry']          = data_polygons.centroid
    data_centroid.set_crs(epsg = projection, inplace = True)
    data_centroid[key]                 = data_polygons[key]
    
    # Assigns the index of the grouped convex envelopes to the original data through the centroids  
    data_centroid                      = gpd.sjoin(left_df = data_centroid, right_df = data_convexhull, how = 'left', predicate = 'within')
    data_centroid.drop(['index_right', 'geometry'], axis = 1, inplace = True)
    data_grouped                       = pd.merge(left = data_polygons, right = data_centroid, how='left', left_on=key, right_on=key)
   
    # Groups the original polygons using the grouped convex envelope index 
    data_grouped                       = data_grouped.dissolve(by='id_convex', aggfunc='sum')
   
    # Assign the sum of the population to the grouped convex unions. 
    data_convexhull                    = pd.merge(left = data_convexhull, right = data_grouped, how = 'left', left_on = 'id_convex', right_on = 'id_convex', suffixes = (None, "_y"))
    data_convexhull                    = data_convexhull.drop(["geometry_y"], axis = 1)
    
    return data_convexhull, data_grouped


# ---------------------- #
# DATA LOAD 

# Set path to proyect
# (Change the path according to the location where you save the project)
os.chdir("C:\\Users\\4PF42LA_1909\\Phyton\\NaturalCities_Mexico")
os.chdir("../NaturalCities_Mexico/data")

# Load the polygons (and multipolygon) of localities in Mexico (National Geostatistical Framework 2020)
localities_polygons             = gpd.read_file("MGN2020_Localities.gpkg")

# Load the polygons and data of the National Urban System 2018
sun2018                         = gpd.read_file("SUN2018.gpkg").to_crs(epsg = projection)

# Load data from the 2020 Population and Housing Census of localities 
localities_census2020           = pd.read_csv("CPyV2020_Localidades.csv")


# ---------------------- #
# DATA PRE-PROCESSING

# Filter the data corresponding to inhabited localities
localities_census2020           = localities_census2020[localities_census2020["LOC"]>0]
localities_census2020           = localities_census2020[localities_census2020["LOC"]<9998]
localities_census2020           = localities_census2020[localities_census2020["POBTOT"]>0]
localities_census2020["CVEGEO"] = localities_census2020["ENTIDAD"].apply("{0:0=2d}".format)+localities_census2020["MUN"].apply("{0:0=3d}".format)+localities_census2020["LOC"].apply("{0:0=4d}".format)
localities_census2020           = localities_census2020[["CVEGEO", "POBTOT", "VIVTOT", "TVIVHAB"]]

# Join the census data and the polygons of the localities 
localities                      = pd.merge(left = localities_polygons, right = localities_census2020, how='left', left_on='CVEGEO', right_on='CVEGEO')
localities                      = localities[["geometry", "CVEGEO", "POBTOT", "VIVTOT", "TVIVHAB"]]
localities                      = localities[localities["POBTOT"]>0]
del localities_polygons, localities_census2020

# Assign projection 
localities.set_crs(epsg = projection, inplace = True, allow_override=True)

# Group of cities according to SUN-2018
sun2018["POB_2018"]             = sun2018["POB_2018"].round()
sun2018                         = sun2018.dissolve(by='CVE_SUN', aggfunc='sum')

# Group localities using the CCA-CEI
natural_cities, localities_grouped              = CCA_by_ConvexEnvelopIntersections(localities, "CVEGEO", projection)

# ---------------------- #
# EXPORT PROCESSED GEOGRAPHIC DATA 

# Set path to output
# (Change the path according to the location where you save the project)
os.chdir("../NaturalCities_Mexico/output")

# Export data 
localities.to_file("Localities_data2020.gpkg", driver='GPKG')
localities_grouped.to_file("LocalitiesGrouped_data2020.gpkg", driver='GPKG')
natural_cities.to_file("NaturalCities_data2020.gpkg", driver='GPKG')
sun2018.to_file("SUN2018_data.gpkg", driver='GPKG')

