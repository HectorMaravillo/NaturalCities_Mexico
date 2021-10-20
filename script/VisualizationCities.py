# -*- coding: utf-8 -*-
"""
Visualization of cities 

@author: Héctor Maravillo
@date:   Oct 2021

NOTE: it is recommended to run the code in blocks to avoid memory overflow. 
"""

# ---------------------- #
# IMPORT LIBRARIES
import geopandas as gpd                              # Library to analyze and manipuated gesopatial data
import os                                            # Library to interacting with the operating system (manage file paths)
import matplotlib.pyplot as plt                      # Library for graph generation 
from matplotlib_scalebar.scalebar import ScaleBar    # Function to create scale bar on maps 


# ---------------------- #
# DEFINE GLOBAL VARIABLES

# Define projection 
# https://epsg.io/
# EPSG = 6372   (Mexico ITRF2008)
projection                      = 6372

# Define font of scale bar
font      = {"family": "times new roman", "style": "italic","size": 38}



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
    
    fig, ax = plt.subplots(1,1, figsize = (30,30), dpi = 250)
    state_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 3)
    sun2018_selected.plot(ax = ax, color = 'green', alpha = 0.6, edgecolor = "darkgreen", linewidth = 5)
    municipalities_selected.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 1, linestyle = 'dotted')
    natural_city_selected.plot(ax = ax, color = 'blue', edgecolor = "darkblue", linewidth = 5)
    scale_bar = ScaleBar(1, dimension = "si-length", units = "m", length_fraction = 0.25,
                         location = "lower left", font_properties = font)
    ax.add_artist(scale_bar)
    ax.axis('off')
    plt.savefig("State_"+name_state_selected+".png", bbox_inches = 'tight')
    plt.close(fig)
    
    del state_selected, municipalities_selected, natural_city_selected, sun2018_selected, ax, fig
 

def Graph_MetropolitanArea(number_sun):
    """
    Graph a Metropolitan Arean of the National Urban System 2018 (SUN-2018), 
    the Natural City System 2020 (NCS-2020) and localities
    
    Parameters:
        number_sun   -   (string): Key of the SUN selected 
    """
     
    sun2018_selected           = sun2018_grouped[sun2018_grouped["CVE_SUN"] == number_sun]
    bounds                     = sun2018_selected.bounds

    name_metropolitan_areas    = metropolitan_areas[number_sun].replace(" ", "_")

    fig, ax = plt.subplots(1,1, figsize = (30,30), dpi = 250)
    ax.set(xlim=(float(bounds.minx), float(bounds.maxx)), ylim=(float(bounds.miny), float(bounds.maxy)))
    states_polygons.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 10)
    sun2018_selected.plot(ax = ax, color = 'green', alpha = 0.6)
    localities.plot(ax = ax, color = 'black', edgecolor ='black', linewidth = 2)
    natural_city_system.plot(ax = ax, color = 'blue', edgecolor = "darkblue",)
    municipalities_polygons.boundary.plot(ax = ax, edgecolor = 'black', linewidth = 2, linestyle = (0,(1,5)))
    scale_bar = ScaleBar(1, dimension = "si-length", units = "m", length_fraction = 0.25,
                         location = "lower left", font_properties = font)
    ax.add_artist(scale_bar)
    ax.axis('off')
    plt.savefig(number_sun+"_"+name_metropolitan_areas+".png", bbox_inches = 'tight')
    plt.close(fig)
    
    del sun2018_selected, fig, ax   
    
# ---------------------- #
# DATA LOAD 
# Set path to proyect
# (Change the path according to the location where you save the project)
os.chdir("C:\\Users\\4PF42LA_1909\\Phyton\\NaturalCities_Mexico")

# Load municipal and state limits, and assign projection
os.chdir("../NaturalCities_Mexico/data")
municipalities_polygons     = gpd.read_file("MGN2020_Municipalities.gpkg")
municipalities_polygons.set_crs(epsg = projection, inplace = True, allow_override=True)
states_polygons             = gpd.read_file("MGN2020_States.gpkg")
states_polygons.set_crs(epsg = projection, inplace = True, allow_override=True)
localities                 = gpd.read_file("MGN2020_Localities.gpkg")
localities.set_crs(epsg = projection, inplace = True, allow_override=True)

# Load processed data  (natural cities and SUN-2018)
os.chdir("..")
os.chdir("../NaturalCities_Mexico/output")
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
scale_bar = ScaleBar(1, dimension = "si-length", units = "m", length_fraction = 0.25,
                      location = "lower left", font_properties = font)
ax.add_artist(scale_bar)
ax.axis('off')
plt.savefig("Cities.png", bbox_inches = 'tight')
plt.close(fig)
del fig, ax

#%%%
# Graph  SUN-2018 and Natural City System 2020 (state level)
number_states      = ["01","02","03","04","05","06","07","08","09",
                     "10","11","12","13","14","15","16","17","18","19",
                     "20","21","22","23","24","25","26","27","28","29",
                     "30","31","32"]

#NOTE: Graphing is in parts to avoid memory overflow 
for i in number_states[0:10]:
    GraphState(i)
#%%
for i in number_states[10:20]:
    GraphState(i)
#%% 
for i in number_states[20:32]:
    GraphState(i)
    
#%%%   
# Graph SUN-2018 and Natural City System (metropolitan level)

# Set path to output
# (Change the path according to the location where you save the project)
os.chdir("../Maps/MetropolitanAreas")

metropolitan_areas = {
        "M09.01": "Valle de México",
        "M17.02": "Cuernavaca", "M17.01": "Cuautla",
        "M21.01": "Puebla-Tlaxcala", "M29.01": "Tlaxcala-Apizaco",
        "M15.02": "Toluca",
        "M13.01": "Pachuca", "M13.02": "Tula", "M13.03": "Tulancingo",
        "M02.03": "Tijuana", "M02.01": "Ensenada", "M02.02": "Mexicali",
        "M31.01": "Mérida",
        "M27.01": "Villahermosa",
        "M07.02": "Tuxtla Gutiérrez",
        "M20.01": "Oaxaca", "M20.02": "Tehuantepec",
        "M30.07": "Veracruz", "M30.04": "Minatitlán", "M30.03": "Córdoba", "M30.05": "Orizaba", "M30.08": "Xalapa", "M30.06": "Poza Rica",
        "M12.01": "Acapulco", "M12.02": "Chilpancingo",   
        "M16.02": "Morelia", "M16.01": "La Piedad-Pénjamo",
        "M22.01": "Querétaro",
        "M11.01": "Celaya",  "M11.03": "León",
        "M01.01": "Aguascalientes",
        "M24.02": "San Luis Potosí", "M24.01": "Rioverde",
        "M32.01": "Zacatecas-Guadalupe",
        "M04.01": "Campeche",
        "M23.02": "Chetumal", "M23.01": "Cancún",
        "M06.01": "Colima-Villa de Alvarez",
        "M18.01": "Tepic",
        "M14.01": "Guadalajara", "M14.03": "Puerto Vallarta",
        "M28.02": "Tampico",
        "M19.01": "Monterrey",
        "M05.04": "Saltillo", "M05.01": "La Laguna", "M05.02": "Monclova-Frontera",
        "M28.04": "Reynosa",
        "M10.01": "Durango",
        "M25.02": "Mazatlán", "M25.01": "Culiacán",
        "M08.01": "Chihuahua", "M08.04": "Juárez",
        "M03.01": "La Paz",
        "M26.02": "Hermosillo", "M26.01": "Guaymas",    
        }
 
names_metropolitan_areas  = list(metropolitan_areas.keys())

#NOTE: Graphing is in parts to avoid memory overflow    
for i in names_metropolitan_areas[0:10]:
    Graph_MetropolitanArea(i)
#%%%
for i in names_metropolitan_areas[10:20]:
    Graph_MetropolitanArea(i)
#%%%
for i in names_metropolitan_areas[20:30]:
    Graph_MetropolitanArea(i)
#%%%
for i in names_metropolitan_areas[30:40]:
    Graph_MetropolitanArea(i)
#%%%
for i in names_metropolitan_areas[40:50]:
    Graph_MetropolitanArea(i)
#%%%
for i in names_metropolitan_areas[50:55]:
    Graph_MetropolitanArea(i)

