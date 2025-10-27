import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Configuración de acceso
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "WMS SIT"

def get_credentials():
    creds_dict = json.loads(st.secrets["google"]["credentials"])
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)

def get_sheet(nombre_hoja):
    creds = get_credentials()
    client = gspread.authorize(creds)
    hoja = client.open(SPREADSHEET_NAME).worksheet(nombre_hoja)
    data = hoja.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0])
