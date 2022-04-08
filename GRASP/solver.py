import random
import numpy as np
from numpy.random import choice as np_choice

from UMGF.SubSystem import SubSystem
from UMGF.Component import Component
from UMGF.solver import *

def solve(subsystems, LOLP, C0=82, E=820, gamma = 2, max_devices=8, nb_exec=5, max_tries=5, precision=10):
    best_path = None
    best_availability = [0,0,0]
    for k in range(nb_exec):
        ratio_subsystems = []
        mean_costs_ratios = []
        sum_mean_costs = 0
        for i,sub in enumerate(subsystems):
            ratios = []
            total_cost = 0
            for j, device in enumerate(sub.components):
                ratios.append((j,(device.states[0][0]  * device.states[0][0]) ** gamma / device.cost) )
                total_cost += device.cost
            
            mean_cost = total_cost / len(sub.components)
            mean_costs_ratios.append(mean_cost)
            sum_mean_costs += mean_cost
            ratios = sorted(ratios,key = lambda device: device[1],reverse=True)
            ratio_subsystems.append(ratios)
        
        for i in range(len(mean_costs_ratios)):
            mean_costs_ratios[i] /= sum_mean_costs

        path_subsystems = []
            
        for i in range(len(subsystems)):
            subsystem = SubSystem(id = i + 1, nb_components= 0, components=[])
            path_subsystems.append(subsystem)

        total_cost = 0
        for i, ratios in enumerate(ratio_subsystems):
            sub_cost = 0
            for j in range(max_devices):
                np_ratios = np.empty(len(ratios))
                for ratio in ratios:
                    np_ratios[ratio[0]] = ratio[1]

                all_inds = range(0,len(ratios))
                
                norm_ratios = np_ratios / np_ratios.sum()
                chosen_device = np_choice(all_inds, 1, p=norm_ratios)[0]
                
                nb_tries = 1
                device_i = subsystems[i].components[chosen_device]
                while (sub_cost + device_i.cost > C0 * mean_costs_ratios[i] and nb_tries<max_tries ):
                    chosen_device = np_choice(all_inds, 1, p=norm_ratios)[0]
                    device_i = subsystems[i].components[chosen_device]
                    nb_tries += 1
                
                if sub_cost + device_i.cost > C0 * mean_costs_ratios[i]:
                    device_i = subsystems[i].components[-1]

                if sub_cost + device_i.cost <= C0 * mean_costs_ratios[i]:

                    total_cost += device_i.cost
                    sub_cost += device_i.cost
                    path_subsystems[i].components.append(device_i)
                    path_subsystems[i].nb_components += 1   
                

        disp , unsupplied, capacity = objective(path_subsystems,LOLP, precision)
        
        if best_availability[0] < disp:
            best_availability = [disp,total_cost,capacity]
            best_path = path_subsystems
    
    return best_path, best_availability

        

            