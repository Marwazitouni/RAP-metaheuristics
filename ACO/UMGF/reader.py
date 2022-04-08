from Component import Component
from SubSystem import SubSystem
import pandas as pd
#from decimal import *

"""
    This File contains two functions used to read the input files (txt,xls files),
    we used Decimal for precision purpous
"""

def read_instance(path):
    """
        Read instance from text file
    """
    f = open(path,"r")
    lines = f.readlines()
    nb_line=1
    nb_sub_system = int(lines[nb_line].split(" ")[1])
    nb_line += 1
    subsystems = []
    """
        Reading the subsystems
    """
    #print("NB_SUBSYSTEMS : " + str(nb_sub_system))
    for i in range(nb_sub_system): # For each Sub system
        nb_components = int(lines[nb_line].split(" ")[2])
        nb_line += 1
        components = []
        #print("SUBSYSTEM " + str(i) + " NB_Components : " + str(nb_components))
        for j in range(nb_components): # For Each Component
            nb_state = int(lines[nb_line].split(" ")[2])
            nb_line += 1
            states = []
            #print("SUBSYSTEM " + str(i) + " Component : " + str(j) + " NB_States : " + str(nb_state))
            for k in range(nb_state):
                proba, capacity = lines[nb_line].replace("\n","").split(" ")
                states.append((float(proba),float(capacity)))
                nb_line += 1
            #print("States : " + str(states))
            component = Component(id=j,nb_states=nb_state,states=states)
            components.append(component)
        subsystem = SubSystem(id=i,nb_components=nb_components,components=components)
        subsystems.append(subsystem)
    """
        Reading the LOLP
    """
    LOLP = []
    nb_line += 1
    nb_loads = int(lines[nb_line].split(" ")[1])
    for l in range(nb_loads):
        nb_line += 1
        load, qs = lines[nb_line].replace("\n","").split(" ")
        LOLP.append((float(load),float(qs)))
    
    return subsystems, LOLP

def read_excel(path,precision):
    """
        Read instance from excel file with precision
    """
    system_df = pd.read_excel(path, sheet_name='System' , index_col=[0,1])
    demands_df = pd.read_excel(path, sheet_name='Loads')
    system_df.Availability = system_df.Availability.apply(lambda x: round(x,4))
    subsystems = []
    for subsystem, new_df in system_df.groupby(level=0):
        nb_units = 0
        components = []
        for unit, unit_df in new_df.groupby(level=1):
            nb_state = len(unit_df) + 1
            states = [tuple(x) for x in unit_df[["Availability","Capacity"]].to_records(index=False)]
            states.append((round(1 - unit_df["Availability"].sum(),4),0))
            component = Component(id=unit,nb_states=nb_state,states=states)
            components.append(component)
            nb_units += 1
        subsystem = SubSystem(id=subsystem,nb_components=nb_units,components=components)
        subsystems.append(subsystem)
    LOLP = []
    max_lolp = demands_df["Load"].max()
    #sum_duration = demands_df["Duration"].sum()
    sum_duration = 8760
    for i,row in demands_df.iterrows():
        tuple_lolp = (float(row["Load"]),round(float(100*row["Duration"]/sum_duration),4))
        LOLP.append(tuple_lolp)
    return subsystems,LOLP, max_lolp
