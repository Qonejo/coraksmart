from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from whitenoise import WhiteNoise
from datetime import datetime
import urllib.parse
import os
import json
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
 

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
app.secret_key = os.urandom(24)

# --- CONFIGURACIÓN SIMPLIFICADA DE WHITENOISE ---
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/", max_age=31536000)
print("WhiteNoise configurado.")

UPLOAD_FOLDER = 'static'

# --- CONFIGURACIÓN DE ARCHIVOS ---
ADMIN_PASSWORD = "[REDACTED:password]"
PEDIDOS_FILE = "pedidos.json"
PRODUCTOS_FILE = "productos.json"
USUARIOS_FILE = "usuarios.json"

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
CONFIG = {
    "horarios_atencion": "Lunes a Viernes: 9:00 AM - 6:00 PM",
    "whatsapp_principal": "5215513361764",
    "whatsapp_secundario": ""
}

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_productos():
    try:
        with open(PRODUCTOS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}
def guardar_productos(productos):
    with open(PRODUCTOS_FILE, 'w', encoding='utf-8') as f: json.dump(productos, f, indent=4)
def cargar_pedidos():
    try:
        with open(PEDIDOS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return []
def guardar_pedidos(pedidos):
    with open(PEDIDOS_FILE, 'w', encoding='utf-8') as f: json.dump(pedidos, f, indent=4)
def cargar_usuarios():
    try:
        with open(USUARIOS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}
def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f: json.dump(usuarios, f, indent=4)

# --- SISTEMA DE AURA Y GENERADOR DE IDS ---
AURA_LEVELS = [
    {"level": 0, "points_needed": -float('inf'), "flame_color": "black",  "prize": "Sin Rango"},
    {"level": 1, "points_needed": 0,         "flame_color": "white",  "prize": "Gomita + Pelón"},
    {"level": 2, "points_needed": 8000,      "flame_color": "blue",   "prize": "Cupón 10%"},
    {"level": 3, "points_needed": 20000,     "flame_color": "green",  "prize": "Producto Sorpresa"},
    {"level": 4, "points_needed": 50000,     "flame_color": "yellow", "prize": "Cupón 15%"},
    {"level": 5, "points_needed": 100000,    "flame_color": "orange", "prize": "1 : : + Salvia"},
    {"level": 6, "points_needed": 250000,    "flame_color": "red",    "prize": "Cupón del 20%"},
    {"level": 7, "points_needed": 500000,    "flame_color": "purple", "prize": "Regalo Misterioso"}
]

def get_user_aura_info(user_emoji):
    usuarios = cargar_usuarios()
    user_data = usuarios.get(user_emoji, {})
    points = user_data.get("aura_points", 0)
    current_level_info = AURA_LEVELS[0]
    for level_info in reversed(AURA_LEVELS):
        if points >= level_info["points_needed"]:
            current_level_info = level_info
            break
    return {"points": points, "level_info": current_level_info}

def get_aura_points_for_product(product_id, price):
    """Calcular puntos de aura basado en el producto y precio"""
    # Mapeo de productos a multiplicadores según la relación especificada
    aura_multipliers = {
        # vapes   1200$x3  = 3600 pts de aura
        "vapes": 3.0,
        # vapes   1000$x3.5= 3500 pts de aura  
        "vape_1000": 3.5,
        # gotero  500$x6   = 3000 pts de aura
        "gotero": 6.0,
        # caps    450$x5.5 = 2025 pts de aura
        "caps": 5.5,
        # olla4   400$x5   = 2000 pts de aura
        "olla4": 5.0,
        # olla3   350$x5   = 1750 pts de aura
        "olla3": 5.0,
        # oll2    280$x5   = 1400 pts de aura
        "oll2": 5.0,
        # ruffles 180$x6   = 1080 pts de aura
        "ruffles": 6.0,
        # brownie 150$x5.5 = 825 pts de aura
        "brownie": 5.5,
        # nerd ro 150$x5.5 = 825 pts de aura
        "nerd": 5.5,
        "nerdsrope": 5.5,
        # barrita 150$x5.5 = 825 pts de aura
        "barrita": 5.5,
        # salvia  130$x6   = 780  pts de aura
        "salvia": 6.0,
        # galleta 130 $x5  = 650 pts de aura
        "galleta": 5.0,
        # bombone 120$x5   = 600 pts de aura
        "bombon": 5.0,
        # nerdbit 120$x5   = 600 pts de aura
        "nerdbit": 5.0,
        # pelon   60$x4.5  = 270 pts de aura
        "pelon": 4.5,
        # gomitas 60$x4    = 240 pts de aura
        "gomitas": 4.0
    }
    
    # Buscar multiplicador por ID del producto
    multiplier = aura_multipliers.get(product_id.lower(), 3.0)  # Default 3.0
    
    # También buscar por palabras clave en el ID
    for keyword, mult in aura_multipliers.items():
        if keyword in product_id.lower():
            multiplier = mult
            break
    
    return int(price * multiplier)

def codificar_numero(numero):
    if not isinstance(numero, int) or numero < 0: return str(numero)
    letras = string.ascii_uppercase
    indice_letra = numero % 26
    letra_codificada = letras[indice_letra]
    numero_ciclo = numero // 26
    if numero_ciclo == 0: return letra_codificada
    else: return f"{letra_codificada}{numero_ciclo}"

def generar_id_pedido():
    now = datetime.now()
    parte_fecha = f"{codificar_numero(now.day - 1)}{codificar_numero(now.month - 1)}{now.strftime('%y')}"
    parte_hora = f"{codificar_numero(now.hour)}{codificar_numero(now.minute)}{codificar_numero(now.second)}"
    parte_pedido = codificar_numero(100 + len(cargar_pedidos()))
    sello_aleatorio = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{parte_fecha}-{parte_hora}-{parte_pedido}-{sello_aleatorio}"

# --- VISTAS PRINCIPALES ---
@app.route("/entrar")
def entrar():
    return render_template("bienvenida.html")

@app.route("/")
def index():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    
    productos_dict = cargar_productos()
    
    # --- LÓGICA DE ORDENAMIENTO SIMPLIFICADA ---
    # Creamos una lista de tuplas (id, datos) ordenada
    productos_ordenados = sorted(productos_dict.items(), key=lambda item: item[1].get('orden', 999))
    
    return render_template(
        "index.html",
        PRODUCTOS_ORDENADOS=productos_ordenados, # Enviamos la lista
        PRODUCTOS_DICT=productos_dict,       # Y el diccionario original
        aura_data=aura_data,
        AURA_LEVELS=AURA_LEVELS
    )

@app.route("/perfil")
def perfil_usuario():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    todos_los_pedidos = cargar_pedidos()
    pedidos_del_usuario = [p for p in todos_los_pedidos if p.get("user_emoji") == user_emoji]
    return render_template("perfil.html", user_emoji=user_emoji, pedidos=reversed(pedidos_del_usuario), PRODUCTOS=cargar_productos(), aura_data=aura_data, AURA_LEVELS=AURA_LEVELS)

@app.route("/admin")
def admin_view():
    if not session.get("logged_in"): return redirect(url_for("login"))
    pedidos = cargar_pedidos()
    productos_dict = cargar_productos()
    productos_ordenados_admin = sorted(productos_dict.items(), key=lambda item: item[1].get('orden', 999))
    pedidos_agrupados = {}
    for pedido in reversed(pedidos):
        emoji_key = pedido.get("user_emoji", "Pedidos Antiguos / Sin Usuario")
        if emoji_key not in pedidos_agrupados:
            pedidos_agrupados[emoji_key] = []
        pedidos_agrupados[emoji_key].append(pedido)
    return render_template("admin.html", PEDIDOS_AGRUPADOS=pedidos_agrupados, PRODUCTOS_ORDENADOS=productos_ordenados_admin, PRODUCTOS=productos_dict)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_view"))
        else:
            flash("Contraseña incorrecta.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("logged_in_user_emoji", None)
    return redirect(url_for("entrar"))

# --- PÁGINA DE NIVELES DE AURA ---
@app.route("/niveles")
def niveles_aura():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    return render_template("niveles.html", aura_data=aura_data, AURA_LEVELS=AURA_LEVELS)

# --- RUTAS DE CONFIGURACIÓN ADMIN ---
@app.route("/admin/configuracion", methods=["GET", "POST"])
def admin_configuracion():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    if request.method == "POST":
        # Actualizar configuración
        CONFIG["horarios_atencion"] = request.form.get("horarios_atencion", CONFIG["horarios_atencion"])
        CONFIG["whatsapp_principal"] = request.form.get("whatsapp_principal", CONFIG["whatsapp_principal"])
        CONFIG["whatsapp_secundario"] = request.form.get("whatsapp_secundario", CONFIG["whatsapp_secundario"])
        
        flash("Configuración actualizada con éxito.", "success")
        return redirect(url_for("admin_configuracion"))
    
    return render_template("admin_config.html", config=CONFIG)
