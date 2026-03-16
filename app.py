import customtkinter as ctk

#Set the overall theme and color of the app

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

#Create the main window

app = ctk.CTk()
app.geometry ("500x350")
app.title("Backlog Gatekeeper")

#Welcome Label

welcome_label = ctk.CTkLabel(app, text="Welcome to the Backlog Gatekeeper!", font=("Arial", 20, "bold"))
welcome_label.pack(pady=40)

#Dummy button 

add_button = ctk.CTkButton(app, text="Add New Game")
add_button.pack(pady=10)

#Run

if __name__ == "__main__":
    app.mainloop()