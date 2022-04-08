from UMGF.Component import Component
from UMGF.SubSystem import SubSystem

"""
    This File contains all the functions used to compute the different metrics,
    we used Decimal for precision purpous
"""

def umgf_sub_system(subsystem,precision):
    """
        This function is used to compute the UMGF of a subsytem
        it returns a dictionary of exponenets as keys (Z) and coeff of umgf_subsystem
    """
    # Initialize the polynome 
    umgf = dict()
    
    # Copy the first component to the result polynome
    for state in subsystem.components[0].states:
        umgf[state[1]] = state[0]
    
    # Multiply the rest of the components 
    for j in range(1,subsystem.nb_components):
        component = subsystem.components[j]
        # Empty Polynome which will be the new result of UMGF
        tmp_umgf = dict()
        # For each key in component
        for k in range(component.nb_states):
            # We multiply by each key present UMGF
            for key in umgf:
                coeff = round(component.states[k][0] * umgf[key],precision)
                exponent = component.states[k][1] + key
                tmp_umgf[exponent] = tmp_umgf.get(exponent,0) + coeff
        umgf = tmp_umgf
    return umgf

def umgf_system(subsystems,precision):
    """
        This function is used to compute the UMGF of the whole system using 
        umgfs of all subsystems
        it returns a dictionary of exponenets as keys (Z) and coeff of umgf_global
    """
    # A copy of umgf of the first subsystem
    umgf = subsystems[0].umgf.copy()
    # Multiply by the rest of UMGFs of the rest of subsytems
    for s in range(1,len(subsystems)):
        subsystem = subsystems[s]
        # Empty Polynome which will be the new result of UMGF
        tmp_umgf = dict()
        list_keys1 = sorted(umgf.keys()) 
        # For each monome in the current UMGF
        for key1 in list_keys1:
            list_keys2 = sorted(subsystem.umgf.keys())
            # We multiply be each monome of the next subsystem
            for key2 in list_keys2:
                # We take the minimum indice of the Z
                exponent = min(key1,key2)
                # We multiply Coeffecients
                coeff = round(umgf[key1] * subsystem.umgf[key2],precision)
                # We add it to the existing coeff (if it doesn't exist we add it to 0)
                tmp_umgf[exponent] = tmp_umgf.get(exponent,0) + coeff
        # The new result of UMGF is Tmp_UMGF
        umgf = tmp_umgf
    return umgf

def disp(global_umgf,LOLP,precision):
    """
        This function is used to compute the Disponibility and Unsupplied demand
        of the whole system using umgf_global
        it returns all_disp,all_unsupplied
    """
    list_keys = global_umgf.keys() 
    all_disp = 0
    all_unsupplied = 0
    for i,demand in enumerate(LOLP):
        partial_disp = 0
        partial_unsupplied = 0
        for key in list_keys:
            if (key >= demand[0]):
                partial_disp += global_umgf[key]
            else:
                partial_unsupplied += round((demand[0]-key) * global_umgf[key],precision)
        all_disp += partial_disp * (demand[1] / 100 )
        all_unsupplied += partial_unsupplied * ( demand[1] / 100 )
    return all_disp,all_unsupplied

def capacity(global_umgf,precision):
    """
        This function is used to compute the capacity
        of the whole system using umgf_global
        it returns all_capacity
    """
    list_keys = global_umgf.keys()
    all_capacity = 0
    # For each monome in the UMFG polynome
    for key in list_keys:
        # We replace the Z with its indices (key) and multiply it by the coeff and sum them
        all_capacity += round(key * global_umgf[key],precision)
    
    return all_capacity

def write_umgf(umgf, precision):
    """
        A helper function to print UMGF
    """
    list_keys = sorted(umgf.keys()) 
    # We go through the monomes in an ordered way
    for key in list_keys:
        print("+ {:3.4E}*Z({:.2f})".format(umgf[key],key),end=" ")
    print("\n")

def objective(subsystems,LOLP, precision):
    
    # Compute UMGF of each subsytem
    for i,subsystem in enumerate(subsystems):
        umgf = umgf_sub_system(subsystem,precision)
        subsystem.umgf = umgf

    # Compute UMGF of each subsytem
    umgf_global = umgf_system(subsystems,precision)
    
    # Compute the disponibility and the unsupplied demand using umgf_global
    disponibility,unsupplied = disp(umgf_global,LOLP,precision)
    all_capcity = capacity(umgf_global,precision)

    return disponibility, unsupplied, all_capcity


    