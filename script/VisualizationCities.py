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
# DEFINING FUNCTIONS

def GraphState(number_state):
    state_selected             = states_polygons[states_polygons["CVE_ENT"] == number_state]
    municipalities_selected    = municipalities_polygons[municipalities_polygons["CVE_ENT"] == number_state]
    natural_city_selected      = gpd.overlay(natural_city_system, state_selected, how = 'intersection')
    sun2018_selected           = gpd.overlay(sun2018_grouped, state_selected, how = 'intersection')
    
    name_state_selected        = state_selected.iloc[0,2].replace(" ", "_")
    
    fig, ax = plt.subplots(1,1, figsize = (30,30), dpi = 300)
    state_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 3)
    sun2018_selected.plot(ax = ax, color = 'green', alpha = 0.6, edgecolor = "darkgreen", linewidth = 5)
    municipalities_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 0.3, linestyle = 'dotted')
    natural_city_selected.plot(ax = ax, color = 'blue', edgecolor = "darkblue", linewidth = 5)
    ax.axis('off')
    plt.savefig("State_"+name_state_selected+".png", bbox_inches = 'tight')
 
    
# ---------------------- #
# Define projection 
# https://epsg.io/
# EPSG = 6372   (Mexico ITRF2008)
projection                      = 6372


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
ax.axis('off')
plt.savefig("Cities.png", bbox_inches = 'tight')


# Graph  SUN-2018 and Natural City System 2020 (state level)
#Select a state number to plot ("01" to "32")
print(states_polygons[["CVE_ENT", "NOMGEO"]])
GraphState("02")
GraphState("03")
GraphState("11")
GraphState("13")
GraphState("16")
GraphState("17")
GraphState("19")
GraphState("20")
GraphState("25")
GraphState("27")
GraphState("31")