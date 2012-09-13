""" This code creates artificial community matrices for analysis """
# Import modules
from __future__ import division
from scipy import stats
import scipy as sp
import numpy as np
import csv
import math
import random 
import sqlite3 as dbapi
import string

""" Set up database capabilities """
# Set up ability to query data
con = dbapi.connect('SimulatedData.sqlite')
cur = con.cursor()

# Switch con data type to string
con.text_factory = str

""" Create database for simulated data """
cur.execute("""DROP TABLE IF EXISTS Simulated_Data""")
con.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Simulated_Data
                (list_num INTEGER,
                site_num INTEGER,
                sp_code INTEGER)""")


""" Write outputs to .csv file """
def output_sites(distribution, method, output_number, results, file_prefix):
    filename = file_prefix + distribution + method + "_site_" + str(output_number) + ".csv"
    output_file = open(filename, "wb")
    datawriter = csv.writer(output_file)
    datawriter.writerow(['Site', 'Sp_ID', 'Abundance'])
    datawriter.writerows(results)
    output_file.close()
    return filename
    
""" Assigns upper and lower probability bounds to species based on veiling of the distribution"""
def species_assign(veil_line, metacommunity_species, veil_side):
    species_assignment = []
    
    if veil_side == "left":
        upper_bound = 1
        
    else:
        upper_bound = 1 - veil_line
    
    percent_remaining = 1 - veil_line
    species_fraction = percent_remaining * (1/(metacommunity_species))
    
    while metacommunity_species > 1:        
        lower_bound = upper_bound - species_fraction

        species_assignment = species_assignment + [[metacommunity_species, lower_bound, upper_bound]]
                
        upper_bound = lower_bound
        metacommunity_species -= 1
    
    species_assignment = species_assignment + [[metacommunity_species, veil_line, upper_bound]]
        
    return species_assignment

""" Create lists of random integers """
def random_integers(min_val, max_val, list_size):
    new_list = []
    
    while list_size > 0:
        number = random.randint(min_val, max_val)
        new_list = new_list + [number]
        list_size -= 1
    return new_list

""" Assign species identity based on distribution probabilities """
def species_ID(species_assignment, distribution_probability):
    species_ID = 0
    for species in species_assignment:
        if distribution_probability >= species[1] <= species[2]:
            if species_ID == 0:
                species_ID = species[0]
            else:
                species_ID = species_ID
            
        else:
            species_ID = species_ID

    return species_ID   
       

""" Log-normal function """
# species_assignment: list containing assigned probability values for species pool
# parameter: list containing species richness parameters or total abundance parameters for each site
def lognormal(species_assignment):
    species = sp.stats.lognorm.rvs(1, loc=0, scale=1, size=1)
    species = sp.stats.lognorm.cdf(species, 1)
    species = species_ID(species_assignment, species)
              
    return species

""" Log-series function """
# species_assignment: list containing assigned probability values for species pool
def logseries(species_assignment):
    species = sp.stats.logser.rvs(0.6, loc=0, size=1)
    species = sp.stats.logser.cdf(species, 0.6, loc=0)
    species = species_ID(species_assignment, species)
                    
    return species


""" Create site """
# Distribution of the metacommunity: distribution
# Parameter used to set community(number of species or total number of individuals): value
# Species distribution values: species_list
# method: Method of stopping the community: species richness (richness) or total abundance (abundance)
# site_number: site ID
def site(distribution, method, species_list, value, site_number, output_number):
    site = [] # Create list of individual recorded at sites
 
    while value > 0:
        # Select random individual from distribution
        if distribution == "lognormal":
            species = lognormal(species_list)
        else:
            species = logseries(species_list)
            
        # After individual is selected, determine how to continue with sampling     
        if method == "abundance": # Sampling continues for a specified number of iterations
            if species == 0: # If the species ID is zero, do not decrease
                value = value
            else:
                value -= 1
        
        else: # If method == "richness" , sampling continues until the desired richness is obtained
            new_species = 1 # Assumes that every new individual will be a new species
            if species == 0: # If there the ID is zero, there is not a new species added
                new_species = 0
            else: # If species is a valid species ID, determine if the individual is of a new species
                for record in site: # Checks to see if species richness has increased
                    if species == record[1]: # If species ID matches one at the site, new_species is zero. 
                        new_species = 0 
                    else: # If the species ID does not match, the value of new_species does not change
                        new_species = new_species # New_species will equal one if the species has not been recorded.
                
            value = value - new_species 
        
        # Do not record if the species ID is zero
        if species == 0:
            site = site
        
        else:
            site = site + [[output_number, site_number, species]]
            
    # Insert data into Experiments table
    cur.executemany("""INSERT INTO Simulated_Data VALUES(?,?,?)""", site)
    con.commit()        
           
    return site


""" Create list of sites """
# Create list of sites
def site_list(distribution, method, species_list, site_value, output_number, min_number, max_number):
    sites_list = []
    site_number = 1
    while site_value > 0:
        value = random.randint(min_number, max_number)
        new_site = site(distribution, method, species_list, value, site_number, output_number)
        site_number += 1
        site_value -= 1
       
    return sites_list

""" Create multiple site lists """
def list_output(distribution, method, species_list, list_values, min_number, max_number):
    output_number = 1
    output_list = []
    for value in list_values:
        output = site_list(distribution, method, species_list, value, output_number, min_number, max_number)
        output_list = output_list + [output_number]
        output_number += 1
        
    return output_list   
        
     
""" Metacommunity parameter definitions """
# Distribution to draw from (lognormal, logseries): distribution
# Percent of distribution that is veiled: veil_line
# Side of the distribution that is veiled (left, right): veil_side
# Number of species in the metacommunity: species_pool

""" Matrix parameter definitions """
# Number of sites: num_sites
# Species richness(richness) or total community abundance(abundance) used to set simulation: simulation_method
# Minimum species richness or total community abundance: min_number
# Maximum species richness or total community abundance: max_number

""" Output file name """
# File name prefix: file_name
 

""" Set up metacommunity parameters """
veil_line = 0
veil_side = "left"
species_pool = 20
distribution = "lognormal"

""" Set up site parameters """
min_sites = 7
max_sites = 14
total_num_lists = 10
simulation_method = "richness"
min_number = 5
max_number = 20

""" Set up file name prefix """
file_name = "test"


# Assign portion of any distribution to species
species_assignment = species_assign(veil_line, species_pool, veil_side)

# Create list of possible site numbers per list
site_list_nums = random_integers(min_sites, max_sites, total_num_lists)

# Create database of simulated raw data
multiple_sites = list_output(distribution, simulation_method, species_assignment, site_list_nums, min_number, max_number)

for site in multiple_sites:
    sql_matrix = cur.execute("""SELECT site_num, sp_code, COUNT(sp_code) AS abundance FROM Simulated_Data
                   WHERE list_num == ?
                   GROUP BY site_num, sp_code""", [site])
       
    matrix = cur.fetchall()
        
    output_sites(distribution, simulation_method, site, matrix, file_name)
    
    
# Computer, end program.

    
    





