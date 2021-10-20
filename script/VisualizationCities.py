# -*- coding: utf-8 -*-
"""
Visualization of cities 

@author: Héctor Maravillo
@date:   Oct 2021
"""

# ---------------------- #
# IMPORT LIBRARIES
import geopandas as gpd          # Library to analyze and manipuated gesopatial data
import os                        # Library to interacting with the operating system (manage file paths)
import matplotlib.pyplot as plt  # Library for graph generation 


# ---------------------- #
# DEFINE GLOBAL VARIABLES

# Define projection 
# https://epsg.io/
# EPSG = 6372   (Mexico ITRF2008)
projection                      = 6372


# ---------------------- #
# DEFINING FUNCTIONS

def GraphState(number_state):
    """
    Graph the elements of the National Urban System 2018 (SUN-2018) and 
    the Natural City System 2020 (NCS-2020) for the selected state. 
    
    Parameters:
        number_state   -   (string): Key of the selected state ("01" to "32") 
    """
       
    state_selected             = states_polygons[states_polygons["CVE_ENT"] == number_state]
    municipalities_selected    = municipalities_polygons[municipalities_polygons["CVE_ENT"] == number_state]
    natural_city_selected      = gpd.overlay(natural_city_system, state_selected, how = 'intersection')
    sun2018_selected           = gpd.overlay(sun2018_grouped, state_selected, how = 'intersection')
    
    name_state_selected        = state_selected.iloc[0,2].replace(" ", "_")
    
    fig, ax = plt.subplots(1,1, figsize = (30,30), dpi = 300)
    state_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 3)
    sun2018_selected.plot(ax = ax, color = 'green', alpha = 0.6, edgecolor = "darkgreen", linewidth = 5)
    municipalities_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 0.5, linestyle = 'dotted')
    natural_city_selected.plot(ax = ax, color = 'blue', edgecolor = "darkblue", linewidth = 5)
    #ax.axis('off')
    #plt.savefig("State_"+name_state_selected+".png", bbox_inches = 'tight')
 
    
# ---------------------- #
# DATA LOAD 
# Set path to proyect
# (Change the path according to the location where you save the project)
os.chdir("C:\\Users\\4PF42LA_1909\\Phyton\\NaturalCities_Mexico")

# Load municipal and state limits, and assign projection
os.chdir("../NaturalCities_Mexico/data")
municipalities_polygons    = gpd.read_file("MGN2020_Municipalities.gpkg")
municipalities_polygons.to_crs(epsg = projection, inplace = True)
states_polygons            = gpd.read_file("MGN2020_States.gpkg")
states_polygons.to_crs(epsg = projection, inplace = True)


# Load processed data  (localities, natural cities and SUN-2018)
os.chdir("..")
os.chdir("../NaturalCities_Mexico/output")
localities                 = gpd.read_file("Localities_data2020.gpkg")
natural_city_system        = gpd.read_file("NaturalCitySystem.gpkg")
sun2018_grouped            = gpd.read_file("SUN2018_data.gpkg")


# ---------------------- #
# GRAPH MAPS

# Set path to output
# (Change the path according to the location where you save the project)
os.chdir("../output/Maps")

# Graph SUN-2018 and Natural City System (national level)
#  SUN-2018              -- Color green
#  Natural City System   -- Color blue
#  State boundaries      -- Line black
fig, ax = plt.subplots(1,1, figsize = (30,30), dpi = 300)
states_polygons.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 2)
sun2018_grouped.plot(ax = ax, color = 'green', alpha = 0.6, edgecolor = "darkgreen", linewidth = 3)
natural_city_system.plot(ax = ax, color = 'blue', edgecolor = "darkblue", linewidth = 2)
#ax.axis('off')
plt.savefig("Cities.png", bbox_inches = 'tight')


# Graph  SUN-2018 and Natural City System 2020 (state level)
number_states      = ["01","02","03","04","05","06","07","08","09",
                     "10","11","12","13","14","15","16","17","18","19",
                     "20","21","22","23","24","25","26","27","28","29",
                     "30","31","32"]

for i in number_states:
    GraphState(i)