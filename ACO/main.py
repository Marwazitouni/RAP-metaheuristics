import numpy as np

from ant_colony import AntColony
from aco_reader import *


def write_solution(path,nb_subsystems):
    if path[0] == "placeholder":
        print("No solutions found")
    else:
        solution = [[] for _ in range(nb_subsystems) ]
        for ele in path[0]:
            solution[ele[0]].append(ele[1] + 1)
        
        for i in range(nb_subsystems):
            print("Subsystem ", i+1,sorted(solution[i])) 

        print("Availability : ", path[1][1])
        print("Cost : ", path[1][2])
        print("Capacity : ", path[1][3])

if __name__ == "__main__":


    path = "input/Instance.xls"
    precision = 10

    subsystems,LOLP, max_lolp = read_excel(path,precision=precision)

    ant_colony = AntColony(subsystems,LOLP, C0= 75, E0 = 750, n_ants = 50, n_best= 1,
        n_iterations = 100, alpha= 1, beta= 0.5, gamma= 0.8, max_devices = 8, evaporation=0.4,
        precision=precision, q0 = 0.5, best_ants = 0)

    print("Solving begins ...")
    shortest_path = ant_colony.solve()
    print ("shortest path: ")
    write_solution(shortest_path,len(subsystems))

