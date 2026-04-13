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

def add_game(title, platform, status, image_url=""): # <-- Added image_url here!
    user_id = get_current_user_id()
    supabase.table("games").insert({
        "title": title, 
        "platform": platform, 
        "status": status,
        "user_id": user_id,
        "image_url": image_url # <-- Tell Supabase to save the picture link!
    }).execute()

def get_all_games():
    user_id = get_current_user_id()
    response = supabase.table("games").select("*").eq("user_id", user_id).execute()
    
    games_list = []
    for row in response.data:
        # We now grab the image_url from the cloud. If an old game doesn't have one, we just use ""
        img_link = row.get('image_url', "") 
        if img_link is None:
            img_link = ""
            
        games_list.append((row['id'], row['title'], row['platform'], row['status'], img_link))
    return games_list

def delete_game(game_id):

    supabase.table("games").delete().eq("id", game_id).execute()

def update_game_status(game_id, new_status):

    supabase.table("games").update({"status": new_status}).eq("id", game_id).execute()

def get_profile():
    try:
        # Ask Supabase directly who is logged in!
        user = supabase.auth.get_user().user
        if not user:
            return None
            
        # Check if a profile exists for this specific user ID
        response = supabase.table("profiles").select("*").eq("user_id", user.id).execute()
        if response.data:
            return response.data[0] # Return the profile data
        return None
    except Exception as e:
        print(f"Database Error (Get Profile): {e}")
        return None

def create_profile(username):
    try:
        # Ask Supabase directly who is logged in!
        user = supabase.auth.get_user().user
        if not user:
            return False
            
        # Save the new username to the vault linked to their ID!
        data = {"user_id": user.id, "username": username}
        supabase.table("profiles").insert(data).execute()
        return True
    except Exception as e:
        print(f"Database Error (Create Profile): {e}")
        return False
    
def search_users(search_query):
    try:
        # We use .ilike() so it finds the username even if you don't capitalize it perfectly!
        response = supabase.table("profiles").select("*").ilike("username", f"%{search_query}%").execute()
        
        # We need to filter out YOUR profile, so you don't accidentally send a friend request to yourself!
        user = supabase.auth.get_user().user
        results = [p for p in response.data if p['user_id'] != user.id]
        return results
    except Exception as e:
        print(f"Database Error (Search Users): {e}")
        return []

def send_friend_request(friend_id):
    try:
        user = supabase.auth.get_user().user
        # Write the request into the ledger!
        data = {"user_id": user.id, "friend_id": friend_id, "status": "pending"}
        supabase.table("friends").insert(data).execute()
        return True
    except Exception as e:
        print(f"Database Error (Send Request): {e}")
        return False
    
def search_users(search_query):
    try:
        response = supabase.table("profiles").select("*").ilike("username", f"%{search_query}%").execute()
        user = supabase.auth.get_user().user
        results = [p for p in response.data if p['user_id'] != user.id]
        return results
    except Exception as e:
        print(f"Database Error (Search Users): {e}")
        return []
    
def send_friend_request(friend_id):
    try:
        user = supabase.auth.get_user().user
        # Write the request into the ledger!
        data = {"user_id": user.id, "friend_id": friend_id, "status": "pending"}
        supabase.table("friends").insert(data).execute()
        return True
    except Exception as e:
        print(f"Database Error (Send Request): {e}")
        return False

def get_pending_requests():
    try:
        user = supabase.auth.get_user().user
        if not user: return []

        # 1. Ask the ledger for all pending requests sent TO me
        response = supabase.table("friends").select("*").eq("friend_id", user.id).eq("status", "pending").execute()
        
        # 2. Match those requests with the person's Username!
        inbox = []
        for req in response.data:
            prof = supabase.table("profiles").select("username").eq("user_id", req['user_id']).execute()
            username = prof.data[0]['username'] if prof.data else "Unknown Player"
            inbox.append({
                "request_id": req['id'],
                "username": username
            })
        return inbox
    except Exception as e:
        print(f"Database Error (Get Requests): {e}")
        return []

def accept_friend_request(request_id):
    try:
        # Flip the status from 'pending' to 'accepted' in the vault!
        supabase.table("friends").update({"status": "accepted"}).eq("id", request_id).execute()
        return True
    except Exception as e:
        print(f"Database Error (Accept Request): {e}")
        return False

def get_friends_list():
    try:
        user = supabase.auth.get_user().user
        if not user: return []

        # 1. Ask the ledger for all 'accepted' friendships
        response = supabase.table("friends").select("*").eq("status", "accepted").execute()
        
        friends_list = []
        seen_ids = set() # <--- THE MAGIC SHIELD: Remembers who we already added
        
        for relation in response.data:
            # Figure out which ID is the friend
            if str(relation['user_id']) == str(user.id):
                other_id = relation['friend_id'] 
            else:
                other_id = relation['user_id']
                
            # 🛡️ THE CHECK: If we already drew this friend, skip to the next one!
            if other_id in seen_ids:
                continue
                
            seen_ids.add(other_id) # Mark this friend as "seen"
            
            # Grab their Username
            prof = supabase.table("profiles").select("username").eq("user_id", other_id).execute()
            
            if prof.data:
                username = prof.data[0]['username']
            else:
                username = "Unknown Player"
            
            friends_list.append({
                "friend_id": other_id,
                "username": username
            })
            
        return friends_list
    except Exception as e:
        print(f"Database Error (Get Friends): {e}")
        return []

if __name__ == '__main__':
    print("Cloud database script ready!")