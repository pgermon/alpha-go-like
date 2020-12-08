import numpy as np
import gzip, os.path
import json
import Goban

# Import du fichier d'exemples
def get_raw_data_go(data_to_predict, output):
    ''' Returns the set of samples from the local file or download it if it does not exists'''


    raw_samples_file = output

    if not os.path.isfile(raw_samples_file):
        print("File", raw_samples_file, "not found, I am downloading it...", end="")
        import urllib.request 
        urllib.request.urlretrieve (data_to_predict, output)
        print(" Done")

    with gzip.open(output) as fz:
        data = json.loads(fz.read().decode("utf-8"))
    return data

# Fonction qui permet de télécharger le fichier file depuis l'url
def download(url,file):
  import os.path
  if not os.path.isfile(file):
        print("File", file, "not found, I am downloading it...", end="")
        import urllib.request 
        urllib.request.urlretrieve (url, file)
        print(" Done")
        
        
def summary_of_example(data, sample_nb):
    ''' Gives you some insights about a sample number'''
    sample = data[sample_nb]
    print("Sample", sample_nb)
    print()
    print("Données brutes en format JSON:", sample)
    print()
    print("The sample was obtained after", sample["depth"], "moves")
    print("The successive moves were", sample["list_of_moves"])
    print("After these moves and all the captures, there was black stones at the following position", sample["black_stones"])
    print("After these moves and all the captures, there was white stones at the following position", sample["white_stones"])
    print("Number of rollouts (gnugo games played against itself from this position):", sample["rollouts"])
    print("Over these", sample["rollouts"], "games, black won", sample["black_wins"], "times with", sample["black_points"], "total points over all these winning games")
    print("Over these", sample["rollouts"], "games, white won", sample["white_wins"], "times with", sample["white_points"], "total points over all these winning games")
    
    
def build_dataset(data, board_size):
    
    N_EXAMPLES = len(data)
    
    # 3 feature maps :
    #   - Map 0 : pierres du joueur ami
    #   - Map 1 : pierres du joueur ennemi
    #   - Map 2 : joueur courant
    
    X = np.zeros([N_EXAMPLES, 3, board_size, board_size], dtype = 'int8')
    
    for i in range(N_EXAMPLES):
        
        # Détermine la couleur des joueurs ami et ennemi
        if data[i]['depth'] % 2 == 0:
            ami = 'black_stones'
            ennemi = 'white_stones'
        else:
            ami = 'white_stones'
            ennemi = 'black_stones'
            
        # Map 0 : 1 si pierre du joueur ami, 0 sinon
        for stone in data[i][ami]:
            (col, lin) = Goban.Board.name_to_coord(stone)
            X[i][0][col][lin] = 1

        # Map 1 : 1 si pierre du joueur ennemi, 0 sinon
        for stone in data[i][ennemi]:
            (col, lin) = Goban.Board.name_to_coord(stone)
            X[i][1][col][lin] = 1
            
        # Map 2 : 1 si le joueur ami est 'black', 0 sinon
        if ami == 'black_stones':
            for col in range(board_size):
                for lin in range(board_size):
                    X[i][2][col][lin] = 1
                    
    return X
    
def get_winning_priors(data):
    
    N_EXAMPLES = len(data)
    
    # Probabilité de gagner pour le joueur courant
    Y = np.zeros([N_EXAMPLES], dtype = float)
    
    for i in range(N_EXAMPLES):
        
        if data[i]['depth'] % 2 == 0:
            Y[i] = data[i]['black_wins'] / data[i]['rollouts']
        else:
            Y[i] = data[i]['white_wins'] / data[i]['rollouts']
    
    return Y
       
    
# ROTATIONS ET SYMETRIES
def enlarge_dataset(X, Y):
    
    enlarged_X = np.copy(X)
    enlarged_Y = np.copy(Y)
    
    N_EXAMPLES = len(X)
    
    for i in range(N_EXAMPLES):
        
        rot_sym = rot_flip(X[i])
        
        # On ajoute les rotations et symétries du plateau i à la fin
        enlarged_X = np.append(enlarged_X, rot_sym, axis = 0)
        
        # On ajoute le label des rotations et symétries du plateau i : même label
        for k in range(7):
            enlarged_Y = np.append(enlarged_Y, Y[i])
            
    return enlarged_X, enlarged_Y
        

# Crée les rotations et symétries d'un example
def rot_flip(sample):
    
    shape = sample.shape # = (3, 9, 9)
    
    # Pour un plateau, on ajoute les 7 rotations et symétries existantes
    # toret.shape = (7, 3, 9, 9)
    toret = np.zeros([7, shape[0], shape[1], shape[2]], dtype = 'int8')
    
    # Ajout des 3 rotations de 90° des plateaux
    for k in range(0, 3):
        rot = np.empty(shape, dtype = 'int8')
        
        # Pour chaque feature map du sample (3)
        for i in range(shape[0]):
            
            rot[i] = np.rot90(sample[i], k + 1, axes=(0, 1))
            
        toret[k] = rot
        
    # Ajout des symétries verticales de chaque rotation + du sample
    for k in range(0, 4):
        sym = np.empty(shape, dtype = 'int8')
        
        for i in range(shape[0]):
            
            # symétrie du sample d'origine
            if k == 3:
                sym[i] = np.flipud(sample[i])
                
            # symétries des rotations de 90° calculées
            else:
                sym[i] = np.flipud(toret[k][i])
        
        toret[3 + k] = sym
    
    return toret
        
    
