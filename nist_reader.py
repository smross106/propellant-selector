"""
Takes an input NIST file and a Propellant, and creates polynomials for all the relevant variables

"""
from numpy import polyfit, poly1d
import numpy as np
import os.path
import warnings

warnings.simplefilter('ignore', np.RankWarning)

POLY_DEG = 10

def get_prop_data(filename):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "prop-data/"+filename+".txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    file = open(abs_file_path,"r")
    all_data = file.read()

    all_data = all_data.split("\n")
    split_data = []
    for i in all_data:
        split_data.append(i.split("\t"))
    
    return(split_data[1:])

def get_combo_data(filename):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "combo-data/"+filename+".txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    file = open(abs_file_path,"r")
    all_data = file.read()

    all_data = all_data.split("\n")
    split_data = []
    for i in all_data:
        split_data.append(i.split("\t"))
    
    return(split_data[1:])

def get_fit(data,position,degree):
    temperatures = []
    values = []

    for row in data:
        if len(row)<=position:
            continue
        if row[0]=="undefined":
            continue
        if row[position]=="undefined":
            continue
        temperatures.append(float(row[0]))
        values.append(float(row[position]))

    if len(temperatures)==0:
        return(None)
    if degree>len(temperatures):
        coeffs = polyfit(temperatures,values,len(temperatures))
    else:
        coeffs = polyfit(temperatures,values,degree)

    polynom = poly1d(coeffs)

    return(polynom)

def propellant_data(propellant,filename):
    split_data = get_prop_data(filename)

    #values for position of each data type are hard coded and manually read from file
    propellant.F_pressure = get_fit(split_data,1,POLY_DEG)
    propellant.F_density_liquid = get_fit(split_data,2,POLY_DEG)

    propellant.F_density_vapour = get_fit(split_data,14,POLY_DEG)

def combo_data(propellant_mix, filename):
    split_data = get_combo_data(filename)

    data = []
    for row in split_data:
        if row[0]==propellant_mix.oxidiser_name and row[1]==propellant_mix.fuel_name:
            data = row
            break
    propellant_mix.ISP_sea_level = row[2]
    propellant_mix.chamber_temp = row[3]
    propellant_mix.exhaust_temp = row[4]