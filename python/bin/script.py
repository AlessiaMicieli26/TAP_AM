import requests
import csv
import time
import json

# Funzioni per chiamare le API e ottenere i dati JSON con gestione degli errori
def get_user_signs(user_id):
    try:
        response = requests.get(f"https://spokelizard-server-production.up.railway.app/users/{user_id}/signs")
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Errore durante la richiesta dei segni dell'utente: {e}")
        return []

def get_games():
    try:
        response = requests.get("https://spokelizard-server-production.up.railway.app/games")
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Errore durante la richiesta dei giochi: {e}")
        return []

def get_user_win_signs(user_id):
    try:
        response = requests.get(f"https://spokelizard-server-production.up.railway.app/users/{user_id}/win-signs")
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Errore durante la richiesta dei segni vincenti dell'utente: {e}")
        return []

# Funzione per ottenere gli ID delle partite già scritte nel file CSV
def get_logged_game_ids(output_file):
    try:
        with open(output_file, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader, None)  # Salta l'intestazione
            logged_game_ids = {row[1] for row in csvreader}  # Colonna game_id è la seconda
        return logged_game_ids
    except FileNotFoundError:
        return set()

# Funzione principale per raccogliere i dati e scrivere in un file CSV
def fetch_and_write_data(user_id, output_file='../../logstash/api_data.csv'):
    user_signs_json = get_user_signs(user_id)
    games_json = get_games()
    user_win_signs_json = get_user_win_signs(user_id)

    if not games_json:
        print("Nessun gioco trovato.")
        return

    logged_game_ids = get_logged_game_ids(output_file)

    with open(output_file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Scrivere l'intestazione se il file è vuoto
        if csvfile.tell() == 0:
            csvwriter.writerow([
                "user_id", "game_id", "game_title", "player_ids", "created_at", 
                "winner_id", "winner_sign", "user_signs", "user_win_signs",
                "rock", "scissors", "paper"
            ])

        # Conta i win_signs per tipo di segno
        win_sign_counts = {"rock": 0, "scissors": 0, "paper": 0}
        for win_sign in user_win_signs_json:
            if win_sign in win_sign_counts:
                win_sign_counts[win_sign] += 1

        for game in games_json.get('games', []):
            game_id = game.get("gameID", "")
            if game_id in logged_game_ids:
                continue  # Salta le partite già registrate
            
            game_title = game.get("title", "")
            player_ids = ', '.join(game.get("playerIds", []))
            created_at = game.get("createdAt", "")
            
            for match in game.get("matches", []):
                match_winner = match.get("winner", None)
                if match_winner:
                    winner_id = match_winner.get("userId", "null")
                    winner_sign = match_winner.get("sign", "null")
                else:
                    winner_id = "null"
                    winner_sign = "null"

                # Scrivere i dati nel file CSV
                csvwriter.writerow([
                    user_id, game_id, game_title, player_ids, created_at, 
                    winner_id, winner_sign, ', '.join(user_signs_json), 
                    json.dumps(user_win_signs_json), 
                    win_sign_counts["rock"], win_sign_counts["scissors"], win_sign_counts["paper"]
                ])

if __name__ == "__main__":
    user_id = "4cf69226-b4cf-469c-9588-62c72a69915c"  # Esempio di user_id, può essere passato come argomento
    while True:
        fetch_and_write_data(user_id)
        time.sleep(30)
