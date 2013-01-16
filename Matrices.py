# This script is designed to make matrices from the BBS and FIA datasets for nested subset analysis. Will be using incidence only.
# Database needs to be in the same folder location as this script.  Everything will run then.
# Import modules
from __future__ import division
import numpy as np
import sqlite3 as dbapi
import string
import csv
import math

# Import seed locations
def Data_array(input_file):
    data = open(input_file)
    datareader = csv.reader(data)
    array = []
    return array


# Clean data for conversion into matrices.  Note: this may have to be done separately for each dataset, but I will try it as a single function first.
def select_data(database, fields, table, good_site_field, good_site_code):
    # Set up ability to query data with SQL
    con = dbapi.connect(database)
    cur = con.cursor()
    
    # Switch con data type to string
    con.text_factory = str
    
    # Query for clean data and insert into array- this code is wrong, but it is the general idea, I think. I need to find out if you can substitute multiple values into a query like I am trying to do, and if so, what the proper syntax is. If I cannot do this, I need to get the clean data from each of these datasets separately.
    # This could also be done with multiple queries, and this would probably be the best way to do things, as it would be less general, but also easier to check for correctness.
    cur.execute("""SELECT DISTINCT (?, ?, ?) FROM (?)
                   WHERE (?) == (?);""" fields, table, good_site_field, good_site_code)
    
    clean_data = cur.fetchall()
    
    return clean_data

# Calculate Euclidean distances to seeds
def euclid_dist(route_data, seeds):
    # Select route data
    for index, route in enumerate (route_data):
        route_lat = route[1]  # Assuming that the data structure goes route_ID, lat, long
        route_long = route[2] # Assuming that the data structure goes route_ID, lat, long 
        distance = 0
       # For each route, calculate the Euclidean distance to each seed point 
        for index,row in enumerate(seeds):
            seed_lat = row[1] # Assuming that the data structure goes seed_ID, lat, long
            seed_long = row[2] # Assuming that the data structure goes seed_ID, lat, long
            
        
            # Calculate Euclidean distance for route points
            euclid = math.sqrt((route_lat-seed_lat)**2 + (route_long-seed_long)**2)
            
            # Compare distances for shortest distance
            if distance == 0:
                euclid = distance
                seed_id = row[0] # Assuming that the data structure goes seed_ID, lat, long
            
            else if euclid < distance:
                euclid = distance
                seed_id = row[0] # Assuming that the data structure goes seed_ID, lat, long
            
            # Add closest seed point and distance to data set
            route = route + [seed_id, distance]
             
    
    return route_data

# Write outputs to .csv file 
def csv_writer(filename, results):
    output_file = open(filename,  'wb')
    datawriter = csv.writer(output_file)
    datawriter.writerows(results)
    output_file.close()
    return filename


