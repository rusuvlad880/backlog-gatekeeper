import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def register_user(email, password):
    
    response = supabase.auth.sign_up({"email": email, "password": password})
    return response

def login_user(email, password):
    
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return password

def get_current_user_id():

    user = supabase.auth.get_user()
    if user:
        return user.user.id
    return None

def create_table():
    pass

def add_game(title, platform, status):

    user_id = get_current_user_id()

    supabase.table("games").insert({
        "title": title, 
        "platform": platform, 
        "status": status,
        "user_id": user_id
    }).execute()

def get_all_games():
    user_id = get_current_user_id()

    response = supabase.table("games").select("*").eq("user_id", user_id).execute()

    games_list = []
    for row in response.data:
        games_list.append((row['id'], row['title'], row['platform'], row['status']))

    return games_list

def delete_game(game_id):

    supabase.table("games").delete().eq("id", game_id).execute()

if __name__ == '__main__':
    print("Cloud database script ready!")