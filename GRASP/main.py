import numpy as np

from solver import *
from grasp_reader import *

from UMGF.SubSystem import SubSystem
from UMGF.Component import Component
from UMGF.solver import *

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

    best_path, best_availability = solve(subsystems, LOLP, C0=82, E=820, gamma=8, max_devices=8, nb_exec=10, precision=10)
    
    print ("shortest path: ")
    print(best_availability)
    print(best_path)
    #print("\n".join(map(str,best_path)))
    #write_solution(shortest_path,len(subsystems))

