# This script is designed to make matrices from the BBS and FIA datasets for nested subset analysis. Will be using incidence only.
# Database needs to be in the same folder location as this script.  Everything will run then.
# Import modules
from __future__ import division
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
    cur.execute("""SELECT DISTINCT (?, ?, ?) FROM (?)
                   WHERE (?) == (?);""" fields, table, good_site_field, good_site_code)
    
    clean_data = cur.fetchall()
    
    return clean_data

# Write outputs to .csv file 
def csv_writer(filename, results):
    output_file = open(filename,  'wb')
    datawriter = csv.writer(output_file)
    datawriter.writerows(results)
    output_file.close()
    return filename


