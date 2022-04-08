class SubSystem:
    def __init__(self,id=0,nb_components=0,components = []):
        self.id = id
        self.nb_components = nb_components
        self.components = components

    def __str__(self): 
        str_components = "\n".join(map(str, self.components))
        return "\nSubSystem_ID " + str(self.id) + " Nb_Components " + str(self.nb_components) + "\n" + str_components 
    
    def __repr__(self):
        return  self.__str__() + "\n" 
