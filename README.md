
Entreprises - Agriculture et sylviculture - Mons




# GDriveList


Voici le code Python complet et corrigé pour lister les fichiers partagés sur Google Drive dans Google Colab, avec une interface interactive en forme de terminal et un affichage en tableau. Ce script authentifie l'utilisateur, permet de choisir entre lister tous les fichiers partagés ou ceux d'un dossier spécifique, et affiche les résultats de manière claire.
Instructions préalables

Avant d'exécuter le script dans Google Colab, vous devez :

    Installer les dépendances nécessaires en exécutant la commande suivante dans une cellule séparée :
    bash

    !pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas tabulate inquirer colorama humanize
    Uploader le fichier credentials.json dans l'environnement Colab :
        Cliquez sur l'icône de dossier dans la barre latérale gauche de Colab.
        Faites glisser ou uploadez le fichier credentials.json obtenu depuis Google Cloud Console.

Code complet

Voici le script Python amélioré :
python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd
import sys
from tabulate import tabulate
import inquirer
from colorama import init, Fore, Style
import humanize

# Initialisation de colorama pour les couleurs dans le terminal
init()

# Scopes pour accéder à Google Drive en lecture seule
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive():
    """Authentification à Google Drive avec gestion des erreurs"""
    creds = None
    token_file = 'token.pickle'

    # Vérifie si un token existe déjà
    if os.path.exists(token_file):
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(Fore.RED + f"Erreur lors de la lecture du token: {str(e)}" + Style.RESET_ALL)
            if os.path.exists(token_file):
                os.remove(token_file)

    # Si pas de credentials valides, authentification ou rafraîchissement
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(Fore.RED + f"Erreur lors du rafraîchissement du token: {str(e)}" + Style.RESET_ALL)
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                # Utilisation de run_console() pour Google Colab
                creds = flow.run_console()
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(Fore.RED + f"Erreur d'authentification: {str(e)}" + Style.RESET_ALL)
                print("\nAssurez-vous que :")
                print("1. Votre compte email est ajouté comme utilisateur de test dans Google Cloud")
                print("2. L'API Google Drive est activée dans votre projet")
                print("3. Le fichier 'credentials.json' est présent")
                sys.exit(1)

    return build('drive', 'v3', credentials=creds)

def list_shared_files(service, folder_id=None):
    """Liste les fichiers partagés sur Google Drive, optionnellement dans un dossier spécifique"""
    results = []
    page_token = None

    while True:
        try:
            # Requête adaptée selon si un dossier spécifique est choisi
            if folder_id:
                query = f"'{folder_id}' in parents"
            else:
                query = "sharedWithMe=true"

            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, size, modifiedTime, sharingUser)',
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                file_type = 'Dossier' if file.get('mimeType') == 'application/vnd.google-apps.folder' else 'Fichier'
                size = humanize.naturalsize(file.get('size', 0)) if 'size' in file else 'N/A'
                results.append({
                    'Nom': file.get('name'),
                    'Type': file_type,
                    'Taille': size,
                    'ID': file.get('id'),
                    'Partagé par': file.get('sharingUser', {}).get('displayName', 'N/A'),
                    'Dernière modification': datetime.fromisoformat(file.get('modifiedTime').replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                })

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        except Exception as e:
            print(Fore.RED + f"Une erreur est survenue: {str(e)}" + Style.RESET_ALL)
            break

    return results

def main():
    """Fonction principale avec interface interactive"""
    print(Fore.GREEN + "Authentification à Google Drive..." + Style.RESET_ALL)
    try:
        service = authenticate_google_drive()

        # Interface interactive avec inquirer
        questions = [
            inquirer.List('action',
                          message="Que voulez-vous faire ?",
                          choices=['Lister tous les fichiers partagés', 'Lister les fichiers dans un dossier spécifique'],
                          ),
        ]
        answers = inquirer.prompt(questions)

        if answers['action'] == 'Lister tous les fichiers partagés':
            print(Fore.GREEN + "Récupération de tous les fichiers partagés..." + Style.RESET_ALL)
            shared_files = list_shared_files(service)
        else:
            folder_id = input("Entrez l'ID du dossier : ")
            print(Fore.GREEN + f"Récupération des fichiers dans le dossier {folder_id}..." + Style.RESET_ALL)
            shared_files = list_shared_files(service, folder_id)

        # Affichage des résultats dans un tableau
        if shared_files:
            df = pd.DataFrame(shared_files)
            print(Fore.GREEN + "\nRésultats :" + Style.RESET_ALL)
            print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        else:
            print(Fore.YELLOW + "Aucun fichier trouvé." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Une erreur est survenue: {str(e)}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
Explications des fonctionnalités

    Authentification :
        Utilise flow.run_console() pour une authentification adaptée à Google Colab.
        Sauvegarde les informations d'authentification dans token.pickle pour éviter de se reconnecter à chaque exécution (bien que dans Colab, ce fichier soit temporaire).
    Lister les fichiers :
        Tous les fichiers partagés : Utilise la requête sharedWithMe=true pour lister les fichiers directement partagés avec vous.
        Dossier spécifique : Utilise "'{folder_id}' in parents" pour lister les fichiers dans un dossier donné, sans filtre supplémentaire, ce qui permet d'accéder aux contenus des dossiers partagés.
    Affichage :
        Les résultats sont affichés dans un tableau clair avec tabulate.
        Les tailles de fichiers sont rendues lisibles avec humanize.
        Les couleurs (via colorama) améliorent la lisibilité dans le terminal.
    Interface interactive :
        Utilise inquirer pour proposer un menu simple permettant de choisir entre lister tous les fichiers ou ceux d'un dossier spécifique.

Comment utiliser ce script dans Colab

    Créez une nouvelle cellule dans votre notebook Colab et exécutez la commande !pip install mentionnée ci-dessus.
    Uploadez le fichier credentials.json dans l'environnement Colab.
    Copiez et collez le script ci-dessus dans une nouvelle cellule, puis exécutez-la.
    Suivez les instructions d'authentification (copiez le lien fourni, connectez-vous, et collez le code généré).
    Choisissez une option dans le menu interactif et, si nécessaire, entrez un ID de dossier.

Remarques

    Si vous entrez un ID de dossier invalide ou auquel vous n'avez pas accès, une erreur sera affichée.
    Pour trouver l'ID d'un dossier, ouvrez-le dans Google Drive via le navigateur, et l'ID est la partie de l'URL après /folders/.

Ce script devrait maintenant fonctionner parfaitement dans Google Colab. Si vous avez des questions ou besoin d'améliorations supplémentaires, n'hésitez pas !
