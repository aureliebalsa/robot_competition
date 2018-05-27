class Bottle:
    """Class that is called in a list, each new element
    is a new bottle detection with some default parameters"""

    def __init__(self,x,y,angle):  #class constructor
        """We define the coordonates x,y of the bottle and the angle
        as the default parameters """
        self.x = x
        self.y = y
        self.angle = angle
        self.lastdetection = 0
        self.quantity = 1


    def add_name(self,name):
        #add the name of the bottle to show
        self.name = 'bottle'+str(name)

    def update(self,x,y,angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.lastdetection = 0
        self.quantity += 1

    def comparison(self,x,y,angle,list_bottles):
        """list_bottles contains all the value saved as bottles
        indice is the bottle that we need to check to see if it's a new one"""

        threshold = 7
        nb_bottles = len(list_bottles)

        indice_comparison = 0

        test = -2
        while (indice_comparison < nb_bottles):
            # comparaison of first angle  avec another angle

            # if same bottle
            if (abs(x - list_bottles[indice_comparison].x) < threshold or abs(y - list_bottles[indice_comparison].y) < threshold):
                list_bottles[indice_comparison].update(x, y, angle)
                list_bottles[indice_comparison].indice = indice_comparison
                indice_bottle = indice_comparison
                list_bottles[indice_comparison].quantity+=1
                test = 1
                break
            else:
                test = 0
                list_bottles[indice_comparison].lastdetection +=1

            indice_comparison += 1

        if test == 0:
            print('new bottle')
            list_bottles.append(Bottle(x, y, angle))
            list_bottles[-1].add_name(nb_bottles)
            indice_bottle=nb_bottles

        return indice_bottle

    def no_detection(self,list_bottles):
        indice_bottle = 0
        nb_bottles = len(list_bottles)
        while (indice_bottle<nb_bottles):
            list_bottles[indice_bottle].lastdetection += 1
            indice_bottle += 1

    def delete_no_detection(self,list_bottles):
        indice_bottle = 0
        while (indice_bottle < len(list_bottles)):
            if(list_bottles[indice_bottle].lastdetection > 7):
                indice_bottle-=1
                del list_bottles[indice_bottle]
                if(len(list_bottles)==0):
                    print('empty list')

            indice_bottle += 1

    def __del__(self): # class destructor
        """destructor of the class"""
