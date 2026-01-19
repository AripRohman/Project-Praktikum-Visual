# File untuk menyimpan paath dan setting aplikasi
import os
import sys

def get_app_directory():

    # Mendapatkan direktori aplikasi yang persistent
    # Saat .exe, akan menggunakan folder di c dan menambah puskesmas app
   
    if getattr(sys, 'frozen', False):
        app_dir = os.path.join(os.path.expanduser('~'), 'PuskesmasApp')
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    
    return app_dir

def get_resource_path(relative_path):

    # Mendapatkan path absolut untuk file resource
    # Berfungsi untuk development dan saat jadi .exe

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

APP_DIR = get_app_directory()
USERS_FILE = os.path.join(APP_DIR, "users.json")
SESSION_FILE = os.path.join(APP_DIR, "session.json")

STYLE_FILE = get_resource_path("Style.qss")
ICON_FILE = get_resource_path(os.path.join("gambar", "icon.png"))
LOGO_FILE = get_resource_path(os.path.join("gambar", "logo.ico"))
MENU_FILE = get_resource_path(os.path.join("gambar", "image.png"))

API_URL = "https://wowbubqrivodbzyyywff.supabase.co/rest/v1/Pasien"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSI" \
          "sInJlZiI6Indvd2J1YnFyaXZvZGJ6eXl5d2ZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY0" \
          "OTk0NTEsImV4cCI6MjA4MjA3NTQ1MX0.8TGPWWnzu5KIVJzJEZjOLZM6UAI5YHap4qTjN1VjFD8"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

print(f"Data aplikasi disimpan di: {APP_DIR}")
print(f"Style QSS: {STYLE_FILE}")
print("ICON PATH:", ICON_FILE)
print("EXISTS:", os.path.exists(ICON_FILE))
print("ICON PATH:", MENU_FILE)