import json
import tkinter as tk
from tkinter import messagebox, ttk
from client_api import add_user

CONFIG_FILE = "config.json"

def save_config():
    username = entry_username.get().strip()
    user_id = entry_user_id.get().strip()
    email = entry_email.get().strip()

    if not username or not user_id or not email:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        user_id = int(user_id)  # Validate user_id as an integer
    except ValueError:
        messagebox.showerror("Error", "User ID must be a number!")
        return

    data = {"user_id": user_id, "notification_email": email}

    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", "Configuration saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {e}")

# Create GUI window
root = tk.Tk()
root.title("User Configuration")
root.geometry("400x350")
root.configure(bg="#2C2F33")  # Dark background
root.resizable(False, False)

# Frame for inputs
frame = tk.Frame(root, bg="#2C2F33")
frame.pack(expand=True, fill="both")

# Title Label
label_title = tk.Label(frame, text="User Configuration", font=("Arial", 14, "bold"), fg="white", bg="#2C2F33")
label_title.pack(pady=10)

# Username
tk.Label(frame, text="Username:", font=("Arial", 11), fg="white", bg="#2C2F33").pack(anchor="w", padx=30)
entry_username = ttk.Entry(frame, width=40, font=("Arial", 10))
entry_username.pack(pady=5, padx=30)

# User ID
tk.Label(frame, text="User ID:", font=("Arial", 11), fg="white", bg="#2C2F33").pack(anchor="w", padx=30)
entry_user_id = ttk.Entry(frame, width=40, font=("Arial", 10))
entry_user_id.pack(pady=5, padx=30)

# Notification Email
tk.Label(frame, text="Notification Email:", font=("Arial", 11), fg="white", bg="#2C2F33").pack(anchor="w", padx=30)
entry_email = ttk.Entry(frame, width=40, font=("Arial", 10))
entry_email.pack(pady=5, padx=30)

# Buttons
btn_frame = tk.Frame(frame, bg="#2C2F33")
btn_frame.pack(pady=15)

btn_save = ttk.Button(btn_frame, text="Save & Add User", command=save_config)
btn_save.pack(side="left", padx=10)

btn_quit = ttk.Button(btn_frame, text="Quit", command=root.quit)
btn_quit.pack(side="left", padx=10)

root.mainloop()

