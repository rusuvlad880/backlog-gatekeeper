import customtkinter as ctk
import database
import requests


#Set the overall theme and color of the app

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

#Create the main window

app = ctk.CTk()
app.geometry ("900x600")
app.title("Backlog Gatekeeper")

login_screen = ctk.CTkFrame(app, fg_color="transparent")
dashboard_screen = ctk.CTkFrame(app, fg_color="transparent")

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
    search_term = steam_search_entry.get()
    if not search_term:
        print("Please type a new game to search!")
        return
    
    try:
        url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US"
        response = requests.get(url)
        data = response.json()

        if data.get('items'):
            top_game = data['items'][0].get('name', 'Unknown')
            
            title_entry.delete(0, ctk.END)
            title_entry.insert(0, top_game)
            
            platform_entry.delete(0, ctk.END)
            platform_entry.insert(0, "PC (Steam)")
            
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

status_entry = ctk.CTkEntry(sidebar, placeholder_text="Status", width=200)
status_entry.pack(pady=10)

def save_button_clicked():
    title = title_entry.get()
    platform = platform_entry.get()
    status = status_entry.get()
    
    if title and platform and status:
        try:
            database.add_game(title, platform, status)
            print(f"Success! Saved {title}.")
            
            title_entry.delete(0, ctk.END)
            platform_entry.delete(0, ctk.END)
            status_entry.delete(0, ctk.END)
            
            load_games()
        except Exception as e:
            print(f"DATABASE ERROR: {e}") # This will reveal why it's failing!
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

game_list_frame = ctk.CTkScrollableFrame(main_area, fg_color="transparent")
game_list_frame.pack(fill="both", expand=True)

def mark_as_done(game_id):
    database.delete_game(game_id)
    load_games()

def load_games():
    for widget in game_list_frame.winfo_children():
        widget.destroy()

    games = database.get_all_games()

    for game in games:
        game_id = game[0]
        game_text = f"{game[1]} | {game[2]} | [{game[3]}]"

        row_frame = ctk.CTkFrame(game_list_frame)
        row_frame.pack(fill="x", pady=5)

        label = ctk.CTkLabel(row_frame, text=game_text, font=("Arial", 16))
        label.pack(side="left", padx=20, pady=10)

        done_button = ctk.CTkButton(row_frame, text="Finish", width=80, fg_color="#C62828", hover_color="#B71C1C", command=lambda id=game_id: mark_as_done(id))
        done_button.pack(side="right", padx=20)

# START APP

login_screen.pack(fill="both", expand=True)

if __name__ == "__main__":
    app.mainloop()
