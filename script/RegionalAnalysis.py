# -*- coding: utf-8 -*-
"""
Regional analysis of city size distribution 

@author: Héctor Maravillo
@date:   Oct 2021
"""

# ---------------------- #
# IMPORT LIBRARIES

import geopandas as gpd          # Library to analyze and manipuated gesopatial data
import os                        # Library to interacting with the operating system (manage file paths)
import numpy as np               # Library to scientific computing
import powerlaw                  # Library to statistical analysis of heavy-tailed distributions 
from tqdm import tqdm            # Library to view process progress 
import csv                       # Library to manipulate CSV files 
import matplotlib.pyplot as plt  # Library for graph generation 


# ---------------------- #
# DEFINE GLOBAL VARIABLES

# Define projection 
# https://epsg.io/
# EPSG = 6372   (Mexico ITRF2008)
projection                      = 6372

#Set number of iterations of the hypothesis test 
it = 1


# ---------------------- #
# DEFINING FUNCTIONS

def Statistical_Summary(data, variable):
    """
    Calculates descriptive statistical measures of the size of cities 
    
    Parameters:
        data            --  (DataFram) Empirical Data
        variable        --  (String) Name of the variable to evaluate    
        
    Return:
        results         -- (Dictionary) Set of statistical measures of the data 
    """
    results                      = {}
    results["Area"]              = data.geometry.area.sum()/(1000**2)
    
    df = data[variable]

    results["Variable"]          = variable
    results["Number_Elements"]   = len(df)
    results["Total_Population"]  = df.sum()
    results["Maximum"]           = df.max()
    results["Minimum"]           = df.min()
    results["Mean"]              = df.mean().round()
    results["Standar_Deviation"] = df.std().round()
    
    return results

def StatisticalAnalysis_PowerLaw (data, it, variable = "POBTOT", test = True):
    """
    Statistical analysis of the power law in the size distribution.
    It follows the proposal of Clauset et al. (2009).
    Uses the Python powerlaw library created by Alstott et al. (2014) 
    
    Parameters:
        data            --  (DataFrame) Empirical Data
        it              --  (integer) Number of iterations in the hypothesis test 
        variable        --  (String) Name of the variable to evaluate    
        test            --  (Boolean) Perform the hypothesis test (True) or not (False) 
        
    Return:
        results         -- (Dictionary) Set of statistical measures of the power law model fit    
    """

    df           = data[variable]
    
    # Fit a (discrete) power law model for the empirical data using the "powerlaw" library 
    fit          = powerlaw.Fit(df, discrete = True, estimate_discrete  =True)                        
    ks_distance  = fit.D                                                        # Kolmogorov-Smirnov distance
    tail         = df[df < fit.xmin]                                          # Data less than the estimated xmin 
    n_1          = len(tail)                                                    # Amount of data less than x_min 
    n_2          = len(df) - n_1                                                # Amount of data greater than or equal to x_min 
    tail.index   = range(0, n_1)                                                 
    
    # Hypothesis testing on the plausibility of the power law fit
    p            = 0
    if test      == True:
        for j in tqdm(range(it)):
            simulated_powerlaw  = fit.power_law.generate_random(n_2, estimate_discrete=True)            # Simulates synthetic data that follows a power law with the same parameters of the empirical data (with x> = xmin) 
            simulated_tail      = [tail[i] for i in np.random.randint(0, n_1, (n_1))]                   # Randomly extract a sample from the empirical data (x <xmin) 
            simulated_data      = np.concatenate((simulated_tail, simulated_powerlaw))                  # Join the two synthetic data samples                          
            fit_simulated       = powerlaw.Fit(simulated_data, discrete=True, estimate_discrete=True)   # Fit the power law on the synthetic sample 
            if fit_simulated.power_law.D > ks_distance:
                p               = p + 1                                                                            # Count the number of times the synthetic sample has a worse fit (in terms of the KS distance) than the empirical data.       
    p_value      = p / it
    
    r_lognormal, p_lognormal    = fit.distribution_compare('power_law', 'lognormal', normalized_ratio = True)  # Perform the Likelihood Ratio Test to compare the power law fit with the lognormal distribution 
    
    return {"xmin": fit.xmin, "alpha": fit.alpha-1, "sigma": fit.sigma,"k-s distance": ks_distance, "p-value": p_value, "test iterations": it,  "p-lognromal": p_lognormal, "r_lognormal": r_lognormal}

def VisualizationDistribution(data, color, ax, nombre, above_xmin = True):
    """
    Graphing the complementary cumulative distribution function of the empirical data and its power law fit 
    
    Parameters:
        data        --  (DataFrame) Empirical data
        color       --  (String) Line color
        ax          --  (axes) Plot axis
        nombre      --  (String) Name of the territorial unit 
    """
    
    fit = powerlaw.Fit(data, discrete = True, estimate_discrete  =True)          # Fit power law to empirical data                   

    if above_xmin == True:
        fit.plot_ccdf(color = color, linestyle = '-', ax = ax, label = nombre)   # Graph complementary cumulative distribution function of empirical data (> = xmin) 
    else:
        powerlaw.plot_ccdf(data, color=color, ax=ax, label = nombre)                             # Graph complementary cumulative distribution function of empirical data (> = xmin)  
    fit.power_law.plot_ccdf(color = color, linestyle = 'dotted', ax = ax)        # Graph complementary cumulative distribution function of power law fit 

def RegionalPartition_States(regions_dictionary):
    """
    Partition states by region
    
    Paramters:
        regions_dictionary  -- (dictionary) Keys are the names of the regions. The values are the list of states by region. 
        
    Return:
        state_partition   --  (dictionary) Key are the names of the regions, and the values are the GeoDataFrame of each region. 
    """
    state_partition         = {}
    regions_items     = regions_dictionary.items()
    
    for name_regions, state_list in regions_items:
        state_partition[name_regions] = states_polygons[states_polygons["CVE_ENT"].isin(state_list)]

    return state_partition

def RegionalPartition_data(data, state_partition):
    """
    Partition empirical data by region 
    
    Paramters: 
        data   --  (GeoDataFrame): Empirical data
        state_partition  --  (dictionary): Key are the names of the regions, and the values are the GeoDataFrame of each region. 
        
    Return:
        regions  -- (dictionary): Key are the names of the regions, and the values are the GeoDataFrame of empirical data of each region. 
    """
    region_partition    = {}
    
    for name_regions, states_regions in state_partition.items():
        region_partition[name_regions] =  gpd.overlay(data, states_regions, how = 'intersection')
        
    return region_partition

def RegionalAnalysis(data_regional_partition, variable = "POBTOT"):
    """ 
    Performs the statistical analysis of the power law (Clauset 2009) 
    for the data of each region 
    
    Paramters:
        data -- (GeoDataFrame)  Empirical data
        regional_partition  -- (dictionary) Key are the names of the regions, and the values are the GeoDataFrame of empirical data of each region. 
        variable  --  (string) Name of the variable to evaluate   
        
    Return:
        
    """
    regions_analysis_powerlaw                     = {}
    
    for name_regions, data_regions in data_regional_partition.items():
        regions_analysis_powerlaw[name_regions]   = StatisticalAnalysis_PowerLaw(data_regions, it, variable = variable)

    return regions_analysis_powerlaw

# ---------------------- #
# DATA LOAD 

# Set path to data
# (Change the path according to the location where you save the project)
os.chdir("C:\\Users\\4PF42LA_1909\\Phyton\\NaturalCities_Mexico")

os.chdir("../NaturalCities_Mexico/data")
# Load processed data of localities, natural cities and SUN2018
states_polygons            = gpd.read_file("MGN2020_States.gpkg")
states_polygons.to_crs(epsg = projection, inplace = True)

os.chdir("..")
os.chdir("../NaturalCities_Mexico/output")
# Load processed data of localities, natural cities and SUN2018
localities_data          = gpd.read_file("Localities_data2020.gpkg")
natural_cities_data      = gpd.read_file("NaturalCities_data2020.gpkg")
sun2018_data             = gpd.read_file("SUN2018_data.gpkg")


# ---------------------- #
# DEFINE REGIONS

# Proposed regionalization in Perez-Campuzano (2015)
regions_dictionary = { 
        "northern": ["02", "03", "05", "08", "10", "19", "25", "26", "28" ], 
        "south"   : [ "04", "07", "12", "20", "23", "27", "31"],
        "center"  : ["01", "06", "09", "11", "13", "14", "15", "16", "17", "18", "21", "22", "24", "29", "30", "32"]    
        }

# Partition state boundaries 
state_partition           = RegionalPartition_States(regions_dictionary)

# Partition data of cities in regions
localities_regions        = RegionalPartition_data(localities_data, state_partition)
natural_cities_regions    = RegionalPartition_data(natural_cities_data, state_partition)
sun2018_regions           = RegionalPartition_data(sun2018_data, state_partition)


# ---------------------- #
# STATISTICAL ANALYSIS OF THE POWER LAW 

#Perform power law analysis 
localities_regional_powerlaw     = RegionalAnalysis(localities_regions)
natural_cities_regional_powerlaw = RegionalAnalysis(natural_cities_regions)
sun2018_regional_powerlaw        = RegionalAnalysis(sun2018_regions, "POB_2018")



