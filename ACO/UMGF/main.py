from reader import read_instance, read_excel
from Component import Component
from SubSystem import SubSystem
from solver import *

# This is the main function we call from the terminal
 
if __name__ == "__main__":

    # Specify the Calculations Precision
    #getcontext().prec = 8

    # Specify the printing (on the screen) Precision
    precision = 10

    # Specify The Path 
    path = "input/Instance_6.xls"

    # Read the inputs from the excel file or the txt file
    subsystems, LOLP, max_lolp = read_excel(path,precision)

    # Print the whole system, verify to check that reading the files is done right
    print("\nSystem : ")
    print('\n'.join(map(str, subsystems)))
    print("LOLP : ",LOLP)
    print("\n******************************************\n")

    # Compute UMGF of each subsytem
    for i,subsystem in enumerate(subsystems):
        umgf = umgf_sub_system(subsystem,precision)
        subsystem.umgf = umgf
        print("UMGF Sub System " + str(i+1))
        write_umgf(umgf,precision)

    # Compute UMGF of each subsytem
    umgf_global = umgf_system(subsystems,precision)
    print("UMGF All System ")    
    write_umgf(umgf_global,precision)
    # Compute the disponibility and the unsupplied demand using umgf_global
    disponibility,unsupplied = disp(umgf_global,LOLP,precision)

    # Compute the capacity of the system using umgf_global
    all_capcity = capacity(umgf_global,precision)

    # Print all the metrics we computed
    print("Disponobility : {:.4f} %".format(disponibility),end="\n\n" )
    print("LOLP : {:.4f} %".format(1 - disponibility),end="\n\n")
    print("Unsupplied  : {:.4f} %".format(unsupplied),end="%\n\n")
    print("Capacity {:.4f} % {:.4f} MW".format((all_capcity * max_lolp)/100),all_capcity,end="\n\n")
