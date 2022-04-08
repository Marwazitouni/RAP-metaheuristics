
from UMGF.Component import Component
from UMGF.SubSystem import SubSystem
import pandas as pd

def read_excel(path,precision):
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
            cost = round(unit_df["Cost"][0],4)
            component = Component(id=unit,nb_states=nb_state,states=states,cost=cost)
            components.append(component)
            nb_units += 1
        subsystem = SubSystem(id=subsystem,nb_components=nb_units,components=components)
        subsystems.append(subsystem)
    LOLP = []
    max_lolp = demands_df["Load"].max()
    #sum_duration = demands_df["Duration"].sum()
    sum_duration = 8760
    for i,row in demands_df.iterrows():
        tuple_lolp = (float(row["Load"]),round(float(100*row["Duration"]/sum_duration),3))
        LOLP.append(tuple_lolp)
    return subsystems,LOLP, max_lolp
