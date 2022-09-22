from tkinter import *
from math import log, sqrt
import time

#########################################################
#                                                       #
# ---------------------- RENDER ----------------------- #
#                                                       #
#########################################################

TEXT = 30
render_data = {"canvas": None, "root": None, "stop": False,
               "start": False, "dim": (6, 7), "view": (500, 500), "text": {}}

def on_quit():
    """
    callback lors du click sur fermeture de fenêtre
    """
    render_data["stop"] = True

def write(i, j, number, color):
    canvas = render_data["canvas"]

    nbr = render_data["dim"][0]
    nbc = render_data["dim"][1]

    if i >= nbr or i < 0 or j < 0 or j >= nbc:
        return

    w = render_data["view"][0]
    h = render_data["view"][1]

    stepx = (w-TEXT)/nbc
    stepy = (h-TEXT)/nbr

    nombres = render_data["text"]
    if (i, j) in nombres:  # On a deja affiche quelque chose dans la case (x, y)
        id = nombres[i, j]
        canvas.itemconfig(id, text=str(number), fill=color)
    else:
        id = canvas.create_text(30+j*stepx+stepx/2, 30+i*stepy+stepy/2,
                                text=str(number), fill=color, font=("Purisa", int(stepx*.75)))
        nombres[i, j] = id

    canvas.update()

def erase(i, j):
    canvas = render_data["canvas"]
    nombres = render_data["text"]
    if (i, j) in nombres:
        canvas.delete(nombres[i, j])
    canvas.update()

def draw_grid():
    """
    trace le plateau de jeu (grille des disques donnée par render_data["grid"])
    """
    if render_data["stop"]:
        return None

    canvas = render_data["canvas"]
    canvas.delete("all")

    nbr = render_data["dim"][0]
    nbc = render_data["dim"][1]
    n = int(sqrt(nbr))
    w = render_data["view"][0]
    h = render_data["view"][1]

    stepx = (w-TEXT)/nbc
    stepy = (h-TEXT)/nbr

    for c in range(nbc+1):
        if c % n == 0:
            canvas.create_line(c*stepx+TEXT, TEXT, c*stepx +
                               TEXT, h, fill="black", width=3)
        else:
            canvas.create_line(c*stepx+TEXT, TEXT, c *
                               stepx+TEXT, h, fill="black")
    for r in range(nbr+1):
        if r % n == 0:
            canvas.create_line(TEXT, r*stepy+TEXT, w, r *
                               stepy+TEXT, fill="black", width=3)
        else:
            canvas.create_line(TEXT, r*stepy+TEXT, w, r *
                               stepy+TEXT, fill="black")

    for c in range(nbc):
        canvas.create_text(c*stepx+TEXT+stepx/2, TEXT/2, text=str(c),
                           width=stepx, font=("Purisa", int(stepx*.33)))
    for r in range(nbr):
        canvas.create_text(TEXT/2, r*stepy+TEXT+stepy/2, text=str(r),
                           width=stepx, font=("Purisa", int(stepx*.33)))

    canvas.update()

def configure_draw(n):
    """
    modifie les dimensions de l'affichage du plateau de jeu selon les nombres de ligne nr et colonne nc (tient compte du ratio largeur/hauteur de la fenêtre graphique)
    """
    nr, nc = n**2, n**2
    dim = (nr, nc)
    render_data["dim"] = dim

    render_data["grid"] = [[0 for i in range(nc)] for j in range(nr)]

    canvas = render_data["canvas"]
    view = (canvas.winfo_width(), canvas.winfo_height()-TEXT)
    dim = render_data["dim"]
    rx = view[0]/dim[1]
    ry = (view[1]-TEXT)/dim[0]
    if (rx < ry):
        v = (view[0], dim[0]*rx+TEXT)
    else:
        v = (dim[1]*ry, view[1])
    render_data["view"] = v

def wait_quit():
    """
    attend explicitement la fermeture de la fenêtre graphique
    """
    if (render_data["start"]):
        canvas = render_data["canvas"]
        while not(render_data["stop"]):
            canvas.update()
        root = render_data["root"]
        root.destroy()

def init_draw(w=450, h=480):
    """
    initialise la fenêtre graphique (canvas de largeur w et hauteur h)
    """
    render_data["view"] = (w, h-TEXT)

    root = Tk()
    root.protocol("WM_DELETE_WINDOW", on_quit)
    canvas = Canvas(root, width=w, height=h)
    canvas["background"] = "white"
    canvas.pack(fill=BOTH, expand=1)
    render_data["canvas"] = canvas
    render_data["root"] = root
    canvas.winfo_toplevel().title("Sudoku")
    canvas.update()
    render_data["start"] = True

def draw_sudoku_grid(n):
    """
    Trace a sudoku grid of order n
    """
    if not render_data["start"]:
        init_draw()

    configure_draw(n)

    draw_grid()


#########################################################
#                                                       #
# -------------------- FILE PARSER -------------------- #
#                                                       #
#########################################################


def read(filename):
    file = open(filename)

    dim = int(file.readline())
    grid = []

    for i in range(dim**2):
        line = file.readline().split('\n')[0].split(' ')
        for j in range(dim**2):
            if int(line[j]) != 0:
                grid.append((i, j, int(line[j])))

    file.close()

    return dim, grid


#########################################################
#                                                       #
# -------------------- SHOW SUDOKU -------------------- #
#                                                       #
#########################################################

#Affiche la fenêtre graphique
def init_window(array):

    len_array = len(array)

    draw_sudoku_grid(int(sqrt(len_array)))

    for y in range(len_array):
        for x in range(len_array):

            if array[y][x] == 0:
                write(y, x, "?", "green2")
            else:
                write(y, x, array[y][x], "red")
    
#Arrête l'affichage de la fenêtre graphique
def stop_window():
    wait_quit()

def quit_window():
    on_quit()

#Affiche la grille de valeur
def show_array(array):

    dim = len(array)

    for y in range(dim):
        for x in range(dim):
            print(array[y][x], end=' ')
        print()

#Remplace un nombre à l'endroit indiqué
def replace_value(row, col, number):

    #render.erase(row, col)
    if number == 0:
        write(row, col, "?", "green2")
    else:
        write(row, col, number, "blue")

#########################################################
#                                                       #
# -------------------- LOAD SUDOKU -------------------- #
#                                                       #
#########################################################

#Creation des lignes du sudoku
def create_line(n, value):
  line = []

  for i in range(n):
    line.append(value)

  return line

#Creation de la grille du Sudoku ligne par ligne
def create_array(n, value):
  array = []

  for i in range(n):
    array.append(create_line(n, value))

  return array

#Chargement du fichier et création de la grille avec insertion des valeurs
def load_array(file):

    dim, values = read(file)
    array = create_array(dim ** 2, 0)

    for location in values:
        array[location[0]][location[1]] = location[2]

    return array, int(dim)

#########################################################
#                                                       #
# ------------------- CHECK SUDOKU -------------------- #
#                                                       #
#########################################################


#Vérifie si le nombre est déjà présent dans la ligne
def is_in_row(array, len_array, row, number):

    for col in range(len_array):
        if number == array[row][col]:
            return True
    return False

#Vérifie si le nombre est déjà présent dans la colonne
def is_in_col(array, len_array, col, number):

    for row in range(len_array):
        if number == array[row][col]:
            return True
    return False

#Vérifie si le nombre est déjà présent dans la box
def is_in_box(array, dim, row, col, number):

    b_row = row - row % dim
    b_col = col - col % dim

    for y in range(dim):
        for x in range(dim):
            if array[y + b_row][x + b_col] == number:
                return True
    return False

#Vérifie si la position du nombre ne comporte par de doublon sur la ligne, la colonne ou dans la box
def is_valid(array, dim, row, column, number):

    if not is_in_row(array, dim ** 2, row, number) and \
        not is_in_col(array, dim ** 2, column, number) and \
        not is_in_box(array, dim, row, column, number) :
        return True
    else:
        return False

#Compte le nombre de case vide dans la grille
def count_empty(array):
    
    empty_cases = 0

    for line in array:
        for value in line:
            if value == 0:
                empty_cases += 1
    
    return empty_cases

#Renvois si la case est vide ou non
def is_empty(array, row, col):

    return array[row][col] == 0

#Compte le nombre de valeur demandées dans une box
def count_value_in_box(array, b_row, b_col, dim, number):

    count = 0

    for y in range(dim):
        for x in range(dim):
            if array[y + b_row][x + b_col] == number:
                count += 1
    
    return count

#Détecte si le nombre est un entier
def is_whole_number(number):

    temp_num = int(number)

    return(temp_num == number)

#Vérifie le nombre de possibilité dans le tableau et renvois la puissance en base de 2 de la valeur - 1 correspondante
def get_possiblities(array_possibilities, array, dim, len_array):

    # 1 = 1 | 2 = 2 | 3 = 4 | 4 = 8 | 5 = 16 | 6 = 32 | 7 = 64 | 8 = 128 | 9 = 256 | etc...

    #Si il n'y a que une seule possiblité, alors la valeur est toujours une puissance de base de 2
    #De ce fait, le logarithme du nombre sera forcément un entier
    #Si le nombre de possilibités est supérieur à 1, alors la valeur de possibilité est additionnée en puissance de base de 2
    #De ce fait, le logarithme de ce nombre ne pourra jamais devenir un entier.

    row = 0
    while row < len_array:
        col = 0
        while col < len_array:
            if is_empty(array, row, col):
                for value in range(1, len_array + 1):
                    if is_valid(array, dim, row, col, value):
                        array_possibilities[row][col] += 2 ** (value - 1)
            col += 1
        row += 1
    return array_possibilities

#Renvois toutes les valeurs possibles sur une case
def get_possibility_in_case(array, row, col, dim):

    possibilities = [0]

    for value in range(1, dim ** 2 + 1):
        if is_valid(array, dim, row, col, value):
            possibilities.append(value)

    return possibilities

#Reset toutes les valeurs de la grilles à 0
def clean_array(array, len_array, value):

    for row in range(len_array):
        for col in range(len_array):
            array[row][col] = value
    return array

#Compte le nombre de valeur dans une ligne
def count_values_in_line(line, value):

    count = 0

    for i in line:
        if i == value:
            count += 1

    return count

#Crée ligne incrémentée de 1 à n
def create_incremented_line(n):

    line = []

    for i in range(n):
        line.append(i + 1)

    return line

#Supprime une valeur dans un tableau à 1 dimension
def remove_value_in_line(tab, value):


    i = 0

    while i < len(tab):

        if tab[i] == value:
            tab.pop(i)

        i = i + 1
    
    return tab

#Fonction crée pour copier à l'identique la grille afin de ne pas avoir une variable pointant vers la grille originale
def copy_array(array, len_array):

    original_array = create_array(len_array, 0)

    row = 0
    col = 0

    while row < len_array :
        while col < len_array :
            original_array[row][col] = array[row][col]
            col += 1
        col = 0
        row += 1
    
    return original_array

#######################################################
#                                                     #
# ------------------ SOLVE SUDOKU ------------------- #
#                                                     #
#######################################################


#Teste toutes les lignes de la grille et remplis les lignes avec 1 valeur manquante
def line_filler_by_addition(array, len_array):

    added_value = False

    for row in range(len_array):
        for col in range(len_array):
            if array[row][col] == 0:
                num_possible = create_incremented_line(len_array)
                for num_col in range(len_array):
                    if array[row][num_col] != 0 and array[row][num_col] in num_possible:
                        num_possible = remove_value_in_line(num_possible, array[row][num_col])
                for num_row in range(len_array):
                    if array[num_row][col] != 0 and array[num_row][col] in num_possible:
                        num_possible = remove_value_in_line(num_possible, array[num_row][col])
                if len(num_possible) == 1:
                    array[row][col] = num_possible[0]
                    replace_value(row,col, array[row][col])
                    added_value = True

    return [array, added_value]

#Teste toutes les lignes de la grilles par élimination et rajoute la valeur manquante si possible
def line_filler_by_elimination(array, len_array):

    added_value = False

    #Teste toutes les lignes horizontales (row)
    for row in range(len_array):
        num_possible = create_incremented_line(len_array)
        for col in range(len_array):
            if array[row][col] != 0:
                num_possible = remove_value_in_line(num_possible, array[row][col])

        #Récupère tout les nombres possibles dans la liste (permet de diminuer le nombre de try)
        for number in num_possible:
            testing_line = create_line(len_array, True)
            for col in range(len_array):
                if array[row][col] != 0:
                    testing_line[col] = False
            
            #Teste toutes les colonnes pour voir si le nombre est déjà présent, met False si déjà présent
            for col in testing_line:
                if col == True:
                    for t_row in range(len_array):
                        if array[t_row][col] == number:
                            testing_line[col] = False
                            break
            #Si il n'y a que une seule possibilité, remplacer avec le nombre correspondant
            if count_values_in_line(testing_line, True) == 1:
                for i in range(len(testing_line)):
                    if testing_line[i] == True:
                        array[row][i] = number
                        replace_value(row, i, array[row][i])

    #Teste toutes les lignes verticales (col)
    for col in range(len_array):
        num_possible = create_incremented_line(len_array)
        for row in range(len_array):
            if array[row][col] != 0:
                num_possible = remove_value_in_line(num_possible, array[row][col])

        #Récupère tout les nombres possibles dans la liste (permet de diminuer le nombre de try)
        for number in num_possible:
            testing_line = create_line(len_array, True)
            for row in range(len_array):
                if array[row][col] != 0:
                    testing_line[col] = False
            
            #Teste toutes les lignes pour voir si le nombre est déjà présent, met False si déjà présent
            for row in testing_line:
                if row == True:
                    for t_col in range(len_array):
                        if array[row][t_col] == number:
                            testing_line[row] = False
                            break
            
            #Si il n'y a que une seule possibilité, remplacer avec le nombre correspondant
            if count_values_in_line(testing_line, True) == 1:
                for i in range(testing_line):
                    if testing_line[i] == True:
                        array[i][col] = number
                        replace_value(i, col, array[i][col])
                        added_value = True

    return [array, added_value]

#Teste et remplis les blocs de la grille par addition (si il ne reste plus qu'une valeur possible)
def block_filler_by_addition(array, dim, len_array):


    added_value = False
    for block_row in range(dim):
        for block_col in range(dim):

            b_row = (block_row * dim) - (block_row * dim) % dim
            b_col = (block_col * dim) - (block_col * dim) % dim

            if count_value_in_box(array,b_row, b_col, dim, 0) == 1:
                for number in range(1, len_array + 1):
                    if not is_in_box(array, dim, block_row, block_col, number):
                        
                        for y in range(b_row, b_row + dim):
                            for x in range(b_col, b_col + dim):

                                if array[y][x] == 0:
                                    array[y][x] = number
                                    replace_value(y, x, array[y][x])
                                    added_value = True

    return [array, added_value]

#Teste et remplis les blocs de la grille par elimination (si il n'y a que cet emplacement logique)
def block_filler_by_elimination(array, dim, len_array):

    added_value = False
    array_box = create_array(dim, True)

    for block_row in range(dim):
        for block_col in range(dim):

            #Récupère les coordonnées de la case supérieure gauche du bloc
            b_row = (block_row * dim) - (block_row * dim) % dim
            b_col = (block_col * dim) - (block_col * dim) % dim

            num_possible = create_incremented_line(len_array)

            #Elimine tout les nombres déjà en place
            for y in range(dim):
                for x in range(dim):
                    if array[y + b_row][x + b_col] != 0:
                        num_possible = remove_value_in_line(num_possible, array[y + b_row][x + b_col])

            #Vérifie le bloc pour tout les nombres possibles
            for number in num_possible:

                #Met toutes les cases utilisées à False
                for y in range(dim):
                    for x in range(dim):
                        if array[y + b_row][x + b_col] != 0:
                            array_box[y][x] = False

                #Vérifie si le nombre est présent sur Y (horizontal) et met la ligne en False si True
                for y in range(dim):
                    if is_in_row(array, len_array, y + b_row, number) == True :
                        for x in range(dim):
                            array_box[y][x] = False
                #Vérifie si le nombre est présent sur X (vertical) et met la ligne en False si True
                for x in range(dim):
                    if is_in_col(array, len_array, x + b_col, number) == True :
                        for y in range(dim):
                            array_box[y][x] = False

                #Compte le nombre de True restant. Si il en reste un seul, remplacer la case par le nombre actuel
                if count_value_in_box(array_box, 0, 0, dim, True) == 1:
                    for y in range(dim):
                        for x in range(dim):
                            if array_box[y][x] == True:
                                array[y + b_row][x + b_col] = number
                                replace_value(y + b_row, x + b_col, array[y + b_row][x + b_col])
                                added_value = True
                
                #Reset de array_box pour les prochains nombres à tester
                array_box = clean_array(array_box, dim, True)

    return [array, added_value]

#Fonction de remplissage simple du sudoku avec vérification de possibilités
def simple_filler(array, original_array, dim, len_array, array_possibilities):

    added_value = False
    
    #Récupère les possibilités de chaques cases (Celles-ci sont retournées en exposant de base de 2)
    array_possibilities = get_possiblities(array_possibilities, array, dim, len_array)
    row = 0

    while row < len_array and not added_value:
        col = 0
        while col < len_array and not added_value:
            if array_possibilities[row][col] != 0 \
                and original_array[row][col] == 0:

                #Récupère l'exposant de la puissance.
                number = log(array_possibilities[row][col]) / log(2)

                #Si le nombre est un entier, alors il n'y a qu'une seule possiblitée, sinon, il y en a plusieurs
                if is_whole_number(number):

                    array[row][col] = int(number) + 1
                    added_value = True
                    replace_value(row, col, array[row][col])
            col += 1
        row += 1

    clean_array(array_possibilities, len_array, 0)

    return [array, added_value]   

#Fonction principale de remplissage du sudoku en non-recurssif
def non_rec_solver(array, original_array, dim, len_array, added_value):

    array_possibilities = copy_array(original_array, len_array)

    while True:

        array, added_value = simple_filler(array, original_array, dim, len_array, array_possibilities)

        if count_empty(array) == 0 :
            return array, added_value
        
        else:
            if not added_value:
                array, added_ba = block_filler_by_addition(array, dim, len_array)
                array, added_be = block_filler_by_elimination(array, dim, len_array)
                array, added_la = line_filler_by_addition(array, len_array)
                array, added_le = line_filler_by_elimination(array, len_array)

                if not added_be and not added_be and not added_la and not added_le:
                    return array, added_value
            added_value = False
            col = 0
            row = 0
        
#Fonction de remplissage du sudoku avec utilisation de la recursivite
def rec_solver(array, original_array, dim, len_array, is_solved):

    row = 0
    col = 0

    while row < len_array :
        
        if is_empty(original_array, row, col) and \
            is_empty(array, row, col):

            number = 1
            while number < len_array + 1:

                if is_valid(array, dim, row, col, number):

                    array[row][col] = number
                    replace_value(row, col, array[row][col])
                    if count_empty(array) == 0:
                        is_solved = True
                        return array, is_solved
                    else:
                        array, is_solved = rec_solver(array, original_array, dim, len_array, is_solved)
                number = number + 1
            if not is_solved:
                array[row][col] = 0
                replace_value(row, col, array[row][col])
            return array, is_solved
        else:
            col = col + 1

            if col >= len_array:
                col = 0
                row = row + 1

#Fonction principale de résolution du sudoku. Utilise remplissage, puis récusivité si remplissage ne permet pas la résolution totale
def main_solver(array, dim):

    init_window(array)
    
    original_array = copy_array(array, dim ** 2)
    array, added_value = non_rec_solver(array, original_array, dim, dim ** 2, False)
    if not added_value:
        original_array = copy_array(array, dim ** 2)
        array, is_solved = rec_solver(array, original_array, dim, dim ** 2, False)

    print("Grille résolue")
    stop_window()

#######################################################
#                                                     #
# -------------------- PLAY SUDOKU ------------------ #
#                                                     #
#######################################################

#Récupère la ligne et la colonne demandée par l'utilisateur. Gestion des erreurs intégrée
def get_row_or_col(direction, len_array):

    if direction == 0:
        value = input("Entrez un numéro de ligne ou entrée pour annuler : ")
    else:
        value = input("Entrez un numéro de colonne ou entrée pour annuler : ")
    if value == "":
        return [-1, False]
    elif is_number(value):
        value = int(value)
        if value >= 0 and value <= len_array:
            return [value, True]
        else:
            if direction == 0:
                print("Le numéro de ligne n'est pas correct. Il doit être entre 0 et", len_array)
            else:
                print("Le numéro de colonne n'est pas correct. Il doit être entre 0 et", len_array)
            return get_row_or_col(direction, len_array)
    else:
        print("Veuillez entrer un nombre entier.")
        return get_row_or_col(direction, len_array)

#Affiche le nombre de possibilitées
def show_possibilites(possibilites):

    print("Les valeurs possibles sont :", end=" ")
    for number in possibilites:
        print(number, end=" ")
    print()

#Met une valeur choisie par l'utilisateur
def set_value(array, original_array, row, col, dim, possibilities):

    value = input("Entrez une valeur possible ou appuyez sur entrée pour annuler le coup : ")
    tuple_choice_yes = ["Oui",  "oui",  "O",  "o",  "Yes",  "yes",  "Y", "y"]
    tuple_choice_no = ["Non", "non", "N", "n", "No", "no", ""]

    if value == "":
        return [array, False]
    elif is_number(value):
        value = int(value)
        if value >= 0 or value <= dim ** 2:
            if value in possibilities:
                array[row][col] = value
                replace_value(row, col, array[row][col])
            else:
                confirmation_1 = True
                while confirmation_1 == True:
                    print("Ce numéro n'est pas présent dans les valeurs possible pour cette case !")
                    choice = input("Êtes vous sûr de vouloir continuer ? (Non par défaut) : ")
                    if choice in tuple_choice_yes:
                        confirmation_2 = True
                        while confirmation_2 == True:
                            print("Confirmez votre choix. Le sudoku risque de ne plus être solvable.")
                            choice = input("Continuer ? (Non par défaut) : ")
                            if choice in tuple_choice_yes:

                                confirmation_1 = False
                                confirmation_2 = False

                                array[row][col] = value
                                replace_value(row, col, array[row][col])
                            elif choice in tuple_choice_no:
                                return [array, True]
                            else:
                                print('Entrez "Oui" ou "Non" pour continuer')
                    elif choice in tuple_choice_no:
                        return [array, True]
                    else:
                        print('Entrez "Oui" ou "Non" pour continuer')
            
            return [array, True]

        else:
            print("Entrez une valeur comprise entre 0 et", dim ** 2)
            return set_value(array, original_array, row, col, dim, possibilities)
    else:
        print("Il faut entrer un nombre entier")
        return set_value(array, original_array, row, col, dim, possibilities)

    if validation_row(array, dim) \
        and validation_col(array, dim) \
        and validation_box(array, dim) :
        return True
    else:
        return False

#Vérifie que tout les nombres sont présents dans une ligne
def validation_row(array, dim):
    
    for row in range(dim ** 2):

        numbers = create_incremented_line(dim ** 2)

        for col in range(dim ** 2):

            if array[row][col] in numbers:
                numbers.pop(col)
            else:
                return False
    return True

#Vérifie que tout les nombres sont présents dans une colonne
def validation_col(array, dim):
    
    for col in range(dim ** 2):

        numbers = create_incremented_line(dim ** 2)

        for row in range(dim ** 2):

            if array[row][col] in numbers:
                numbers.pop(row)
            else:
                return False
    return True

#Vérifie que tout les nombres sont présents dans une box
def validation_box(array, dim):
    
    for col in range(0, dim ** 2, dim):

        numbers = create_incremented_line(dim ** 2)

        for row in range(0, dim ** 2, dim):

            b_row = row - row % dim
            b_col = col - col % dim

            for y in range(dim):
                for x in range(dim):
                    if array[y][x] in numbers:
                        numbers.pop(y)
                    else:
                        return False
    return True

#Fonction principale de validation du sudoku
def validation(array, dim):

    if validation_row(array, dim) and \
        validation_col(array, dim) and \
        validation_box(array, dim):
        return True
    else:
        return False

#Vérifie si la valeur est bien un nombre
def is_number(value):



    tuple_number = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    for i in value:
        if i not in tuple_number:
            return False
    return True

#Fonction principale pour jouer au sudoku
def main_play(array, dim):

    end_game = False
    original_array = copy_array(array, dim ** 2)

    init_window(array)

    while end_game == False:

        valid = True
        count_cases = count_empty(array)
        print("Il reste", count_cases,"cases à remplir")
        if count_cases > 0:
            row, valid = get_row_or_col(0, dim ** 2)

        if valid and count_cases > 0:
            col, valid = get_row_or_col(1, dim ** 2)
        if valid and count_cases > 0:
            if original_array[row][col] == 0:
                possibilities = get_possibility_in_case(array, row, col, dim)
                show_possibilites(possibilities)
                array, valid = set_value(array, original_array, row, col, dim, possibilities)
            else:
                print("Il n'est pas possible de modifier cette case")
                valid = False
        if valid:
            if count_empty(array) == 0:
                if validation(array, dim):
                    end_game = True
                    print("Sudoku résolu ! Bravo !")
                else:
                    print("Des erreurs sont présentes dans le sudoku !")
                    print("Dernière réponse suprimée. Vérifiez le sudoku.")
                    array[row][col] = 0
                    replace_value(row, col, array[row][col])

    quit_window()

#######################################################
#                                                     #
# -------------------- SUDOKU.PY -------------------- #
#                                                     #
#######################################################

#Fonction principale
def main():

    array, dim = get_file()
    if get_game_choice() == 1:

        main_play(array, dim)
    else:
        main_solver(array, dim)

#Récupère le choix du joueur. Redemande en cas d'erreur
def get_game_choice():

    tuple_play = ["J", "j", "jouer", "Jouer", "joue", "Joue", "play", "Play"]
    tuple_solve = ["R", "r", "résoudre", "Résoudre", "Resoudre", "resoudre", "Solve", "solve"]

    sel_choice = input('Voulez-vous "(J)ouer" ou "(R)ésoudre" ? ')

    if sel_choice in tuple_play:
        sel_choice = 1
    elif sel_choice in tuple_solve:
        sel_choice = 2
    else:
        print("Réponse incorrecte !")
        return get_game_choice()
    return sel_choice

#Récupère le fichier par l'utilisateur
def get_file():

    sel_file = input("Entrez le nom du fichier (entrée pour prendre le fichier défaut): ")

    if sel_file == "":
        return load_array('grilles\sudoku_9_9_1.txt')
        
    if not sel_file.lower().endswith(".txt"):
        sel_file += ".txt"
        
    return load_array("grilles\\"+sel_file)

if __name__ == "__main__":
    main()
