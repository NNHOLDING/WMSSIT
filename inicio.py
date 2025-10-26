import tkinter as tk
from tkinter import ttk, messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "TuNombreDeHoja"
SHEET_NAME = "Usuarios"

# Función para conectar con Google Sheets
def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

# Función de autenticación
def authenticate():
    progress.start()
    try:
        sheet = get_sheet()
        users = sheet.get_all_records()
        usuario_ingresado = entry_user.get().strip()
        contraseña_ingresada = entry_pass.get().strip()

        for user in users:
            if user["Usuario"] == usuario_ingresado and user["Contraseña"] == contraseña_ingresada:
                rol = user.get("Rol", "Sin rol")
                messagebox.showinfo("Acceso concedido", f"Bienvenido {usuario_ingresado}\nRol: {rol}")
                return
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar: {e}")
    finally:
        progress.stop()

# Interfaz gráfica
root = tk.Tk()
root.title("WMS - Inicio de sesión")
root.geometry("350x300")
root.configure(bg="#f0f4ff")

tk.Label(root, text="Inicio de sesión", font=("Helvetica", 16, "bold"), bg="#f0f4ff").pack(pady=10)

tk.Label(root, text="Usuario", bg="#f0f4ff").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Contraseña", bg="#f0f4ff").pack()
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

show_var = tk.BooleanVar()
tk.Checkbutton(root, text="Mostrar contraseña", variable=show_var,
               command=lambda: entry_pass.config(show="" if show_var.get() else "*"),
               bg="#f0f4ff").pack()

tk.Button(root, text="Iniciar sesión", bg="#add8e6", command=authenticate).pack(pady=10)

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(fill="x", padx=20)

root.mainloop()