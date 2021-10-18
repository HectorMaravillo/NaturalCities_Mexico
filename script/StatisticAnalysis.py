# -*- coding: utf-8 -*-
"""
Statistical analysis of city size distribution 

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
    df = data[variable]
    
    results                      = {}
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

def Export_Dictionary(dictionary, name_file):
    """
    Export a dictionary to a CSV file 
    
    Parameters:
        dictionary  --  (Dictionary) Dictionary to export
        name_file   --  (string) Resulting file name 
    """
  
    with open(name_file+'.csv','w',newline='') as datos:
        almacenar = csv.writer(datos)
        almacenar.writerows(dictionary.items())

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
        powerlaw.plot_ccdf(data, color=color, ax=ax)                             # Graph complementary cumulative distribution function of empirical data (> = xmin)  
    fit.power_law.plot_ccdf(color = color, linestyle = 'dotted', ax = ax)        # Graph complementary cumulative distribution function of power law fit 

# ---------------------- #
# DATA LOAD 

# Set path to data
# (Change the path according to the location where you save the project)
os.chdir("../output")

# Load processed data of localities, natural cities and SUN2018
localities_data          = gpd.read_file("Localities_data2020.gpkg")
natural_cities_data      = gpd.read_file("NaturalCities_data2020.gpkg")
sun2018_data             = gpd.read_file("SUN2018_data.gpkg")


# Set path to output
# (Change the path according to the location where you save the project)
os.chdir("../output/StatisticAnalysis")

# ---------------------- #
# DESCRIPTIVE STATISTICS

# Statistical descriptive of the city size distribution 

localities_descriptive_statistics     = Statistical_Summary(localities_data, "POBTOT")
Export_Dictionary(localities_descriptive_statistics, "Localities_DescriptiveStatistics")

naturalcities_descriptive_statistics  = Statistical_Summary(natural_cities_data, "POBTOT")
Export_Dictionary(naturalcities_descriptive_statistics, "NaturalCities_DescriptiveStatistics")

sun2018_descriptive_statistics        = Statistical_Summary(sun2018_data, "POB_2018")
Export_Dictionary(sun2018_descriptive_statistics, "SUN2018_DescriptiveStatistics")


# ---------------------- #
# STATISTICAL ANALYSIS OF THE POWER LAW 
#Set number of iterations of the hypothesis test 
it = 1

#Perform power law analysis 
localities_anlysis_powerlaw          = StatisticalAnalysis_PowerLaw(localities_data, it)
Export_Dictionary(localities_anlysis_powerlaw, "Localities_PowerLaw")

naturalcities_anlysis_powerlaw       = StatisticalAnalysis_PowerLaw(natural_cities_data, it)
Export_Dictionary(naturalcities_anlysis_powerlaw, "NaturalCities_PowerLaw")

sun2018_anlysis_powerlaw             = StatisticalAnalysis_PowerLaw(sun2018_data, it, variable="POB_2018")
Export_Dictionary(sun2018_anlysis_powerlaw, "SUN2018_PowerLaw")


# ---------------------- #
# VISUALIZATION OF CITY SIZE DISTRIBUTION 

# Plot of the complementary cumulative distribution function (CCDF) 
fig, ax                  = plt.subplots(1,1, figsize=(10,10), dpi = 200)
VisualizationDistribution(localities_data["POBTOT"], "black", ax, "Localities")
VisualizationDistribution(natural_cities_data["POBTOT"], "blue", ax, "Natural Cities")
VisualizationDistribution(sun2018_data["POB_2018"], "green", ax, "SUN-2018")
ax.legend()
plt.savefig("CCDF_above_xmin.png", bbox_inches='tight')

# Plot of the complementary cumulative distribution function (CCDF) 
fig, ax                  = plt.subplots(1,1, figsize=(10,10), dpi = 200)
VisualizationDistribution(localities_data["POBTOT"], "black", ax, "Localities", False)
VisualizationDistribution(natural_cities_data["POBTOT"], "blue", ax, "Natural Cities", False)
VisualizationDistribution(sun2018_data["POB_2018"], "green", ax, "SUN-2018", False)
ax.legend()
plt.savefig("CCDF_full_sample.png", bbox_inches='tight')


# ---------------------- #
# EXPORT PROCESSED GEOGRAPHIC DATA 
# Set path to output
# (Change the path according to the location where you save the project)
os.chdir("..")

# Create Natural City System using xmin estimation 
natural_city_system      = natural_cities_data[natural_cities_data["POBTOT"] > naturalcities_anlysis_powerlaw["xmin"]]

# Export data 
natural_city_system.to_file("NaturalCitySystem.gpkg", driver='GPKG')



