import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔐 Configuración de acceso a Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
SPREADSHEET_NAME = "WMS SIT"
SHEET_LPN = "LPNs Generados"

# 📄 Obtener hoja específica de LPNs
def get_lpn_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_LPN)
    return sheet

# 🔢 Obtener último consecutivo por tipo
def get_last_lpn(sheet, tipo):
    data = sheet.col_values(1)[1:]  # Ignorar encabezado
    prefix = "IB" if tipo == "Etiquetas IB" else "OB"
    data = [d for d in data if d.startswith(prefix)]
    if not data:
        return 0
    last = data[-1]
    return int(last[-6:])  # Extraer últimos 6 dígitos

# 🧾 Generar nuevos LPNs
def generate_lpns(cantidad, usuario, bodega, tipo):
    sheet = get_lpn_sheet()
    last = get_last_lpn(sheet, tipo)
    nuevos = []
    for i in range(1, cantidad + 1):
        consecutivo = str(last + i).zfill(6)
        prefix = "IB" if tipo == "Etiquetas IB" else "OB"
        lpn = f"{prefix}{bodega}506{consecutivo}"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevos.append([lpn, fecha, usuario, "Disponible", bodega])
    sheet.append_rows(nuevos)
    return nuevos

# 📊 Obtener cualquier hoja como DataFrame
def get_sheet(nombre_hoja):
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    hoja = client.open(SPREADSHEET_NAME).worksheet(nombre_hoja)
    data = hoja.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0])
