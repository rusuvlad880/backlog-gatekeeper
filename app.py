import customtkinter as ctk
import database
import requests
import io
from PIL import Image


#Set the overall theme and color of the app

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

#Create the main window

app = ctk.CTk()
app.geometry ("1000x650")
app.title("Backlog Gatekeeper")

login_screen = ctk.CTkFrame(app, fg_color="transparent")
dashboard_screen = ctk.CTkFrame(app, fg_color="transparent")

current_image_url = ""

# SCREEN 1: LOGIN

login_box = ctk.CTkFrame(login_screen, width=400, height=500)
login_box.pack(expand=True)

login_title = ctk.CTkLabel(login_box, text="Gatekeeper Acces", font=("Arial", 28, "bold"))
login_title.pack(pady=(40, 20))

email_entry = ctk.CTkEntry(login_box, placeholder_text="Email Address", width=250)
email_entry.pack(pady=10)

password_entry = ctk.CTkEntry(login_box, placeholder_text="Password", show="*", width=250)
password_entry.pack(pady=10)

error_label = ctk.CTkLabel(login_box, text="", text_color="red")
error_label.pack()

def handle_auth(action):
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        error_label.configure(text="Please fill in both fields.")
        return
    
    try:
        if action == "login":
            database.login_user(email, password)
        elif action == "register":
            database.register_user(email, password)

        login_screen.pack_forget()
        dashboard_screen.pack(fill="both", expand=True)
        load_games()

    except Exception as e:
        print(f"Auth Error: {e}")
        error_label.configure(text="Authentication Failed. Try again.")

login_btn = ctk.CTkButton(login_box, text="Login", command=lambda: handle_auth("login"), width=250)
login_btn.pack(pady=(20, 10))

register_btn = ctk.CTkButton(login_box, text="Create Account", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: handle_auth("register"), width=250)
register_btn.pack(pady=(0, 40))

# SCREEN 2 DASHBOARD

sidebar = ctk.CTkFrame(dashboard_screen, width=250, corner_radius=0)
sidebar.pack(side="left", fill="y")

sidebar_title = ctk.CTkLabel(sidebar, text="Add New Game", font=("Arial", 20, "bold"))
sidebar_title.pack(pady=(30, 10))

steam_search_entry = ctk.CTkEntry(sidebar, placeholder_text="Search Steam...", width=200)
steam_search_entry.pack(pady=5)

def perform_steam_search():
    global current_image_url

    search_term = steam_search_entry.get()
    if not search_term:
        print("Please type a new game to search!")
        return
    
    try:
        url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US"
        response = requests.get(url)
        data = response.json()

        if data.get('items'):

            top_game = data['items'][0]
            
            title_entry.delete(0, ctk.END)
            title_entry.insert(0, top_game.get('name', 'Unknown'))
            
            platform_entry.delete(0, ctk.END)
            platform_entry.insert(0, "PC (Steam)")

            current_image_url = top_game.get('tiny_image', "")
            
            print(f"Grabbed Image URL: {current_image_url}")

            steam_search_entry.delete(0, ctk.END)
            print(f"Magic Auto-Fill Success: {top_game}")
        else:
            print("No games found on Steam.")
            
    except Exception as e:
        print(f"Steam API Error: {e}")

steam_btn = ctk.CTkButton(sidebar, text="Auto-Fill from Steam", command=perform_steam_search, width=200, fg_color="#171A21", hover_color="#2A475E")
steam_btn.pack(pady=(0, 20))

title_entry = ctk.CTkEntry(sidebar, placeholder_text="Game Title", width=200)
title_entry.pack(pady=10)

platform_entry = ctk.CTkEntry(sidebar, placeholder_text="Platform (e.g., PC)", width=200)
platform_entry.pack(pady=10)

status_dropdown = ctk.CTkOptionMenu(sidebar, values=["Backlog", "Playing", "Finished"], width=200)
status_dropdown.pack(pady=10)
status_dropdown.set("Backlog")

def save_button_clicked():
    global current_image_url # <--- 1. We tell the save button to grab the ghost variable!
    
    title = title_entry.get()
    platform = platform_entry.get()
    status = status_dropdown.get()
    
    if title and platform and status:
        try:
            # 2. We pass ALL 4 pieces of info to the database!
            database.add_game(title, platform, status, current_image_url)
            
            print(f"Success! Saved {title} to the cloud with its image.")
            
            title_entry.delete(0, ctk.END)
            platform_entry.delete(0, ctk.END)
            status_dropdown.set("Backlog")
            
            current_image_url = "" # 3. Wipe the variable clean for the next game!
            load_games()
        except Exception as e:
            print(f"DATABASE ERROR: {e}") 
    else:
        print("Please fill out all boxes.")

save_btn = ctk.CTkButton(sidebar, text="Save to Backlog", command=save_button_clicked, width=200)
save_btn.pack(pady=20)

def change_theme_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)

theme_option_menu = ctk.CTkOptionMenu(sidebar, values=["System", "Dark", "Light"], command=change_theme_event)
theme_option_menu.pack(side="bottom", pady=(0, 20))

theme_label = ctk.CTkLabel(sidebar, text="Theme Preferences:")
theme_label.pack(side="bottom", pady=(0, 5))
theme_option_menu.set("System")

main_area = ctk.CTkFrame(dashboard_screen, fg_color="transparent")
main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

dashboard_title = ctk.CTkLabel(main_area, text="My Digital Shelf", font=("Arial", 32, "bold"))
dashboard_title.pack(anchor="w", pady=(0, 20))

tabview = ctk.CTkTabview(main_area)
tabview.pack(fill="both", expand=True)

tab_backlog = tabview.add("Backlog")
tab_playing = tabview.add("Playing")
tab_finished = tabview.add("Finished")

scroll_frames = {
    "Backlog": ctk.CTkScrollableFrame(tab_backlog, fg_color="transparent"),
    "Playing": ctk.CTkScrollableFrame(tab_playing, fg_color="transparent"),
    "Finished": ctk.CTkScrollableFrame(tab_finished, fg_color="transparent")
}

for frame in scroll_frames.values():
    frame.pack(fill="both", expand=True)

def change_status(game_id, new_status):
    database.update_game_status(game_id, new_status)
    load_games()

def remove_game(game_id):
    database.delete_game(game_id)
    load_games()

def load_games():

    for frame in scroll_frames.values():
        for widget in frame.winfo_children():
            widget.destroy()

    games = database.get_all_games()

    for game in games:
        # Unpack the data
        game_id, title, platform, status, img_link = game[0], game[1], game[2], game[3], game[4]
        
        if status not in scroll_frames:
            status = "Backlog"
            
        # STEP 1: BUILD THE BOX FIRST! (Python needs this to exist before putting things inside)
        row_frame = ctk.CTkFrame(scroll_frames[status])
        row_frame.pack(fill="x", pady=5)
        
        # STEP 2: LOAD AND ATTACH THE IMAGE
        if img_link: 
            try:
                img_data = requests.get(img_link).content 
                img = Image.open(io.BytesIO(img_data)) 
                ctk_img = ctk.CTkImage(img, size=(120, 45)) 
                
                img_label = ctk.CTkLabel(row_frame, image=ctk_img, text="")
                img_label.image = ctk_img # The Magic Anchor!
                img_label.pack(side="left", padx=(10, 0), pady=10)
            except Exception as e:
                print(f"Failed to load image for {title}: {e}")
        
        # STEP 3: ATTACH THE TEXT
        label = ctk.CTkLabel(row_frame, text=f"{title}  |  {platform}", font=("Arial", 16))
        label.pack(side="left", padx=20, pady=10)
        
        # STEP 4: ATTACH THE SMART BUTTONS
        if status == "Backlog":
            btn = ctk.CTkButton(row_frame, text="Start Playing", width=100, fg_color="#2E7D32", hover_color="#1B5E20", command=lambda id=game_id: change_status(id, "Playing"))
        elif status == "Playing":
            btn = ctk.CTkButton(row_frame, text="Finish Game", width=100, fg_color="#1565C0", hover_color="#0D47A1", command=lambda id=game_id: change_status(id, "Finished"))
        elif status == "Finished":
            btn = ctk.CTkButton(row_frame, text="Delete", width=80, fg_color="#C62828", hover_color="#B71C1C", command=lambda id=game_id: remove_game(id))
            
        btn.pack(side="right", padx=20)

# START APP

login_screen.pack(fill="both", expand=True)

if __name__ == "__main__":
    app.mainloop()
