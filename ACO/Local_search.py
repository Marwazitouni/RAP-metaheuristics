import random

from UMGF.SubSystem import SubSystem
from UMGF.Component import Component
from UMGF.solver import *

def improve_cost(path,subsystems,LOLP,precision, C0, E0, gamma):
    
    path_subsystems = path_to_subsystems(path[0],subsystems)

    objective_0 , disp_0 , cost_0, capacity_0 = path[1]

    for i in range(len(path_subsystems)):
        sub = path_subsystems[i]
        for j in range(len(sub.components)):
            device = sub.components[j]
            if len(subsystems[i].components[device.id:]) > 0:
                cheaper_device = random.choice(subsystems[i].components[device.id:])
                path_subsystems[i].components[j] = cheaper_device
                disp , unsupplied, capacity = objective(path_subsystems,LOLP, precision)
                new_cost = cost_0 - (device.cost - cheaper_device.cost)
                new_objective = round(disp * ((C0 / new_cost) ** gamma) * ((capacity / E0) ** gamma),4)
        
                if new_objective > objective_0: # cost_0 - (device.cost - cheaper_device.cost) < C0   and (capacity > E0 or capacity > capacity_0):
                    disp_0 , cost_0, capacity_0 = disp, cost_0 - (device.cost - cheaper_device.cost), capacity
                else:
                    path_subsystems[i].components[j] = device
    
    improved_path = subsystems_to_path(path_subsystems, disp_0 , cost_0, capacity_0, C0, E0, gamma)
    return improved_path

def path_to_subsystems(path,subsystems):
    path_subsystems = []
    
    for i in range(len(subsystems)):
        subsystem = SubSystem(id = i + 1, nb_components= 0, components=[])
        path_subsystems.append(subsystem)

    for move in path:
        subsystem_i, device_id = move
        subsystem = subsystems[subsystem_i]

        if device_id < subsystem.nb_components: # Blank Node

            device_i = subsystem.components[device_id]

            path_subsystems[subsystem_i].components.append(device_i)
            path_subsystems[subsystem_i].nb_components += 1
    
    return path_subsystems

def subsystems_to_path(path_subsystems, disp , cost, capacity, C0, E0, gamma):
    
    moves = []
    
    for i in range(len(path_subsystems)):
        sub = path_subsystems[i]
        for j in range(len(sub.components)):
            device = sub.components[j]
            moves.append((i,device.id-1))
    
    objective = disp * ((C0 / cost) ** gamma) * ((capacity / E0) ** gamma)
    if cost > C0 or capacity < E0:
        objective = round(disp * ((C0 / cost) ** gamma) * ((capacity / E0) ** gamma),4)
        path = (moves,[objective,disp , cost, capacity])
    else:
        path = (moves,[disp,disp , cost, capacity])
    
    return path

