from google.colab import auth
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd

def authenticate_google_drive():
    """Authentification à Google Drive"""
    auth.authenticate_user()
    return build('drive', 'v3')

def list_shared_files(service):
    """Liste tous les fichiers partagés sur Google Drive"""
    results = []
    page_token = None
    
    while True:
        try:
            # Recherche des fichiers partagés
            response = service.files().list(
                q="sharedWithMe=true",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, shared, sharingUser, modifiedTime)',
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                results.append({
                    'Nom': file.get('name'),
                    'Type': file.get('mimeType'),
                    'ID': file.get('id'),
                    'Partagé par': file.get('sharingUser', {}).get('displayName', 'N/A'),
                    'Dernière modification': datetime.fromisoformat(file.get('modifiedTime').replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
                
        except Exception as e:
            print(f"Une erreur est survenue: {str(e)}")
            break
    
    return results

def main():
    """Fonction principale"""
    print("Authentification à Google Drive...")
    service = authenticate_google_drive()
    
    print("Récupération des fichiers partagés...")
    shared_files = list_shared_files(service)
    
    # Création d'un DataFrame pandas pour un affichage plus élégant
    df = pd.DataFrame(shared_files)
    if not df.empty:
        print("\nFichiers partagés trouvés:")
        print(df)
    else:
        print("\nAucun fichier partagé trouvé.")

if __name__ == "__main__":
    main()