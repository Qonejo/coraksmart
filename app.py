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
# Cambiar contraseña del admin
ADMIN_PASSWORD = "coraker12"
ADMIN_PASSWORD = "[REDACTED:password]"
PEDIDOS_FILE = "pedidos.json"
PRODUCTOS_FILE = "productos.json"
USUARIOS_FILE = "usuarios.json"

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
CONFIG_FILE = "config.json"

def cargar_configuracion():
    """Cargar configuración desde archivo o usar valores por defecto"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "horarios_atencion": "Lunes a Viernes: 9:00 AM - 6:00 PM",
            "whatsapp_principal": "5215513361764", 
            "whatsapp_secundario": "5215625877420",
            "whatsapp_1": "5215513361764",
            "whatsapp_2": "5215625877420",
            "whatsapp_3": "",
            "whatsapp_1_nombre": "Corak",
            "whatsapp_2_nombre": "Rubadub",
            "whatsapp_3_nombre": "Terciario"
        }

def guardar_configuracion(config):
    """Guardar configuración en archivo"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Cargar configuración al iniciar
CONFIG = cargar_configuracion()

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_productos():
    try:
        with open(PRODUCTOS_FILE, 'r', encoding='utf-8') as f: 
            productos = json.load(f)
            # Asegurar que todos los productos tengan whatsapp_asignado
            for product_id, product_data in productos.items():
                if 'whatsapp_asignado' not in product_data:
                    product_data['whatsapp_asignado'] = '1'
            return productos
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
AURA_LEVELS_FILE = "aura_levels.json"

def cargar_aura_levels():
    """Cargar niveles de aura desde archivo o usar valores por defecto"""
    try:
        with open(AURA_LEVELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [
            {"level": 0, "points_needed": -float('inf'), "flame_color": "black",  "name": "Bandido", "prize": "No hay recompensas en este nivel", "character_size": 96},
            {"level": 1, "points_needed": 9000,         "flame_color": "white",  "name": "Vampiro ojón", "prize": "1 Gomita gratis", "character_size": 96},
            {"level": 2, "points_needed": 16000,      "flame_color": "blue",   "name": "Avispa mutante", "prize": "5% descuento en tu próxima compra", "character_size": 96},
            {"level": 3, "points_needed": 21000,      "flame_color": "green",  "name": "Lombriz mounstro", "prize": "Salvia + 1", "character_size": 96},
            {"level": 4, "points_needed": 30000,     "flame_color": "yellow", "name": "Perrodragón", "prize": "10% descuento en tu próxima compra", "character_size": 96},
            {"level": 5, "points_needed": 39000,     "flame_color": "orange", "name": "Brujo runero", "prize": "1 Olla", "character_size": 96},
            {"level": 6, "points_needed": 52000,     "flame_color": "red",    "name": "Obelisco runa", "prize": "15% descuento en tu próxima compra", "character_size": 96},
            {"level": 7, "points_needed": 66000,     "flame_color": "purple", "name": "Entidad", "prize": "1 Brownie + 1 Gomita + Media olla + 5% descuento en tu próxima compra", "character_size": 96}
        ]

def guardar_aura_levels(levels):
    """Guardar niveles de aura en archivo"""
    # Convertir -inf a string para JSON
    levels_for_json = []
    for level in levels:
        level_copy = level.copy()
        if level_copy["points_needed"] == -float('inf'):
            level_copy["points_needed"] = "negative_infinity"
        levels_for_json.append(level_copy)
    
    with open(AURA_LEVELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(levels_for_json, f, indent=4, ensure_ascii=False)

def procesar_aura_levels_loaded(levels):
    """Procesar niveles cargados para convertir string infinity a float"""
    for level in levels:
        if level["points_needed"] == "negative_infinity":
            level["points_needed"] = -float('inf')
    return levels

# Cargar niveles de aura al iniciar
AURA_LEVELS = procesar_aura_levels_loaded(cargar_aura_levels())

def get_user_aura_info(user_emoji):
    usuarios = cargar_usuarios()
    user_data = usuarios.get(user_emoji, {})
    points = user_data.get("aura_points", 0)
    current_level_info = AURA_LEVELS[0]
    for level_info in reversed(AURA_LEVELS):
        if points >= level_info["points_needed"]:
            current_level_info = level_info
            break
    
    # Determinar el personaje correcto basado en nivel y progreso
    character_gif = get_character_gif(points, current_level_info)
    current_level_info["character_gif"] = character_gif
    
    # Determinar información de la barra de progreso
    progress_bar_info = get_progress_bar_info(points, current_level_info, user_emoji)
    
    # Verificar recompensas pendientes
    pending_rewards = check_pending_rewards(user_emoji)
    
    return {
        "points": points, 
        "level_info": current_level_info,
        "progress_bar": progress_bar_info,
        "pending_rewards": pending_rewards
    }

def get_character_gif(points, level_info):
    """Determinar qué archivo GIF del personaje mostrar basado en puntos y nivel"""
    level = level_info["level"]
    
    # Nivel 0 (sin experiencia)
    if points == 0:
        return "f0.gif"
    
    # Nivel 1 - con sub-niveles basados en progreso
    if level == 1:
        # Buscar el siguiente nivel para calcular progreso
        next_level_points = None
        for next_level in AURA_LEVELS:
            if next_level["level"] == 2:
                next_level_points = next_level["points_needed"]
                break
        
        if next_level_points:
            progress = points / next_level_points
            if progress < 1/3:
                return "f1a.gif"
            elif progress < 2/3:
                return "f1b.gif"
            else:
                return "f1c.gif"
        else:
            return "f1a.gif"
    
    # Niveles 2-7
    elif 2 <= level <= 7:
        return f"f{level}.gif"
    
    # Por defecto
    return "f0.gif"

def get_progress_bar_info(points, current_level_info, user_emoji):
    """Determinar información de la barra de progreso visual"""
    level = current_level_info["level"]
    
    # Si está en el nivel máximo
    if level >= 7:
        return {
            "bar_type": "barcom.gif",
            "exp_orbs": 0,
            "completed": True
        }
    
    # Buscar el siguiente nivel
    next_level_info = None
    for level_info in AURA_LEVELS:
        if level_info["level"] == level + 1:
            next_level_info = level_info
            break
    
    if not next_level_info:
        return {
            "bar_type": "barcom.gif",
            "exp_orbs": 0,
            "completed": True
        }
    
    # Calcular puntos necesarios para el siguiente nivel
    points_needed_for_next = next_level_info["points_needed"]
    points_in_current_level = points - current_level_info["points_needed"]
    points_needed_in_level = points_needed_for_next - current_level_info["points_needed"]
    
    # Validar que no tengamos valores inválidos
    if points_needed_in_level <= 0 or points_in_current_level < 0:
        return {
            "bar_type": "barva.png",
            "exp_orbs": 0,
            "completed": False
        }
    
    # Si no tiene puntos en el nivel actual
    if points_in_current_level <= 0:
        return {
            "bar_type": "barva.png",
            "exp_orbs": 0,
            "completed": False
        }
    
    # Si ya completó el nivel actual
    if points >= points_needed_for_next:
        # Verificar si ya reclamó la recompensa de este nivel
        usuarios = cargar_usuarios()
        user_data = usuarios.get(user_emoji, {})
        claimed_levels = user_data.get("claimed_levels", [])
        next_level = next_level_info["level"]
        
        return {
            "bar_type": "barcom.gif",
            "exp_orbs": 0,
            "completed": True,
            "level_up": next_level not in claimed_levels,  # Solo mostrar si no ha reclamado
            "reward": next_level_info["prize"],
            "next_level": next_level,
            "points_in_level": points_in_current_level,
            "points_needed_for_next": points_needed_for_next
        }
    
    # Determinar cuántas orbes de experiencia mostrar
    # Cada orbe exp.png representa una porción relativa de los puntos del nivel
    # Calculamos el valor de cada orbe basado en los puntos totales del nivel
    
    # Para nivel 1: 7000 puntos / 10 = 700 puntos por orbe
    # Para nivel 2: 2030 puntos / 10 = 203 puntos por orbe (pero mínimo 240)
    max_orbs = 8  # Máximo 8 orbes por barra para que no se desborde visualmente
    
    # Protección adicional contra división por cero y valores inválidos
    if points_needed_in_level <= 0 or max_orbs <= 0:
        orb_value = 240
    else:
        orb_value = max(240, points_needed_in_level / max_orbs)
        # Protección contra valores infinitos o muy grandes
        if not isinstance(orb_value, (int, float)) or orb_value == float('inf') or orb_value > 10000000:
            orb_value = 240
    
    # Protección contra NaN e infinitos
    if (orb_value <= 0 or points_in_current_level < 0 or 
        orb_value == float('inf') or points_in_current_level == float('inf')):
        exp_orbs = 0
    else:
        try:
            division_result = points_in_current_level / orb_value
            # Protección adicional contra infinitos en el resultado
            if division_result == float('inf') or division_result != division_result:  # NaN check
                exp_orbs = 0
            else:
                exp_orbs = min(max_orbs, int(division_result))
        except (ValueError, ZeroDivisionError, OverflowError):
            exp_orbs = 0
    
    # Determinar tipo de barra
    if points_in_current_level >= 240:
        bar_type = "barinic.png"
    else:
        bar_type = "barva.png"
    
    # Calcular porcentaje de progreso con protección contra división por cero
    if points_needed_in_level <= 0:
        progress_percent = 0
    else:
        try:
            progress_percent = int((points_in_current_level / points_needed_in_level) * 100)
        except (ValueError, ZeroDivisionError):
            progress_percent = 0
    
    return {
        "bar_type": bar_type,
        "exp_orbs": exp_orbs,
        "completed": False,
        "progress_percent": progress_percent,
        "points_in_level": points_in_current_level,
        "points_needed_for_next": points_needed_for_next,
        "orb_value": int(orb_value) if isinstance(orb_value, (int, float)) and orb_value != float('inf') and orb_value < 10000000 else 240
    }

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

def generar_codigo_recompensa():
    """Generar código alfanumérico de 6 dígitos para reclamar recompensas"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def check_pending_rewards(user_emoji):
    """Verificar si el usuario tiene recompensas pendientes por reclamar"""
    usuarios = cargar_usuarios()
    user_data = usuarios.get(user_emoji, {})
    current_points = user_data.get("aura_points", 0)
    claimed_levels = user_data.get("claimed_levels", [])
    
    # Determinar nivel actual
    current_level = 0
    for level_info in reversed(AURA_LEVELS):
        if current_points >= level_info["points_needed"]:
            current_level = level_info["level"]
            break
    
    # Verificar si hay niveles completados sin reclamar
    pending_rewards = []
    for level in range(1, current_level + 1):
        if level not in claimed_levels:
            level_info = next((l for l in AURA_LEVELS if l["level"] == level), None)
            if level_info:
                pending_rewards.append(level_info)
    
    return pending_rewards

def procesar_compra_interna(carrito, productos, user_emoji):
    """Procesa internamente una compra y devuelve total, detalle y puntos de aura"""
    total = 0
    detalle_completo = {}
    aura_total = 0
    
    for cart_id, cant in carrito.items():
        parts = cart_id.split('-', 1)
        base_id = parts[0]
        variation_id = parts[1] if len(parts) > 1 else None
        prod_data = productos.get(base_id if variation_id else cart_id)
        
        if not prod_data:
            continue
            
        precio_item = 0
        
        if "bundle_items" in prod_data:
            precio_item = prod_data.get("bundle_precio", 0)
        elif variation_id and "variaciones" in prod_data:
            variation_data = prod_data["variaciones"].get(variation_id)
            if variation_data:
                precio_item = variation_data.get("precio", 0)
        elif "precio" in prod_data:
            precio_item = prod_data.get("precio", 0)
        
        subtotal = precio_item * cant
        total += subtotal
        
        # Calcular puntos de aura
        puntos_por_item = get_aura_points_for_product(base_id, precio_item)
        aura_total += puntos_por_item * cant
        
        # Guardar detalle completo
        detalle_completo[cart_id] = {
            "nombre": prod_data.get("nombre", "Producto"),
            "precio": precio_item,
            "cantidad": cant,
            "subtotal": subtotal
        }
    
    return total, detalle_completo, aura_total

def crear_mensaje_pedido(pedido, detalle_completo):
    """Crea el mensaje de WhatsApp para el pedido"""
    delivery_info = pedido.get("delivery_info", {})
    
    mensaje_partes = [
        f"¡Que onda! 🛒",
        f"*Pedido #{pedido['id']}*",
        ""
    ]
    
    # Lista de productos
    for cart_id, info in detalle_completo.items():
        mensaje_partes.append(f"• {info['cantidad']}x {info['nombre']}")
    
    mensaje_partes.append("")
    mensaje_partes.append(f"*Total: ${pedido['total']:.2f}*")
    mensaje_partes.append("")
    
    # Información de entrega
    mensaje_partes.append(f"📅 *Horario:* {delivery_info.get('day', 'No especificado')} a las {delivery_info.get('time', 'No especificado')}")
    
    # Zona/ubicación
    if delivery_info.get('station'):
        mensaje_partes.append(f"📍 *Zona:* {delivery_info.get('station', 'No especificado')}")
    
    if delivery_info.get('instructions'):
        mensaje_partes.append(f"📝 *Notas:* {delivery_info['instructions']}")
    
    if delivery_info.get('phone'):
        mensaje_partes.append(f"📱 *Teléfono:* {delivery_info['phone']}")
    
    return "\n".join(mensaje_partes)

def determinar_whatsapp_destino(carrito, productos):
    """Determinar qué WhatsApp debe recibir el pedido basándose en los productos"""
    whatsapp_counts = {"1": 0, "2": 0, "3": 0}
    
    for product_cart_id, cantidad in carrito.items():
        # Separar product_id de variation_id si existe
        if '-' in product_cart_id:
            product_id = product_cart_id.split('-')[0]
        else:
            product_id = product_cart_id
        
        if product_id in productos:
            whatsapp_asignado = productos[product_id].get('whatsapp_asignado', '1')
            whatsapp_counts[whatsapp_asignado] += cantidad
    
    # Retornar el WhatsApp con más productos
    max_whatsapp = max(whatsapp_counts, key=whatsapp_counts.get)
    
    # Mapear a los números de WhatsApp configurados
    whatsapp_map = {
        "1": CONFIG.get('whatsapp_1', CONFIG.get('whatsapp_principal', '')),
        "2": CONFIG.get('whatsapp_2', CONFIG.get('whatsapp_secundario', '')),
        "3": CONFIG.get('whatsapp_3', '')
    }
    
    whatsapp_numero = whatsapp_map.get(max_whatsapp, CONFIG.get('whatsapp_principal', ''))
    
    # Si no hay número configurado, usar el principal
    if not whatsapp_numero:
        whatsapp_numero = CONFIG.get('whatsapp_principal', '')
    
    return whatsapp_numero, max_whatsapp

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
        PRODUCTOS=productos_dict,       # Y el diccionario original (nombre correcto)
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

# --- HELPER PARA HISTORIAL COMBINADO ---
def parse_pedido_timestamp(ts_str):
    """Intenta parsear los diferentes formatos de timestamp usados en la aplicación."""
    # Formato 1: "30 de July, 2025 a las 19:19"
    # Formato 2: "2025-07-30 19:30:00"
    if " a las " in ts_str:
        try:
            # Normalizar el string
            ts_str_normalized = ts_str.replace(' a las ', ' ').replace(' de ', ' ')
            # Mapear meses en español si es necesario
            month_map = {
                'enero': 'January', 'febrero': 'February', 'marzo': 'March', 'abril': 'April',
                'mayo': 'May', 'junio': 'June', 'julio': 'July', 'agosto': 'August',
                'septiembre': 'September', 'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
            }
            for es, en in month_map.items():
                ts_str_normalized = ts_str_normalized.lower().replace(es, en)

            # Asumimos que el mes está en inglés y capitalizado
            return datetime.strptime(ts_str_normalized, '%d %B, %Y %H:%M')
        except (ValueError, TypeError):
            pass # Falla y prueba el siguiente formato

    # Formato 2 y fallback
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        # Si todo falla, devolver una fecha por defecto para evitar crashes
        return datetime.fromtimestamp(0)


def get_combined_history():
    """Crea una lista unificada y cronológica de pedidos y recompensas pendientes."""
    pedidos = cargar_pedidos()
    usuarios = cargar_usuarios()
    productos = cargar_productos()
    aura_levels = AURA_LEVELS

    combined_history = []

    # 1. Procesar Pedidos
    for pedido in pedidos:
        timestamp_str = pedido.get("timestamp")
        if not timestamp_str or not isinstance(timestamp_str, str):
            continue

        timestamp_dt = parse_pedido_timestamp(timestamp_str)

        # Crear resumen del detalle
        detalle_summary_parts = []
        if isinstance(pedido.get('detalle'), dict):
            for prod_id, cantidad in pedido['detalle'].items():
                base_id = prod_id.split('-')[0]
                prod_info = productos.get(base_id, {})
                nombre = prod_info.get('nombre', prod_id)
                detalle_summary_parts.append(f"{cantidad}x {nombre}")
        detalle_summary = ", ".join(detalle_summary_parts)

        combined_history.append({
            'type': 'pedido',
            'id': pedido.get('id'),
            'user_emoji': pedido.get('user_emoji', '👤'),
            'timestamp_str': timestamp_str,
            'timestamp_dt': timestamp_dt,
            'details': detalle_summary or "Detalle no disponible",
            'total': pedido.get('total', 0),
            'status': pedido.get('completado', False),
            'data': pedido
        })

    # 2. Procesar Recompensas Pendientes
    for user_emoji, user_data in usuarios.items():
        if "reward_codes" in user_data:
            for level_str, reward_info in user_data["reward_codes"].items():
                if not reward_info.get("claimed", False):
                    level = int(level_str)
                    level_info = next((l for l in aura_levels if l["level"] == level), None)
                    if not level_info: continue

                    timestamp_str = reward_info.get("generated_at")
                    if not timestamp_str or not isinstance(timestamp_str, str): continue

                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        continue

                    combined_history.append({
                        'type': 'recompensa',
                        'id': f"{user_emoji}-{level}",
                        'user_emoji': user_emoji,
                        'timestamp_str': timestamp_str,
                        'timestamp_dt': timestamp_dt,
                        'details': f"Nivel {level}: {level_info['prize']}",
                        'total': 0,
                        'status': False,
                        'data': {
                            'level': level,
                            'user_emoji': user_emoji,
                            'prize': level_info['prize'],
                            'code': reward_info.get('code', 'N/A')
                        }
                    })

    # 3. Ordenar la lista combinada
    combined_history.sort(key=lambda x: x['timestamp_dt'], reverse=True)

    return combined_history


@app.route("/admin")
def admin_view():
    if not session.get("logged_in"): return redirect(url_for("login"))

    # Usar la nueva función para obtener el historial combinado
    historial_combinado = get_combined_history()

    # Cargar datos adicionales que la plantilla pueda necesitar
    productos_dict = cargar_productos()
    productos_ordenados_admin = sorted(productos_dict.items(), key=lambda item: item[1].get('orden', 999))

    return render_template("admin.html",
                           historial=historial_combinado,
                           PRODUCTOS_ORDENADOS=productos_ordenados_admin,
                           PRODUCTOS=productos_dict,
                           config=CONFIG)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Usar la nueva contraseña
        if request.form.get("password") == "coraker12":
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

# --- API PARA EMOJIS ---
def cargar_emoji_list():
    """Cargar lista de emojis desde archivo, o usar lista por defecto"""
    try:
        with open('emoji_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('available_emojis', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return ["😀", "🚀", "🌟", "🍕", "🤖", "👻", "👽", "👾", "🦊", "🧙", "🌮", "💎", "🌙", "🔮", "🧬", "🌵", "🎉", "🔥", "💯", "👑", "💡", "🎮", "🛰️", "🛸", "🗿", "🌴", "🧪", "✨", "🔑", "🗺️", "🐙", "🦋", "🐲", "🍩", "⚡", "🎯", "⚓", "🌈", "🌌", "🌠", "🎱", "🎰", "🕹️", "🏆", "💊", "🎁", "💌", "📈", "😎", "😂", "🤣", "😍", "🥰", "😘", "😋", "😜", "🤩", "🥳", "😇", "🤠", "🤡", "🥸", "🤓", "😈", "👹", "👺", "💀", "👽", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "🦄", "🐵", "🐶", "🐺", "🐱", "🦁", "🐯", "🦒", "🦓", "🐴", "🦏", "🐘", "🐭", "🐹", "🐰", "🐻", "🐼", "🐨", "🐷", "🐸", "🦆", "🐧", "🦅", "🦉", "🐍", "🐢", "🦎", "🐙", "🦑", "🦐", "🦀", "🐡", "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧", "🐪", "🐫", "🦙", "🦘", "🦥", "🦨", "🦔", "🐁", "🐀", "🦇", "🕷️", "🦟", "🦗", "🐛", "🦋", "🐌", "🐚", "🪱", "🪲", "🪳", "🪰", "🌸", "🌺", "🌻", "🌹", "🌷", "💐", "🌾", "🌿", "🍀", "🌱", "🌳", "🌲", "🌴", "🌵", "🌾", "☘️", "🍃", "🍂", "🍁", "🍄", "🌰", "🎄", "💮", "🏔️", "⛰️", "🌋", "🏞️", "🏜️", "🏖️", "🏝️", "🌅", "🌄", "🌠", "🌌", "🌉", "🌁"]

def guardar_emoji_list(emoji_list):
    """Guardar lista de emojis en archivo"""
    config = {"available_emojis": emoji_list}
    with open('emoji_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Inicializar lista de emojis
EMOJI_LIST = cargar_emoji_list()

@app.route("/api/get-emojis")
def get_emojis():
    usuarios = cargar_usuarios()
    response = jsonify({ "all_emojis": EMOJI_LIST, "occupied_emojis": list(usuarios.keys()) })
    response.headers['Cache-Control'] = 'max-age=60'  # Cache por 1 minuto
    return response

@app.route("/api/emoji-access", methods=["POST"])
def emoji_access():
    data = request.get_json()
    emoji = data.get("emoji")
    password = data.get("password")
    if not emoji or not password or emoji not in EMOJI_LIST:
        return jsonify({"success": False, "message": "Datos inválidos."})
    usuarios = cargar_usuarios()
    if emoji in usuarios:
        if check_password_hash(usuarios[emoji]["password_hash"], password):
            session["logged_in_user_emoji"] = emoji
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Contraseña incorrecta."})
    else:
        if len(usuarios) >= 50:
            return jsonify({"success": False, "message": "Todas las vacantes están ocupadas."})
        usuarios[emoji] = {"password_hash": generate_password_hash(password), "aura_points": 0}
        guardar_usuarios(usuarios)
        session["logged_in_user_emoji"] = emoji
        return jsonify({"success": True, "message": "¡Avatar registrado con éxito!"})

# --- PÁGINA DE NIVELES DE AURA ---
@app.route("/niveles")
def niveles_aura():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    return render_template("niveles.html", aura_data=aura_data, AURA_LEVELS=AURA_LEVELS)

# --- PÁGINA DE CHECKOUT ---
@app.route("/checkout")
def checkout():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    
    carrito = session.get('carrito', {})
    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for("index"))
    
    productos = cargar_productos()
    carrito_items = []
    item_total = {}
    total = 0
    
    for item_id, cantidad in carrito.items():
        if '-' in item_id:
            product_id, variation_id = item_id.split('-', 1)
            product = productos.get(product_id, {})
            if 'variaciones' in product and variation_id in product['variaciones']:
                precio = product['variaciones'][variation_id]['precio']
        else:
            product = productos.get(item_id, {})
            if 'bundle_precio' in product:
                precio = product['bundle_precio']
            else:
                precio = product.get('precio', 0)
        
        subtotal = precio * cantidad
        item_total[item_id] = subtotal
        total += subtotal
        carrito_items.append((item_id, cantidad))
    
    return render_template("checkout.html", 
                         carrito_items=carrito_items, 
                         item_total=item_total,
                         total=total,
                         productos=productos,
                         config=CONFIG)

# --- PROCESAR PEDIDO ---
@app.route("/procesar_pedido", methods=["POST"])
def procesar_pedido():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    
    user_emoji = session["logged_in_user_emoji"]
    carrito = session.get('carrito', {})
    
    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for("index"))
    
    # Obtener datos del formulario
    delivery_day = request.form.get('delivery_day')
    delivery_time = request.form.get('delivery_time')
    delivery_station = request.form.get('delivery_station')
    special_instructions = request.form.get('special_instructions', '')
    phone_number = request.form.get('phone_number', '')
    
    # Validar campos requeridos
    if not all([delivery_day, delivery_time, delivery_station]):
        flash("Por favor completa todos los campos requeridos.", "error")
        return redirect(url_for("checkout"))
    
    # Procesar pedido (usar la función existente pero con datos adicionales)
    productos = cargar_productos()
    total, detalle_completo, aura_total = procesar_compra_interna(carrito, productos, user_emoji)
    
    # Crear pedido con información adicional
    pedido = {
        "id": generar_id_pedido(),
        "user_emoji": user_emoji,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detalle": carrito.copy(),
        "detalle_completo": detalle_completo,
        "total": total,
        "aura_ganada": aura_total,
        "delivery_info": {
            "day": delivery_day,
            "time": delivery_time,
            "station": delivery_station,
            "instructions": special_instructions,
            "phone": phone_number
        },
        "completado": False
    }
    
    # Guardar pedido
    todos_los_pedidos = cargar_pedidos()
    todos_los_pedidos.append(pedido)
    guardar_pedidos(todos_los_pedidos)
    
    # NO otorgar puntos de aura aquí - se otorgarán cuando el admin complete el pedido
    # Guardar información de aura potencial en el pedido para referencia
    pedido["aura_potencial"] = aura_total
    
    # Limpiar carrito
    session['carrito'] = {}
    
    # Determinar WhatsApp destino basándose en productos
    whatsapp_numero, whatsapp_id = determinar_whatsapp_destino(carrito, productos)
    
    # Crear mensaje de WhatsApp
    mensaje_whatsapp = crear_mensaje_pedido(pedido, detalle_completo)
    whatsapp_link = f"https://wa.me/{whatsapp_numero}?text={urllib.parse.quote(mensaje_whatsapp)}"
    
    # Guardar información del WhatsApp usado en el pedido
    pedido["whatsapp_usado"] = {
        "numero": whatsapp_numero,
        "id": whatsapp_id,
        "nombre": CONFIG.get(f'whatsapp_{whatsapp_id}_nombre', 'Principal')
    }
    
    flash(f"¡Pedido realizado con éxito! Podrás ganar {aura_total} puntos de Aura cuando sea confirmado.", "success")
    return redirect(whatsapp_link)

# --- RUTA PARA RECLAMAR RECOMPENSAS ---
@app.route("/reclamar_recompensa", methods=["POST"])
def reclamar_recompensa():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    
    user_emoji = session["logged_in_user_emoji"]
    usuarios = cargar_usuarios()
    
    if user_emoji not in usuarios:
        return jsonify({"success": False, "message": "Usuario no encontrado"})
    
    # Marcar que ya reclamó la recompensa de este nivel
    # Esto se puede implementar guardando el último nivel reclamado
    user_data = usuarios[user_emoji]
    current_points = user_data.get("aura_points", 0)
    
    # Determinar nivel actual
    current_level = 0
    for level_info in reversed(AURA_LEVELS):
        if current_points >= level_info["points_needed"]:
            current_level = level_info["level"]
            break
    
    # Marcar el nivel como reclamado
    if "claimed_levels" not in user_data:
        user_data["claimed_levels"] = []
    
    if current_level not in user_data["claimed_levels"]:
        user_data["claimed_levels"].append(current_level)
        usuarios[user_emoji] = user_data
        guardar_usuarios(usuarios)
        
        return jsonify({
            "success": True, 
            "message": "¡Recompensa reclamada con éxito!",
            "level": current_level
        })
    else:
        return jsonify({
            "success": False, 
            "message": "Ya has reclamado la recompensa de este nivel"
        })

# --- RUTA PARA CAMBIAR EMOJI DEL USUARIO ---
@app.route("/profile/change-emoji", methods=["POST"])
def change_user_emoji():
    if not session.get("logged_in_user_emoji"): 
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    new_emoji = data.get("new_emoji")
    current_emoji = session["logged_in_user_emoji"]
    
    if not new_emoji or new_emoji not in EMOJI_LIST:
        return jsonify({"success": False, "message": "Emoji no válido"})
    
    if new_emoji == current_emoji:
        return jsonify({"success": False, "message": "Ya tienes este emoji seleccionado"})
    
    usuarios = cargar_usuarios()
    
    # Verificar que el nuevo emoji no esté ocupado
    if new_emoji in usuarios:
        return jsonify({"success": False, "message": "Este emoji ya está ocupado por otro usuario"})
    
    # Verificar que el usuario actual exista
    if current_emoji not in usuarios:
        return jsonify({"success": False, "message": "Usuario actual no encontrado"})
    
    # Mover todos los datos del usuario al nuevo emoji
    user_data = usuarios[current_emoji].copy()
    usuarios[new_emoji] = user_data
    del usuarios[current_emoji]
    
    # Actualizar pedidos existentes con el nuevo emoji
    pedidos = cargar_pedidos()
    for pedido in pedidos:
        if pedido.get("user_emoji") == current_emoji:
            pedido["user_emoji"] = new_emoji
    guardar_pedidos(pedidos)
    
    # Guardar cambios y actualizar sesión
    guardar_usuarios(usuarios)
    session["logged_in_user_emoji"] = new_emoji
    
    return jsonify({
        "success": True, 
        "message": "Avatar cambiado exitosamente"
    })

# --- RUTA PARA ELIMINAR CUENTA DE USUARIO ---
@app.route("/profile/delete-account", methods=["POST"])
def delete_user_account():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    user_emoji = session["logged_in_user_emoji"]
    usuarios = cargar_usuarios()
    
    if user_emoji not in usuarios:
        return jsonify({"success": False, "message": "Usuario no encontrado"})
    
    # Eliminar todos los pedidos del usuario
    pedidos = cargar_pedidos()
    pedidos_filtrados = [p for p in pedidos if p.get("user_emoji") != user_emoji]
    guardar_pedidos(pedidos_filtrados)
    
    # Eliminar usuario
    del usuarios[user_emoji]
    guardar_usuarios(usuarios)
    
    # Cerrar sesión
    session.clear()
    
    return jsonify({
        "success": True, 
        "message": "Cuenta eliminada exitosamente"
    })

# --- RUTA PARA GENERAR CÓDIGOS DE RECOMPENSA ---
@app.route("/generate-reward-code", methods=["POST"])
def generate_reward_code():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    level = data.get("level")
    user_emoji = session["logged_in_user_emoji"]
    
    if not level:
        return jsonify({"success": False, "message": "Nivel no especificado"})
    
    usuarios = cargar_usuarios()
    if user_emoji not in usuarios:
        return jsonify({"success": False, "message": "Usuario no encontrado"})
    
    # Verificar que el usuario realmente alcanzó ese nivel
    user_points = usuarios[user_emoji].get("aura_points", 0)
    level_info = next((l for l in AURA_LEVELS if l["level"] == level), None)
    
    if not level_info or user_points < level_info["points_needed"]:
        return jsonify({"success": False, "message": "No tienes suficientes puntos para este nivel"})
    
    # Generar código único
    codigo = generar_codigo_recompensa()
    
    # Guardar código de reclamación (opcional, para tracking)
    if "reward_codes" not in usuarios[user_emoji]:
        usuarios[user_emoji]["reward_codes"] = {}
    
    usuarios[user_emoji]["reward_codes"][str(level)] = {
        "code": codigo,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "claimed": False
    }
    
    guardar_usuarios(usuarios)
    
    return jsonify({
        "success": True,
        "code": codigo,
        "level": level
    })

@app.route("/admin/recompensas", methods=["GET", "POST"])
def admin_recompensas():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        data = request.get_json()
        user_emoji = data.get("user_emoji")
        level = data.get("level")
        action = data.get("action")  # "confirm" o "reject"
        
        if not all([user_emoji, level, action]):
            return jsonify({"success": False, "message": "Datos incompletos"})
        
        usuarios = cargar_usuarios()
        if user_emoji not in usuarios:
            return jsonify({"success": False, "message": "Usuario no encontrado"})
        
        if "reward_codes" not in usuarios[user_emoji]:
            return jsonify({"success": False, "message": "No hay códigos de recompensa para este usuario"})
        
        level_str = str(level)
        if level_str not in usuarios[user_emoji]["reward_codes"]:
            return jsonify({"success": False, "message": "Código de recompensa no encontrado"})
        
        if action == "confirm":
            usuarios[user_emoji]["reward_codes"][level_str]["claimed"] = True
            usuarios[user_emoji]["reward_codes"][level_str]["confirmed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Marcar nivel como reclamado en el progreso del usuario
            if "progress_bar" not in usuarios[user_emoji]:
                usuarios[user_emoji]["progress_bar"] = {}
            if "claimed_levels" not in usuarios[user_emoji]["progress_bar"]:
                usuarios[user_emoji]["progress_bar"]["claimed_levels"] = []
            
            if level not in usuarios[user_emoji]["progress_bar"]["claimed_levels"]:
                usuarios[user_emoji]["progress_bar"]["claimed_levels"].append(level)
            
            message = "Recompensa confirmada exitosamente"
        
        elif action == "reject":
            del usuarios[user_emoji]["reward_codes"][level_str]
            message = "Código de recompensa rechazado"
        
        guardar_usuarios(usuarios)
        return jsonify({"success": True, "message": message})
    
    # GET - Mostrar recompensas pendientes
    usuarios = cargar_usuarios()
    recompensas_pendientes = []
    
    for user_emoji, user_data in usuarios.items():
        if "reward_codes" in user_data:
            for level, reward_info in user_data["reward_codes"].items():
                if not reward_info.get("claimed", False):
                    level_info = next((l for l in AURA_LEVELS if l["level"] == int(level)), None)
                    if level_info:
                        recompensas_pendientes.append({
                            "user_emoji": user_emoji,
                            "level": int(level),
                            "level_name": level_info["name"],
                            "prize": level_info["prize"],
                            "code": reward_info["code"],
                            "generated_at": reward_info["generated_at"],
                            "user_points": user_data.get("aura_points", 0)
                        })
    
    # Ordenar por fecha de generación
    recompensas_pendientes.sort(key=lambda x: x["generated_at"], reverse=True)
    
    return render_template("admin_recompensas.html", 
                         recompensas_pendientes=recompensas_pendientes,
                         config=cargar_configuracion())

# --- RUTAS DE CONFIGURACIÓN ADMIN ---
@app.route("/admin/configuracion", methods=["GET", "POST"])
def admin_configuracion():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    if request.method == "POST":
        # Cargar configuración actual
        config = cargar_configuracion()
        
        # Actualizar configuración
        config["horarios_atencion"] = request.form.get("horarios_atencion", config.get("horarios_atencion", ""))
        config["whatsapp_principal"] = request.form.get("whatsapp_principal", config.get("whatsapp_principal", ""))
        config["whatsapp_secundario"] = request.form.get("whatsapp_secundario", config.get("whatsapp_secundario", ""))
        config["whatsapp_1"] = request.form.get("whatsapp_1", config.get("whatsapp_1", ""))
        config["whatsapp_2"] = request.form.get("whatsapp_2", config.get("whatsapp_2", ""))
        config["whatsapp_3"] = request.form.get("whatsapp_3", config.get("whatsapp_3", ""))
        config["whatsapp_1_nombre"] = request.form.get("whatsapp_1_nombre", config.get("whatsapp_1_nombre", ""))
        config["whatsapp_2_nombre"] = request.form.get("whatsapp_2_nombre", config.get("whatsapp_2_nombre", ""))
        config["whatsapp_3_nombre"] = request.form.get("whatsapp_3_nombre", config.get("whatsapp_3_nombre", ""))
        
        # Guardar configuración en archivo
        guardar_configuracion(config)
        
        # Actualizar CONFIG global
        global CONFIG
        CONFIG = config
        
        flash("Configuración actualizada con éxito.", "success")
        return redirect(url_for("admin_configuracion"))
    
    return render_template("admin_config.html", config=CONFIG)

@app.route("/admin/reset-password", methods=["POST"])
def admin_reset_user_password():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    user_emoji = request.form.get("user_emoji")
    new_password = request.form.get("new_password")
    
    if not user_emoji or not new_password:
        flash("Debe proporcionar tanto el emoji del usuario como la nueva contraseña", "error")
        return redirect(url_for("admin_configuracion"))
    
    usuarios = cargar_usuarios()
    if user_emoji not in usuarios:
        flash(f"No se encontró un usuario con el emoji: {user_emoji}", "error")
        return redirect(url_for("admin_configuracion"))
    
    # Reiniciar la contraseña
    usuarios[user_emoji]["password_hash"] = generate_password_hash(new_password)
    guardar_usuarios(usuarios)
    
    flash(f"Contraseña reiniciada exitosamente para el usuario {user_emoji}", "success")
    return redirect(url_for("admin_configuracion"))

@app.route("/admin/reset-user-account", methods=["POST"])
def admin_reset_user_account():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    user_emoji = request.form.get("user_emoji")
    
    if not user_emoji:
        flash("Debe proporcionar el emoji del usuario", "error")
        return redirect(url_for("admin_emojis"))
    
    usuarios = cargar_usuarios()
    if user_emoji not in usuarios:
        flash(f"No se encontró un usuario con el emoji: {user_emoji}", "error")
        return redirect(url_for("admin_emojis"))
    
    # Reiniciar cuenta: mantener solo la contraseña, eliminar puntos de aura y datos
    password_hash = usuarios[user_emoji]["password_hash"]
    usuarios[user_emoji] = {
        "password_hash": password_hash,
        "aura_points": 0,
        "claimed_levels": []
    }
    guardar_usuarios(usuarios)
    
    # Eliminar todos los pedidos del usuario
    pedidos = cargar_pedidos()
    pedidos_filtrados = [p for p in pedidos if p.get("user_emoji") != user_emoji]
    guardar_pedidos(pedidos_filtrados)
    
    flash(f"Cuenta del usuario {user_emoji} reiniciada exitosamente", "success")
    return redirect(url_for("admin_emojis"))

# --- GESTIÓN DE EMOJIS EN ADMIN ---
@app.route("/admin/emojis", methods=["GET", "POST"])
def admin_emojis():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    global EMOJI_LIST
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_emoji":
            new_emoji = request.form.get("new_emoji")
            if new_emoji and new_emoji not in EMOJI_LIST:
                EMOJI_LIST.append(new_emoji)
                guardar_emoji_list(EMOJI_LIST)
                flash(f"Emoji {new_emoji} agregado exitosamente", "success")
            else:
                flash("Emoji ya existe o es inválido", "error")
                
        elif action == "remove_emoji":
            emoji_to_remove = request.form.get("emoji_to_remove")
            if emoji_to_remove in EMOJI_LIST:
                # Verificar que no esté en uso
                usuarios = cargar_usuarios()
                if emoji_to_remove in usuarios:
                    flash(f"No se puede eliminar {emoji_to_remove} porque está en uso", "error")
                else:
                    EMOJI_LIST.remove(emoji_to_remove)
                    guardar_emoji_list(EMOJI_LIST)
                    flash(f"Emoji {emoji_to_remove} eliminado exitosamente", "success")
            else:
                flash("Emoji no encontrado", "error")
        
        return redirect(url_for("admin_emojis"))
    
    usuarios = cargar_usuarios()
    return render_template("admin_emojis.html", 
                         emoji_list=EMOJI_LIST, 
                         usuarios=usuarios)

# --- GESTIÓN DE USUARIOS EN ADMIN ---
@app.route("/admin/change-user-emoji", methods=["POST"])
def admin_change_user_emoji():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    current_emoji = request.form.get("current_emoji")
    new_emoji = request.form.get("new_emoji")
    
    if not current_emoji or not new_emoji:
        flash("Debe proporcionar emoji actual y nuevo", "error")
        return redirect(url_for("admin_emojis"))
    
    if new_emoji not in EMOJI_LIST:
        flash("El nuevo emoji no está en la lista disponible", "error")
        return redirect(url_for("admin_emojis"))
    
    usuarios = cargar_usuarios()
    
    if current_emoji not in usuarios:
        flash(f"Usuario con emoji {current_emoji} no encontrado", "error")
        return redirect(url_for("admin_emojis"))
    
    if new_emoji in usuarios:
        flash(f"El emoji {new_emoji} ya está en uso", "error")
        return redirect(url_for("admin_emojis"))
    
    # Mover usuario al nuevo emoji
    user_data = usuarios[current_emoji].copy()
    usuarios[new_emoji] = user_data
    del usuarios[current_emoji]
    
    # Actualizar pedidos
    pedidos = cargar_pedidos()
    for pedido in pedidos:
        if pedido.get("user_emoji") == current_emoji:
            pedido["user_emoji"] = new_emoji
    guardar_pedidos(pedidos)
    
    guardar_usuarios(usuarios)
    
    flash(f"Usuario movido de {current_emoji} a {new_emoji} exitosamente", "success")
    return redirect(url_for("admin_emojis"))

# --- API PARA GESTIÓN DE EMOJIS ---
@app.route("/admin/emojis/add", methods=["POST"])
def admin_api_add_emoji():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    emoji = data.get("emoji")
    
    if not emoji:
        return jsonify({"success": False, "message": "Emoji no proporcionado"})
    
    global EMOJI_LIST
    
    if emoji in EMOJI_LIST:
        return jsonify({"success": False, "message": "El emoji ya existe en la lista"})
    
    # Verificar límite de 200 emojis
    if len(EMOJI_LIST) >= 200:
        return jsonify({"success": False, "message": "Se ha alcanzado el límite máximo de 200 emojis"})
    
    EMOJI_LIST.append(emoji)
    guardar_emoji_list(EMOJI_LIST)
    
    return jsonify({"success": True, "message": f"Emoji {emoji} agregado exitosamente. Total: {len(EMOJI_LIST)}/200"})

@app.route("/admin/emojis/remove", methods=["POST"])
def admin_api_remove_emoji():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    emoji = data.get("emoji")
    
    if not emoji:
        return jsonify({"success": False, "message": "Emoji no proporcionado"})
    
    global EMOJI_LIST
    
    if emoji not in EMOJI_LIST:
        return jsonify({"success": False, "message": "Emoji no encontrado en la lista"})
    
    # Verificar que no esté en uso
    usuarios = cargar_usuarios()
    if emoji in usuarios:
        return jsonify({"success": False, "message": f"No se puede eliminar {emoji} porque está en uso"})
    
    EMOJI_LIST.remove(emoji)
    guardar_emoji_list(EMOJI_LIST)
    
    return jsonify({"success": True, "message": f"Emoji {emoji} eliminado exitosamente"})

@app.route("/admin/users/change-emoji", methods=["POST"])
def admin_api_change_user_emoji():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    old_emoji = data.get("old_emoji")
    new_emoji = data.get("new_emoji")
    
    if not old_emoji or not new_emoji:
        return jsonify({"success": False, "message": "Emojis no proporcionados"})
    
    if new_emoji not in EMOJI_LIST:
        return jsonify({"success": False, "message": "El nuevo emoji no está en la lista disponible"})
    
    usuarios = cargar_usuarios()
    
    if old_emoji not in usuarios:
        return jsonify({"success": False, "message": f"Usuario con emoji {old_emoji} no encontrado"})
    
    if new_emoji in usuarios:
        return jsonify({"success": False, "message": f"El emoji {new_emoji} ya está en uso"})
    
    # Mover usuario al nuevo emoji
    user_data = usuarios[old_emoji].copy()
    usuarios[new_emoji] = user_data
    del usuarios[old_emoji]
    
    # Actualizar pedidos
    pedidos = cargar_pedidos()
    for pedido in pedidos:
        if pedido.get("user_emoji") == old_emoji:
            pedido["user_emoji"] = new_emoji
    guardar_pedidos(pedidos)
    
    guardar_usuarios(usuarios)
    
    return jsonify({"success": True, "message": f"Usuario movido de {old_emoji} a {new_emoji} exitosamente"})

# --- RUTA PARA COMPLETAR PEDIDOS Y OTORGAR AURA ---
@app.route("/admin/completar_pedido/<pedido_id>", methods=["POST"])
def admin_completar_pedido(pedido_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    pedidos = cargar_pedidos()
    productos = cargar_productos()
    usuarios = cargar_usuarios()
    
    # Buscar el pedido
    pedido_encontrado = None
    for pedido in pedidos:
        if pedido.get("id") == pedido_id:
            pedido_encontrado = pedido
            break
    
    if not pedido_encontrado:
        flash(f"Pedido {pedido_id} no encontrado", "error")
        return redirect(url_for("admin_view"))
    
    # Cambiar estado del pedido
    was_completed = pedido_encontrado.get("completado", False)
    pedido_encontrado["completado"] = not was_completed
    
    # Si se está marcando como completado por primera vez, otorgar puntos de aura
    if not was_completed and pedido_encontrado["completado"]:
        user_emoji = pedido_encontrado.get("user_emoji")
        if user_emoji and user_emoji in usuarios:
            # Calcular puntos de aura para este pedido
            aura_total = 0
            for cart_id, cant in pedido_encontrado.get("detalle", {}).items():
                parts = cart_id.split('-', 1)
                base_id = parts[0]
                prod_data = productos.get(base_id if len(parts) > 1 else cart_id)
                
                if not prod_data:
                    continue
                
                precio_item = 0
                if "bundle_items" in prod_data:
                    precio_item = prod_data.get("bundle_precio", 0)
                elif len(parts) > 1 and "variaciones" in prod_data:
                    variation_id = parts[1]
                    variation_data = prod_data["variaciones"].get(variation_id)
                    if variation_data:
                        precio_item = variation_data.get("precio", 0)
                elif "precio" in prod_data:
                    precio_item = prod_data.get("precio", 0)
                
                puntos_por_item = get_aura_points_for_product(base_id, precio_item)
                aura_total += puntos_por_item * cant
            
            # Otorgar puntos al usuario
            usuarios[user_emoji]["aura_points"] = usuarios[user_emoji].get("aura_points", 0) + aura_total
            guardar_usuarios(usuarios)
            
            # Actualizar el pedido con los puntos otorgados
            pedido_encontrado["aura_otorgada"] = aura_total
            
            flash(f"Pedido {pedido_id} completado. Se otorgaron {aura_total} puntos de aura al usuario {user_emoji}", "success")
        else:
            flash(f"Pedido {pedido_id} completado (usuario no encontrado para otorgar aura)", "warning")
    
    # Si se está desmarcando como completado, quitar puntos de aura
    elif was_completed and not pedido_encontrado["completado"]:
        user_emoji = pedido_encontrado.get("user_emoji")
        aura_otorgada = pedido_encontrado.get("aura_otorgada", 0)
        
        if user_emoji and user_emoji in usuarios and aura_otorgada > 0:
            usuarios[user_emoji]["aura_points"] = max(0, usuarios[user_emoji].get("aura_points", 0) - aura_otorgada)
            guardar_usuarios(usuarios)
            
            # Quitar la marca de aura otorgada
            pedido_encontrado.pop("aura_otorgada", None)
            
            flash(f"Pedido {pedido_id} marcado como no completado. Se quitaron {aura_otorgada} puntos de aura", "warning")
        else:
            flash(f"Pedido {pedido_id} marcado como no completado", "info")
    
    # Guardar cambios
    guardar_pedidos(pedidos)
    
    return redirect(url_for("admin_view"))

# --- RUTA PARA BORRAR PEDIDO INDIVIDUAL ---
@app.route("/admin/delete-order/<pedido_id>", methods=["POST"])
def admin_delete_order(pedido_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    pedidos = cargar_pedidos()
    usuarios = cargar_usuarios()
    
    # Buscar el pedido
    pedido_encontrado = None
    for i, pedido in enumerate(pedidos):
        if pedido.get("id") == pedido_id:
            pedido_encontrado = pedido
            pedido_index = i
            break
    
    if not pedido_encontrado:
        flash(f"Pedido {pedido_id} no encontrado", "error")
        return redirect(url_for("admin_view"))
    
    # Si el pedido estaba completado, quitar puntos de aura
    if pedido_encontrado.get("completado") and pedido_encontrado.get("aura_otorgada", 0) > 0:
        user_emoji = pedido_encontrado.get("user_emoji")
        aura_otorgada = pedido_encontrado.get("aura_otorgada", 0)
        
        if user_emoji and user_emoji in usuarios:
            usuarios[user_emoji]["aura_points"] = max(0, usuarios[user_emoji].get("aura_points", 0) - aura_otorgada)
            guardar_usuarios(usuarios)
    
    # Eliminar el pedido
    del pedidos[pedido_index]
    guardar_pedidos(pedidos)
    
    flash(f"Pedido {pedido_id} eliminado exitosamente", "success")
    return redirect(url_for("admin_view"))

@app.route("/admin/clear-orders", methods=["POST"])
def admin_clear_orders():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    # Crear una copia de respaldo antes de borrar
    import shutil
    import datetime
    
    backup_filename = f"pedidos_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        shutil.copy("pedidos.json", backup_filename)
    except FileNotFoundError:
        pass  # No hay archivo de pedidos para respaldar
    
    # Borrar todos los pedidos
    pedidos_vacios = []
    guardar_pedidos(pedidos_vacios)
    
    flash(f"TODOS los pedidos han sido eliminados. Se creó una copia de respaldo: {backup_filename}", "success")
    return redirect(url_for("admin_configuracion"))

# --- RUTAS DE GESTIÓN DE NIVELES DE AURA ---
@app.route("/admin/aura-levels", methods=["GET", "POST"])
def admin_aura_levels():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    global AURA_LEVELS
    
    if request.method == "POST":
        # Procesar archivos de personajes subidos
        for level_info in AURA_LEVELS:
            level = level_info["level"]
            character_file = request.files.get(f'character_{level}')
            
            if character_file and character_file.filename:
                filename = secure_filename(f"f{level}.gif")
                character_file.save(os.path.join('static', filename))
                level_info["character_gif"] = filename
            
            # Actualizar datos del nivel
            new_points = request.form.get(f'points_{level}')
            new_title = request.form.get(f'title_{level}')
            new_prize = request.form.get(f'prize_{level}')
            new_size = request.form.get(f'character_size_{level}')
            
            # Mejor validación para puntos
            if new_points is not None and new_points.strip() != '' and level != 0:
                try:
                    level_info["points_needed"] = int(new_points)
                except ValueError:
                    flash(f"Error: Puntos inválidos para nivel {level}", "error")
            
            if new_title is not None and new_title.strip() != '':
                level_info["name"] = new_title
            if new_prize is not None and new_prize.strip() != '':
                level_info["prize"] = new_prize
            if new_size is not None and new_size.strip() != '':
                try:
                    level_info["character_size"] = int(new_size)
                except ValueError:
                    flash(f"Error: Tamaño inválido para nivel {level}", "error")
        
        # Guardar cambios permanentemente
        guardar_aura_levels(AURA_LEVELS)
        
        # Recargar los niveles desde archivo para confirmar que se guardaron
        AURA_LEVELS = procesar_aura_levels_loaded(cargar_aura_levels())
        
        flash("Niveles de aura actualizados correctamente", "success")
        return redirect(url_for("admin_aura_levels"))
    
    return render_template("admin_aura_levels.html", levels=AURA_LEVELS)

# --- RUTAS DE GESTIÓN DE MEDIOS ---
@app.route("/admin/media", methods=["GET", "POST"])
def admin_media():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    if request.method == "POST":
        upload_type = request.form.get('upload_type')
        
        if upload_type == 'logo':
            logo_file = request.files.get('logo_file')
            if logo_file and logo_file.filename:
                # Hacer backup del logo actual
                try:
                    import shutil
                    shutil.copy('static/logo.png', f'static/logo_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                except:
                    pass
                
                # Guardar nuevo logo
                logo_file.save(os.path.join('static', 'logo.png'))
                flash("Logo actualizado correctamente", "success")
                
        elif upload_type == 'progress_bar':
            bar_type = request.form.get('bar_type')
            progress_file = request.files.get('progress_file')
            
            if progress_file and progress_file.filename and bar_type:
                filename = f"{bar_type}.png"
                progress_file.save(os.path.join('static', filename))
                flash(f"Barra {bar_type} actualizada correctamente", "success")
        
        return redirect(url_for("admin_media"))
    
    # Obtener lista de archivos en static/
    try:
        media_files = [f for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]
        media_files.sort()
    except:
        media_files = []
    
    return render_template("admin_media.html", media_files=media_files)

@app.route("/admin/delete-media", methods=["POST"])
def admin_delete_media():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"success": False, "message": "Nombre de archivo no especificado"})
    
    # Proteger archivos críticos
    protected_files = ['logo.png', 'style.css', 'script_fast.js']
    if filename in protected_files:
        return jsonify({"success": False, "message": "No se puede eliminar este archivo crítico"})
    
    try:
        file_path = os.path.join('static', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "Archivo eliminado correctamente"})
        else:
            return jsonify({"success": False, "message": "Archivo no encontrado"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al eliminar: {str(e)}"})

# --- RUTAS DE GESTIÓN DE PRODUCTOS ---
@app.route("/admin/productos")
def admin_productos():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    productos = cargar_productos()
    return render_template("admin_productos.html", productos=productos, config=CONFIG)

@app.route("/admin/agregar-producto", methods=["GET", "POST"])
def admin_agregar_producto():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    if request.method == "POST":
        productos = cargar_productos()
        
        # Obtener datos del formulario
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion", "")
        precio = float(request.form.get("precio"))
        stock = int(request.form.get("stock"))
        whatsapp_asignado = request.form.get("whatsapp_asignado", "1")
        
        # Manejar archivo de imagen
        imagen = request.files.get("imagen")
        imagen_filename = "default.png"  # imagen por defecto
        
        if imagen and imagen.filename:
            imagen_filename = secure_filename(imagen.filename)
            imagen.save(os.path.join("static", imagen_filename))
        
        # Crear ID único para el producto
        product_id = nombre.lower().replace(" ", "_").replace("ñ", "n")
        counter = 1
        original_id = product_id
        while product_id in productos:
            product_id = f"{original_id}_{counter}"
            counter += 1
        
        # Crear producto
        productos[product_id] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "stock": stock,
            "imagen": imagen_filename,
            "whatsapp_asignado": whatsapp_asignado,
            "orden": max([p.get("orden", 0) for p in productos.values()], default=0) + 1
        }
        
        guardar_productos(productos)
        flash(f"Producto '{nombre}' agregado exitosamente.", "success")
        return redirect(url_for("admin_productos"))
    
    return render_template("add_product.html", config=CONFIG)

@app.route("/admin/editar-producto/<product_id>", methods=["GET", "POST"])
def admin_editar_producto(product_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    productos = cargar_productos()
    if product_id not in productos:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("admin_productos"))
    
    if request.method == "POST":
        # Actualizar datos del producto
        productos[product_id]["nombre"] = request.form.get("nombre")
        productos[product_id]["descripcion"] = request.form.get("descripcion", "")
        productos[product_id]["precio"] = float(request.form.get("precio"))
        productos[product_id]["whatsapp_asignado"] = request.form.get("whatsapp_asignado", "1")
        
        if not productos[product_id].get("bundle_items"):  # Solo actualizar stock si no es bundle
            productos[product_id]["stock"] = int(request.form.get("stock"))
        
        # Manejar nueva imagen si se subió
        imagen = request.files.get("imagen")
        if imagen and imagen.filename:
            imagen_filename = secure_filename(imagen.filename)
            imagen.save(os.path.join("static", imagen_filename))
            productos[product_id]["imagen"] = imagen_filename
        
        guardar_productos(productos)
        flash(f"Producto '{productos[product_id]['nombre']}' actualizado exitosamente.", "success")
        return redirect(url_for("admin_productos"))
    
    return render_template("edit_product.html", producto=productos[product_id], product_id=product_id, config=CONFIG)

@app.route("/admin/upload-logo", methods=["POST"])
def admin_upload_logo():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    if 'logo' not in request.files:
        return jsonify({"success": False, "message": "No se seleccionó archivo"})
    
    file = request.files['logo']
    if file.filename == '':
        return jsonify({"success": False, "message": "No se seleccionó archivo"})
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        filename = secure_filename(file.filename)
        
        # Guardar con nombre fijo como logo.png
        logo_path = os.path.join("static", "logo.png")
        
        # Hacer backup del logo anterior
        if os.path.exists(logo_path):
            backup_path = os.path.join("static", f"logo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            os.rename(logo_path, backup_path)
        
        file.save(logo_path)
        
        flash("Logo actualizado exitosamente", "success")
        return jsonify({"success": True, "message": "Logo actualizado exitosamente"})
    else:
        return jsonify({"success": False, "message": "Formato de archivo no válido. Use PNG, JPG, JPEG o GIF."})

@app.route("/admin/upload-product-images", methods=["POST"])
def admin_upload_product_images():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"})
    
    product_id = request.form.get('product_id')
    if not product_id:
        return jsonify({"success": False, "message": "ID de producto no especificado"})
    
    # Cargar productos actuales
    productos = cargar_productos()
    if product_id not in productos:
        return jsonify({"success": False, "message": "Producto no encontrado"})
    
    # Procesar archivos subidos
    uploaded_files = request.files.getlist('images')
    if not uploaded_files:
        return jsonify({"success": False, "message": "No se subieron archivos"})
    
    try:
        # Inicializar imagenes_adicionales si no existe
        if 'imagenes_adicionales' not in productos[product_id]:
            productos[product_id]['imagenes_adicionales'] = {}
        
        # Encontrar el siguiente índice disponible
        existing_indices = [int(k) for k in productos[product_id]['imagenes_adicionales'].keys() if k.isdigit()]
        next_index = max(existing_indices, default=0) + 1
        
        uploaded_count = 0
        for file in uploaded_files:
            if file and file.filename:
                # Generar nombre de archivo único
                file_extension = file.filename.split('.')[-1].lower()
                new_filename = f"{product_id}_img_{next_index}.{file_extension}"
                
                # Guardar archivo
                file.save(os.path.join('static', new_filename))
                
                # Agregar a la lista de imágenes adicionales
                productos[product_id]['imagenes_adicionales'][str(next_index)] = new_filename
                
                next_index += 1
                uploaded_count += 1
        
        # Guardar productos actualizados
        guardar_productos(productos)
        
        return jsonify({
            "success": True, 
            "message": f"{uploaded_count} imágenes subidas correctamente"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al subir imágenes: {str(e)}"})
    
def guardar_productos(productos):
    """Guardar productos en el archivo JSON"""
    with open(PRODUCTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(productos, f, indent=4, ensure_ascii=False)

# --- API PARA CARRITO ---
def _get_cart_data():
    productos = cargar_productos()
    carrito = session.get('carrito', {})
    total_carrito = 0
    productos_en_carrito = {}
    for cart_id, cant in carrito.items():
        precio_item = 0
        nombre_item = "Producto Desconocido"
        prod_data_base = productos.get(cart_id)
        if prod_data_base and "bundle_precio" in prod_data_base:
            precio_item = prod_data_base.get("bundle_precio", 0)
            nombre_item = prod_data_base.get("nombre", "Paquete")
        else:
            parts = cart_id.split('-', 1)
            base_id = parts[0]
            variation_id = parts[1] if len(parts) > 1 else None
            prod_data = productos.get(base_id)
            if not prod_data: continue
            nombre_item = prod_data.get("nombre", "Producto Desconocido")
            if variation_id and "variaciones" in prod_data:
                variation_data = prod_data["variaciones"].get(variation_id)
                if not variation_data: continue
                precio_item = variation_data.get("precio", 0)
                nombre_item = f"{prod_data['nombre']} ({variation_id})"
            elif not variation_id and "precio" in prod_data:
                precio_item = prod_data.get("precio", 0)
        total_carrito += precio_item * cant
        productos_en_carrito[cart_id] = {"nombre": nombre_item, "precio": precio_item}
    return {"carrito": carrito, "total": round(total_carrito, 2), "productos_detalle": productos_en_carrito}

@app.route("/api/agregar/<path:product_cart_id>", methods=["POST"])
def api_agregar(product_cart_id):
    productos = cargar_productos()
    carrito = session.get('carrito', {})
    cantidad_en_carrito = carrito.get(product_cart_id, 0)
    stock_disponible = 0
    prod_data = productos.get(product_cart_id)
    if prod_data and "bundle_items" in prod_data:
        try:
            stocks_posibles = [productos.get(item_id, {}).get("stock", 0) // cant_nec for item_id, cant_nec in prod_data["bundle_items"].items()]
            stock_disponible = min(stocks_posibles) if stocks_posibles else 0
        except ZeroDivisionError:
            stock_disponible = 0
    else:
        parts = product_cart_id.split('-', 1)
        base_id = parts[0]
        variation_id = parts[1] if len(parts) > 1 else None
        prod_data_var = productos.get(base_id)
        if prod_data_var:
            if variation_id and "variaciones" in prod_data_var:
                stock_disponible = prod_data_var["variaciones"].get(variation_id, {}).get("stock", 0)
            elif not variation_id and "stock" in prod_data_var:
                stock_disponible = prod_data_var.get("stock", 0)
    if cantidad_en_carrito < stock_disponible:
        carrito[product_cart_id] = cantidad_en_carrito + 1
        session['carrito'] = carrito
        session.modified = True
    return jsonify(_get_cart_data())

@app.route("/api/quitar/<path:product_cart_id>", methods=["POST"])
def api_quitar(product_cart_id):
    carrito = session.get('carrito', {})
    if product_cart_id in carrito:
        if carrito[product_cart_id] > 1:
            carrito[product_cart_id] -= 1
        else:
            del carrito[product_cart_id]
    session['carrito'] = carrito
    session.modified = True
    return jsonify(_get_cart_data())

@app.route("/api/limpiar", methods=["POST"])
def api_limpiar():
    session.pop('carrito', None)
    return jsonify(_get_cart_data())

@app.route('/api/carrito')
def api_carrito():
    carrito = session.get('carrito', {})
    productos = cargar_productos()
    
    # Este bloque busca informaciÃ³n detallada de los productos
    productos_detalle = {}
    total = 0.0
    for prod_id, cantidad in carrito.items():
        base_id = prod_id.split('-')[0]  # En caso de variaciones
        producto = productos.get(base_id, {})
        
        nombre = producto.get('nombre', 'Desconocido')
        precio = 0.0
        
        if producto.get('variaciones') and '-' in prod_id:
            var_id = prod_id.split('-', 1)[1]
            precio = producto['variaciones'].get(var_id, {}).get('precio', 0.0)
        elif producto.get('bundle_precio'):
            precio = producto.get('bundle_precio', 0.0)
        else:
            precio = producto.get('precio', 0.0)

        productos_detalle[prod_id] = {
            'nombre': nombre,
            'precio': precio,
        }
        total += precio * cantidad

    return jsonify({
        'carrito': carrito,
        'productos_detalle': productos_detalle,
        'total': total
    })


# --- ACCIÃ“N DE COMPRA ---
@app.route("/comprar")
def comprar():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    productos = cargar_productos()
    carrito = session.get('carrito', {})
    if not carrito: return redirect(url_for("index"))
    
    puntos_aura_ganados = 0
    
    for cart_id, cant in carrito.items():
        parts = cart_id.split('-', 1)
        base_id = parts[0]
        variation_id = parts[1] if len(parts) > 1 else None
        prod_data = productos.get(base_id if variation_id else cart_id)
        if not prod_data:
            flash(f"Producto '{base_id}' ya no existe.", "error")
            return redirect(url_for("index"))
        
        precio_item = 0
        multiplier = prod_data.get("aura_multiplier", 1)
        
        if "bundle_items" in prod_data:
            precio_item = prod_data.get("bundle_precio", 0)
            for item_id, cant_nec in prod_data["bundle_items"].items():
                if productos.get(item_id, {}).get("stock", 0) < (cant_nec * cant):
                    flash(f"No hay suficiente stock para el paquete '{prod_data['nombre']}'.", "error")
                    return redirect(url_for("index"))
        elif variation_id and "variaciones" in prod_data:
            variation_data = prod_data["variaciones"].get(variation_id)
            if not variation_data or variation_data.get("stock", 0) < cant:
                flash(f"No hay suficiente stock para {prod_data['nombre']} ({variation_id}).", "error")
                return redirect(url_for("index"))
            precio_item = variation_data.get("precio", 0)
        elif "precio" in prod_data:
            if prod_data.get("stock", 0) < cant:
                flash(f"No hay suficiente stock para {prod_data['nombre']}.", "error")
                return redirect(url_for("index"))
            precio_item = prod_data.get("precio", 0)
        else:
            flash(f"Producto '{base_id}' mal configurado.", "error")
            return redirect(url_for("index"))
        # Usar la nueva función de cálculo de puntos de aura
        puntos_por_item = get_aura_points_for_product(base_id, precio_item)
        puntos_aura_ganados += puntos_por_item * cant

    for cart_id, cant in carrito.items():
        parts = cart_id.split('-', 1)
        base_id = parts[0]
        variation_id = parts[1] if len(parts) > 1 else None
        prod_data = productos.get(base_id if variation_id else cart_id)
        if "bundle_items" in prod_data:
            for item_id, cant_nec in prod_data["bundle_items"].items():
                productos[item_id]["stock"] -= (cant_nec * cant)
        elif variation_id and "variaciones" in prod_data:
            productos[base_id]["variaciones"][variation_id]["stock"] -= cant
        elif "stock" in prod_data:
            productos[base_id]["stock"] -= cant
    guardar_productos(productos)
    
    cart_data = _get_cart_data()
    total_general = cart_data["total"]
    libro_de_pedidos = cargar_pedidos()
    nuevo_id_pedido = generar_id_pedido()
    nuevo_pedido = {
        "id": nuevo_id_pedido, "timestamp": datetime.now().strftime("%d de %B, %Y a las %H:%M"),
        "detalle": carrito.copy(), "total": round(total_general, 2), "completado": False,
        "user_emoji": session.get("logged_in_user_emoji"), "puntos_ganados": puntos_aura_ganados
    }
    libro_de_pedidos.append(nuevo_pedido)
    guardar_pedidos(libro_de_pedidos)
    mensaje_partes = [f"*Â¡Que onda Corak! ocupo:* ðŸ›ï¸\n\n*Pedido #{nuevo_id_pedido}*\nResumen:"]
    for cart_id, cant in carrito.items():
        nombre_item = cart_data["productos_detalle"].get(cart_id, {}).get("nombre", "Item")
        precio_total_item = cant * cart_data["productos_detalle"].get(cart_id, {}).get("precio", 0)
        mensaje_partes.append(f"â€¢ {cant}x {nombre_item} - *${precio_total_item:.2f}*")
    mensaje_partes.append(f"\n*TOTAL DEL PEDIDO: ${total_general:.2f}*")
    mensaje_final = "\n".join(mensaje_partes)
    mensaje_formateado = urllib.parse.quote(mensaje_final)
    # Usar el número de WhatsApp principal de la configuración
    whatsapp_number = CONFIG["whatsapp_principal"]
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={mensaje_formateado}"
    
    session.pop('carrito', None)
    return redirect(whatsapp_url)

@app.route("/cronjob")
def cronjob():
    """Ruta especial para mantener el servidor activo con cronjobs"""
    return "Success", 200

if __name__ == "__main__":
    import os
    print("Iniciando servidor...")
    
    # Configuración para desarrollo vs producción
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    # Ejecutar aplicación Flask normal (sin Socket.IO)
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
