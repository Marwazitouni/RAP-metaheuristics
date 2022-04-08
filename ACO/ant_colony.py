import random as rn
import numpy as np
from numpy.random import choice as np_choice

from UMGF.SubSystem import SubSystem
from UMGF.Component import Component
from UMGF.solver import *

from Local_search import *

class AntColony(object):

    def __init__(self, subsystems, LOLP, C0, E0, n_ants = 40, n_best = 5, n_iterations = 100, alpha=1, beta=1, gamma = 0.8,max_devices = 8,evaporation = 0.9, precision = 10, q0 = 0.5, best_ants = 10):
        """
        Args:
            distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
            n_ants (int): Number of ants running per iteration
            n_best (int): Number of best ants who deposit pheromone
            n_iteration (int): Number of iterations
            decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay, so 0.95 will lead to decay, 0.5 to much faster decay.
            alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight. Default=1
            beta (int or float): exponent on distance, higher beta give distance more weight. Default=1

        Example:
            ant_colony = AntColony(german_distances, 100, 20, 2000, 0.95, alpha=1, beta=2)          
        """
        self.subsystems = subsystems
        self.LOLP = LOLP
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.gamma = gamma
        self.beta = beta
        self.max_devices = max_devices
        self.evaporation = evaporation
        self.precision = precision
        self.C0 = C0
        self.E0 = E0
        self.q0 = q0
        self.best_ants = best_ants
        self.aco_graph = self.init_graph()

    def solve(self):
        shortest_path = None
        all_time_shortest_path = ("placeholder", [-1 * np.inf, - 1 * np.inf])
        for i in range(self.n_iterations):
            
            all_paths = self.gen_all_paths()
            all_paths = self.improve_best_ants(all_paths)
            
            feasible_solutions = list(filter(lambda path: path[1][2] < self.C0 and path[1][3] > self.E0, all_paths))
            if len(feasible_solutions)!=0:
                shortest_path = max(feasible_solutions, key=lambda x: x[1][1])
                print(len(feasible_solutions))
            else:
                shortest_path = max(all_paths, key=lambda x: x[1][0])
        
            if shortest_path[1][1] > all_time_shortest_path[1][1] and shortest_path[1][2] < self.C0 and shortest_path[1][3] > self.E0: 
                all_time_shortest_path = shortest_path
                print (shortest_path)

            self.spread_pheronome_global(all_paths, feasible_solutions)
            
        return all_time_shortest_path
    
    def init_graph(self):
        aco_graph = []
        """ Initializing pheromone """
        for subsystem in self.subsystems:
            heuristic_info = []
            sum_availability = 0
            nb_devices = 0
            for component in subsystem.components:
                #heuristic_info.append(1 / (1 + component.states[0][0])) # Using Zeblah
                heuristic_info.append(component.states[0][0] / component.cost) # Using Alice
                sum_availability += component.states[0][0]
                nb_devices += 1
            heuristic_info.append(sum_availability / nb_devices)
            #pheromone = [1 / (sum_availability * (nb_devices + 1))] * (nb_devices + 1) # Using Zeblah
            pheromone = [1 / (nb_devices + 1)] * (nb_devices + 1) # Using Alice
            heuristic_info = np.array(heuristic_info)
            pheromone = np.array(pheromone)
            
            aco_graph.append([heuristic_info,pheromone])
        return aco_graph

    def spread_pheronome_global(self, all_paths, feasible_solutions):
        """
        if len(feasible_solutions)!=0:
            sorted_paths = sorted(feasible_solutions, key=lambda x: x[1][0], reverse=True)
        else:
        """
        sorted_paths = all_paths #sorted(all_paths, key=lambda x: x[1][0], reverse=True)

        for path, x in sorted_paths[:self.n_best]:
            for move in path:
                disp = x[0] 
                self.aco_graph[move[0]][1][move[1]] += 1.0 / disp

    def improve_best_ants(self,all_paths):
        sorted_paths = sorted(all_paths, key=lambda x: x[1][0], reverse=True)
        for path in sorted_paths[:self.best_ants]:
            path = improve_cost(path,self.subsystems,self.LOLP,self.precision,self.C0,self.E0,self.gamma)
        
        return sorted_paths

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path()
            disp, capacity = self.path_reliability(path)
            disp = round(disp,4)
            capacity = round(capacity,2)
            cost = round(self.compute_cost(path),4)
            if cost > self.C0 or capacity < self.E0:
                objective = round(disp * ((self.C0 / cost) ** self.gamma) * ((capacity / self.E0) ** self.gamma),4)
                all_paths.append((path, [objective, disp,cost,capacity]))
            else:
                all_paths.append((path, [disp, disp,cost,capacity]))
            
        return all_paths

    def spread_pheronome_local(self, pheromone, device):
        pheromone[device] = self.evaporation * pheromone[device]

    def gen_path(self):
        path = []
        for i in range(len(self.aco_graph)):
            for j in range(self.max_devices):
                
                pheromone = self.aco_graph[i][1]
                heuristic_info = self.aco_graph[i][0]
                
                device = self.pick_device(pheromone, heuristic_info)
                self.spread_pheronome_local(pheromone, device)
                
                path.append((i, device))

        return path

    def pick_device(self, pheromone, heuristic_info):
        q = rn.random()
        if q < self.q0:
            device = np.argmax((pheromone ** self.alpha) * (heuristic_info ** self.beta))
        else:
            row = (pheromone ** self.alpha) * (heuristic_info ** self.beta)

            norm_row = row / row.sum()
            all_inds = range(len(pheromone))
            device = np_choice(all_inds, 1, p=norm_row)[0]
        
        return device

    def path_reliability(self, path):
        path_subsystems = []
        
        for i in range(len(self.subsystems)):
            subsystem = SubSystem(id = i + 1, nb_components= 0, components=[])
            path_subsystems.append(subsystem)

        for move in path:
            subsystem_i, device_id = move
            subsystem = self.subsystems[subsystem_i]

            if device_id < subsystem.nb_components: # Blank Node

                device_i = subsystem.components[device_id]

                path_subsystems[subsystem_i].components.append(device_i)
                path_subsystems[subsystem_i].nb_components += 1
        
        not_feasible = False
        for subsystem in path_subsystems:
            if len(subsystem.components) == 0:
                not_feasible = True
                break
        
        if not_feasible:
            disp, capacity = 0,1
        else:
            disp , unsupplied, capacity = objective(path_subsystems,self.LOLP, self.precision)
        
        return disp, capacity

    def compute_cost(self,path):
        total_cost = 0
        for move in path:
            subsystem_i, device_id = move
            subsystem = self.subsystems[subsystem_i]

            if device_id < subsystem.nb_components: # Blank Node
                device_i = subsystem.components[device_id]
                total_cost += device_i.cost
        
        return total_cost
    
    