from aco_reader import read_excel

from UMGF.Component import Component
from UMGF.SubSystem import SubSystem

# This is the main function we call from the terminal
 
if __name__ == "__main__":

    # Specify the Calculations Precision
    #getcontext().prec = 8

    # Specify the printing (on the screen) Precision
    precision = 10

    # Specify The Path 
    path = "input/Instance.xls"

    # Read the inputs from the excel file or the txt file
    subsystems, LOLP, max_lolp = read_excel(path,precision)

    

    print(subsystems[0])