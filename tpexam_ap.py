import json
import os
import datetime
import csv
import threading
import time

def charger_utilisateurs(fichier='utilisateurs.json'):
    """Charge les données des utilisateurs à partir d'un fichier JSON."""
    if os.path.exists(fichier):
        with open(fichier, 'r') as file:
            return json.load(file)
    return {}

def enregistrer_utilisateurs(utilisateurs, fichier='utilisateurs.json'):
    """Enregistre les données des utilisateurs dans un fichier JSON."""
    with open(fichier, 'w') as file:
        json.dump(utilisateurs, file, indent=4)

def creer_profil_utilisateur(utilisateurs):
    """Crée ou récupère un profil utilisateur."""
    identifiant = input("Entrez votre identifiant : ")
    if identifiant in utilisateurs:
        print(f"\nBienvenue de retour, {identifiant} ! Voici votre historique de QCM :")
        afficher_historique(identifiant, utilisateurs)
    else:
        print(f"\nBienvenue, {identifiant} ! Votre profil a été créé.")
        utilisateurs[identifiant] = {'historique': []}
    return identifiant

def afficher_historique(identifiant, utilisateurs):
    """Affiche l'historique des QCM d'un utilisateur."""
    historique = utilisateurs.get(identifiant, {}).get('historique', [])
    if historique:
        print("\nHistorique des QCM :")
        for entree in historique:
            print(f"Date : {entree['date']} - Score : {entree['score']}")
    else:
        print("\nAucun historique disponible.")



def afficher_chronometre(temps, chrono_event, question):
    """Affiche un chronomètre qui décrémente le temps restant."""
    while temps > 0 and not chrono_event.is_set() :
        print(f"\rTemps restant: {temps} secondes                                          ", end="", flush=True)
        time.sleep(1)
        temps -= 1
        
    if  not chrono_event.is_set():
        print("\rTemps écoulé !               ")
        print(f"La réponse juste était : {question['reponse_correcte']}")
        chrono_event.set()


def poser_questions(questions, temps_par_question, identifiant, utilisateurs):
    """Pose les questions à l'utilisateur avec une limite de temps pour chaque question."""
    score = 0
    for question in questions:
        print(f"\n{question['question']}")
        for i, option in enumerate(question['options'], 1):
            print(f"{i}. {option}")

        chrono_event = threading.Event()
        chrono_thread = threading.Thread(
            target=afficher_chronometre, args=(temps_par_question, chrono_event, question)
        )
        chrono_thread.start()

        reponse = None
        try:
            
            reponse = input("   Votre réponse (entrez le numéro ou -1 pour quitter) :  ").strip()
        except Exception:
            pass

        chrono_event.set()
        chrono_thread.join()

        if not reponse and chrono_event.is_set():
            # Temps écoulé, la réponse correcte a déjà été affichée dans le chronomètre.
            continue

        if reponse == "-1":
            date_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            utilisateurs[identifiant]['historique'].append({'date': date_actuelle, 'score': 'Abandonne'})
            enregistrer_utilisateurs(utilisateurs)
            print("\nVous avez choisi de quitter. Votre progression a été enregistrée.")
            return score
            

        if reponse and reponse.isdigit() and 1 <= int(reponse) <= len(question['options']):
            choix = int(reponse) - 1
            if question['options'][choix] == question['reponse_correcte']:
                print("Bonne réponse !")
                score += 1
            else:
                print(f"Mauvaise réponse. La bonne réponse était : {question['reponse_correcte']}")
        else:
            print("Réponse invalide. Question ignorée.")
    return score





def enregistrer_resultat(identifiant, utilisateurs, score):
    """Enregistre le résultat d'un QCM pour un utilisateur."""
    date_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    utilisateurs[identifiant]['historique'].append({'date': date_actuelle, 'score': score})
    enregistrer_utilisateurs(utilisateurs)
    print(f"\nVotre score final est : {score}")

def exporter_resultats_csv(identifiant, utilisateurs):
    """Exporte les résultats d'un utilisateur dans un fichier CSV."""
    nom_fichier = f"{identifiant}_resultats.csv"
    with open(nom_fichier, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Score"])
        for entree in utilisateurs[identifiant]['historique']:
            writer.writerow([entree['date'], entree['score']])
    print(f"\nLes résultats ont été exportés dans {nom_fichier}.")

def lancer_qcm():
    """Lance l'application de QCM."""
    utilisateurs = charger_utilisateurs()
    identifiant = creer_profil_utilisateur(utilisateurs)

    categories = {
        '1': 'Programmation',
        '2': 'Réseaux',
        '3': 'Culture Générale'
    }

    questions_par_categorie = {
         'Programmation': [
        # Questions sur la programmation
        {'question': "Quelle est la fonction pour afficher un message en Python?", 'options': ["print()", "echo()", "show()", "output()"], 'reponse_correcte': "print()"},
        {'question': "Quel type de données est renvoyé par `len()` en Python?", 'options': ["int", "str", "list", "float"], 'reponse_correcte': "int"},
        {'question': "Quelle méthode est utilisée pour ajouter un élément à une liste?", 'options': ["add()", "insert()", "append()", "push()"], 'reponse_correcte': "append()"},
        {'question': "Comment appelle-t-on une fonction qui s'appelle elle-même?", 'options': ["Itérative", "Récursive", "Anonyme", "Générique"], 'reponse_correcte': "Récursive"},
        {'question': "Quel mot-clé est utilisé pour définir une fonction en Python?", 'options': ["function", "def", "fun", "declare"], 'reponse_correcte': "def"},
        {'question': "Comment déclare-t-on une variable globale en Python?", 'options': ["global var_name", "var_name global", "global: var_name", "declare global var_name"], 'reponse_correcte': "global var_name"},
        {'question': "Quelle est la méthode pour obtenir la longueur d'une chaîne de caractères en Python?", 'options': ["length()", "len()", "size()", "str_len()"], 'reponse_correcte': "len()"},
        {'question': "Que signifie `PEP` en Python?", 'options': ["Python Execution Protocol", "Python Enhancement Proposal", "Programming Execution Plan", "Process Extension Plan"], 'reponse_correcte': "Python Enhancement Proposal"},
        {'question': "Quelle bibliothèque Python est utilisée pour le traitement de données?", 'options': ["NumPy", "DataHandler", "SciKit", "Pandas"], 'reponse_correcte': "Pandas"},
        {'question': "Quelle est la structure de données LIFO?", 'options': ["Queue", "Deque", "Stack", "Priority Queue"], 'reponse_correcte': "Stack"},
        {'question': "Quelle est la valeur par défaut de l'argument `end` dans `print()`?", 'options': ["''", "' '", "'\\n'", "'\\t'"], 'reponse_correcte': "'\\n'"},
        {'question': "Quel module Python permet de gérer les fichiers JSON?", 'options': ["json", "filejson", "os", "csv"], 'reponse_correcte': "json"},
        {'question': "Que renvoie `type(42.0)`?", 'options': ["<class 'int'>", "<class 'float'>", "<class 'complex'>", "<class 'decimal'>"], 'reponse_correcte': "<class 'float'>"},
        {'question': "Quelle est la sortie de `print(2**3)`?", 'options': ["6", "8", "9", "16"], 'reponse_correcte': "8"},
        {'question': "Quelle méthode est utilisée pour diviser une chaîne par un délimiteur en Python?", 'options': ["split()", "divide()", "tokenize()", "parse()"], 'reponse_correcte': "split()"},
        {'question': "Quel est le symbole utilisé pour un commentaire en Python?", 'options': ["//", "#", "--", "/*"], 'reponse_correcte': "#"},
        {'question': "Quelle commande est utilisée pour installer des bibliothèques Python?", 'options': ["install library", "pip install", "python install", "lib add"], 'reponse_correcte': "pip install"},
        {'question': "Comment convertit-on une chaîne de caractères en entier?", 'options': ["int()", "convert()", "to_int()", "str_to_int()"], 'reponse_correcte': "int()"},
        {'question': "Quel est le mot-clé pour capturer les exceptions?", 'options': ["catch", "except", "try", "throw"], 'reponse_correcte': "except"},
        {'question': "Quel est l'opérateur de division entière en Python?", 'options': ["%", "//", "/", "**"], 'reponse_correcte': "//"}
      ],
         
         'Réseaux': [
        {'question': "Qu'est-ce qu'une adresse IP?", 'options': ["Identifiant unique d'un ordinateur sur un réseau", "Nom d'un site web", "Type de réseau", "Protocole de communication"], 'reponse_correcte': "Identifiant unique d'un ordinateur sur un réseau"},
        {'question': "Quel protocole est utilisé pour envoyer des emails?", 'options': ["HTTP", "SMTP", "FTP", "SNMP"], 'reponse_correcte': "SMTP"},
        {'question': "Que signifie le terme DNS?", 'options': ["Domain Name System", "Data Network Service", "Direct Name Server", "Dynamic Network Sharing"], 'reponse_correcte': "Domain Name System"},
        {'question': "Quel est le port standard pour HTTP?", 'options': ["80", "443", "21", "25"], 'reponse_correcte': "80"},
        {'question': "Quelle couche du modèle OSI gère les adresses MAC?", 'options': ["Application", "Transport", "Liaison de données", "Réseau"], 'reponse_correcte': "Liaison de données"},
        {'question': "Quel protocole est utilisé pour sécuriser les communications sur Internet?", 'options': ["HTTP", "HTTPS", "FTP", "SMTP"], 'reponse_correcte': "HTTPS"},
        {'question': "Qu'est-ce qu'un VPN?", 'options': ["Virtual Private Network", "Virtual Public Network", "Verified Private Network", "Verified Public Network"], 'reponse_correcte': "Virtual Private Network"},
        {'question': "Quelle est la taille d'une adresse IPv4?", 'options': ["16 bits", "32 bits", "64 bits", "128 bits"], 'reponse_correcte': "32 bits"},
        {'question': "Quel protocole est utilisé pour la résolution des noms de domaine?", 'options': ["DNS", "DHCP", "IP", "HTTP"], 'reponse_correcte': "DNS"},
        {'question': "Quelle est la fonction du DHCP?", 'options': ["Attribuer des adresses IP dynamiques", "Gérer les connexions VPN", "Transférer des fichiers", "Établir des tunnels sécurisés"], 'reponse_correcte': "Attribuer des adresses IP dynamiques"},
        {'question': "Que signifie le terme NAT dans les réseaux?", 'options': ["Network Address Translation", "Network Access Time", "Node Access Translation", "Network Allocation Table"], 'reponse_correcte': "Network Address Translation"},
        {'question': "Quelle est la différence entre TCP et UDP?", 'options': ["TCP est fiable, UDP ne l'est pas", "UDP est plus lent que TCP", "TCP est utilisé pour la vidéo", "UDP est utilisé pour les emails"], 'reponse_correcte': "TCP est fiable, UDP ne l'est pas"},
        {'question': "Qu'est-ce qu'une adresse MAC?", 'options': ["Adresse physique d'un appareil", "Adresse IP d'un réseau", "Adresse d'un site web", "Protocole réseau"], 'reponse_correcte': "Adresse physique d'un appareil"},
        {'question': "Que signifie HTTP?", 'options': ["HyperText Transfer Protocol", "HyperText Transmission Protocol", "Host Transfer Protocol", "HyperText Transaction Protocol"], 'reponse_correcte': "HyperText Transfer Protocol"},
        {'question': "Quel est le port standard pour HTTPS?", 'options': ["80", "443", "21", "8080"], 'reponse_correcte': "443"},
        {'question': "Que signifie le terme LAN?", 'options': ["Local Area Network", "Large Access Node", "Linked Area Network", "Limited Access Network"], 'reponse_correcte': "Local Area Network"},
        {'question': "Que fait un routeur?", 'options': ["Connecte différents réseaux entre eux", "Attribue des adresses IP dynamiques", "Contrôle l'accès à Internet", "Transfère des fichiers entre ordinateurs"], 'reponse_correcte': "Connecte différents réseaux entre eux"},
        {'question': "Quelle commande est utilisée pour vérifier la connectivité réseau?", 'options': ["ping", "traceroute", "netstat", "ifconfig"], 'reponse_correcte': "ping"},
        {'question': "Qu'est-ce qu'un réseau pair-à-pair (P2P)?", 'options': ["Un réseau où chaque appareil peut agir comme client ou serveur", "Un réseau centralisé", "Un réseau pour les grands serveurs", "Un réseau utilisé uniquement pour les jeux"], 'reponse_correcte': "Un réseau où chaque appareil peut agir comme client ou serveur"},
        {'question': "Quel est l'objectif principal du pare-feu?", 'options': ["Protéger le réseau contre les accès non autorisés", "Attribuer des adresses IP", "Connecter des appareils au réseau", "Gérer les serveurs web"], 'reponse_correcte': "Protéger le réseau contre les accès non autorisés"}
      ],
        'Culture Générale': [
        {'question': "Quel est le plus grand océan du monde?", 'options': ["Atlantique", "Pacifique", "Indien", "Arctique"], 'reponse_correcte': "Pacifique"},
        {'question': "Quelle est la capitale de l'Australie?", 'options': ["Sydney", "Melbourne", "Canberra", "Perth"], 'reponse_correcte': "Canberra"},
        {'question': "Quel est le symbole chimique de l'eau?", 'options': ["O", "H2", "H2O", "OH"], 'reponse_correcte': "H2O"},
        {'question': "Quel est le pays avec la plus grande population au monde?", 'options': ["Inde", "États-Unis", "Chine", "Indonésie"], 'reponse_correcte': "Chine"},
        {'question': "Quel est l'animal terrestre le plus rapide?", 'options': ["Lion", "Guépard", "Antilope", "Cheval"], 'reponse_correcte': "Guépard"},
        {'question': "Quelle planète est connue comme la planète rouge?", 'options': ["Mars", "Jupiter", "Vénus", "Mercure"], 'reponse_correcte': "Mars"},
        {'question': "Combien de couleurs y a-t-il dans un arc-en-ciel?", 'options': ["5", "6", "7", "8"], 'reponse_correcte': "7"},
        {'question': "Quel est le plus haut sommet du monde?", 'options': ["Mont Blanc", "Mont Everest", "Mont Kilimandjaro", "Mont Fuji"], 'reponse_correcte': "Mont Everest"},
        {'question': "Quel pays est connu pour la Tour Eiffel?", 'options': ["Italie", "France", "Espagne", "Allemagne"], 'reponse_correcte': "France"},
        {'question': "Quelle est la monnaie utilisée au Japon?", 'options': ["Yuan", "Yen", "Won", "Ringgit"], 'reponse_correcte': "Yen"},
        {'question': "Quel scientifique a découvert la loi de la gravité?", 'options': ["Albert Einstein", "Isaac Newton", "Galilée", "Copernic"], 'reponse_correcte': "Isaac Newton"},
        {'question': "Quel est le plus petit pays du monde?", 'options': ["Monaco", "Liechtenstein", "Vatican", "Malte"], 'reponse_correcte': "Vatican"},
        {'question': "Quelle est la langue officielle du Brésil?", 'options': ["Espagnol", "Portugais", "Français", "Anglais"], 'reponse_correcte': "Portugais"},
        {'question': "Quel continent est aussi un pays?", 'options': ["Australie", "Afrique", "Europe", "Asie"], 'reponse_correcte': "Australie"},
        {'question': "Quel sport est connu sous le nom de 'roi des sports'?", 'options': ["Basketball", "Football", "Tennis", "Cricket"], 'reponse_correcte': "Football"},
        {'question': "Dans quel pays se trouve la Statue de la Liberté?", 'options': ["Canada", "États-Unis", "Angleterre", "Australie"], 'reponse_correcte': "États-Unis"},
        {'question': "Quelle est la plus grande île du monde?", 'options': ["Madagascar", "Groenland", "Bornéo", "Islande"], 'reponse_correcte': "Groenland"},
        {'question': "Quel est le désert le plus chaud du monde?", 'options': ["Sahara", "Atacama", "Kalahari", "Gobi"], 'reponse_correcte': "Sahara"},
        {'question': "Combien de continents y a-t-il dans le monde?", 'options': ["5", "6", "7", "8"], 'reponse_correcte': "7"},
        {'question': "Quel est le nom de l'étoile la plus proche de la Terre?", 'options': ["Lune", "Soleil", "Sirius", "Alpha Centauri"], 'reponse_correcte': "Soleil"}
     ]      
    }

    print("\nChoisissez une catégorie :")
    for key, value in categories.items():
        print(f"{key}. {value}")

    choix = input("Entrez le numéro de la catégorie : ")
    categorie = categories.get(choix)

    if not categorie:
        print("Catégorie invalide. Retour au menu principal.")
        return

    print(f"\nVous avez choisi la catégorie : {categorie}")
    questions = questions_par_categorie[categorie]
    temps_par_question = 30  # Temps limite par question en secondes
    score = poser_questions(questions, temps_par_question, identifiant, utilisateurs)
    enregistrer_resultat(identifiant, utilisateurs, score)

    choix_exporter = input("Voulez-vous exporter vos résultats dans un fichier CSV ? (o/n) : ")
    if choix_exporter.lower() == 'o':
        exporter_resultats_csv(identifiant, utilisateurs)

# Lancer l'application
if __name__ == "__main__":
    lancer_qcm()
