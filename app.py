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

# --- API PARA EMOJIS ---
EMOJI_LIST = ["😀", "🚀", "🌟", "🍕", "🤖", "👻", "👽", "👾", "🦊", "🧙", "🌮", "💎", "🌙", "🔮", "🧬", "🌵", "🎉", "🔥", "💯", "👑", "💡", "🎮", "🛰️", "🛸", "🗿", "🌴", "🧪", "✨", "🔑", "🗺️", "🐙", "🦋", "🐲", "🍩", "⚡", "🎯", "⚓", "🌈", "🌌", "🌠", "🎱", "🎰", "🕹️", "🏆", "💊", "🎁", "💌", "📈", "🗿"]

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

if __name__ == "__main__":
    import os
    print("Iniciando servidor...")
    
    # Configuración para desarrollo vs producción
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    # Ejecutar aplicación Flask normal (sin Socket.IO)
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
