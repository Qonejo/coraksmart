from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from whitenoise import WhiteNoise
from datetime import datetime
import urllib.parse
import os
import sys
import json
import string
import random
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import click

import requests
from uuid import uuid4

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

# --- SECRET KEY CONFIGURATION ---
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('RENDER'):
        raise ValueError("No SECRET_KEY set for production environment!")
    else:
        SECRET_KEY = 'dev-secret-key-for-local-testing-only'
        print("WARNING: Using default SECRET_KEY for local development.", file=sys.stderr)
app.secret_key = SECRET_KEY

# --- DATABASE CONFIGURATION ---
# Use the DATABASE_URL from Render, fallback to a local SQLite DB for development
db_url = os.environ.get('DATABASE_URL', 'sqlite:///corak.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- WHITENOISE CONFIGURATION ---
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/", max_age=31536000)

# --- CONSTANTS ---
UPLOAD_FOLDER = 'static'
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH") # It's better to use env vars

# --- SUPABASE STORAGE CONFIG ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "media")

def subir_a_supabase(file_storage):
    """
    Sube el archivo a Supabase Storage (bucket público) y regresa la URL pública.
    """
    nombre = f"{uuid4().hex}_{secure_filename(file_storage.filename)}"
    ruta = f"uploads/{nombre}"  # carpeta lógica en el bucket
    url_upload = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{ruta}"

    resp = requests.post(
        url_upload,
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": file_storage.mimetype or "application/octet-stream",
            "x-upsert": "false",
        },
        data=file_storage.read(),
        timeout=30,
    )
    resp.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{ruta}"


# --- DATABASE MODELS ---
class Product(db.Model):
    id = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(512))
    whatsapp_asignado = db.Column(db.String(10), default='1')
    orden = db.Column(db.Integer, default=999)
    promocion = db.Column(db.Boolean, default=False)
    variaciones = db.Column(JSON)
    bundle_items = db.Column(JSON)
    bundle_precio = db.Column(db.Float)
    imagenes_adicionales = db.Column(JSON)
    aura_multiplier = db.Column(db.Float, default=3.0, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model):
    emoji = db.Column(db.String(10), primary_key=True)
    password_hash = db.Column(db.String(256))
    aura_points = db.Column(db.Integer, default=0)
    claimed_levels = db.Column(JSON, default=list)
    reward_codes = db.Column(JSON, default=dict)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Order(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    user_emoji = db.Column(db.String(10), db.ForeignKey('user.emoji'))
    timestamp = db.Column(db.String(100))
    detalle = db.Column(JSON)
    detalle_completo = db.Column(JSON)
    total = db.Column(db.Float)
    aura_ganada = db.Column(db.Integer)
    aura_potencial = db.Column(db.Integer)
    aura_otorgada = db.Column(db.Integer)
    delivery_info = db.Column(JSON)
    completado = db.Column(db.Boolean, default=False)
    whatsapp_usado = db.Column(JSON)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Config(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)

class AuraLevel(db.Model):
    level = db.Column(db.Integer, primary_key=True)
    points_needed = db.Column(db.Float, nullable=False)
    flame_color = db.Column(db.String(50))
    name = db.Column(db.String(100))
    prize = db.Column(db.String(255))
    character_size = db.Column(db.Integer)

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if d.get('points_needed') == -float('inf'):
             d['points_needed'] = "-Infinity"
        return d

class Emoji(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emoji = db.Column(db.String(10), unique=True, nullable=False)


# --- DATA HELPER FUNCTIONS ---

@functools.lru_cache()
def get_default_config():
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

def get_config():
    """Cargar configuración desde la base de datos."""
    config_db = Config.query.all()
    if not config_db:
        return get_default_config()
    return {item.key: item.value for item in config_db}

def get_aura_levels():
    """Cargar niveles de aura desde la base de datos."""
    levels_db = AuraLevel.query.order_by(AuraLevel.level).all()
    if not levels_db:
        return [] # Should be populated by migration script

    levels = []
    for level in levels_db:
        level_dict = level.to_dict()
        if level_dict.get("points_needed") == "negative_infinity":
            level_dict["points_needed"] = -float('inf')
        levels.append(level_dict)
    return levels

def get_emoji_list():
    """Cargar lista de emojis desde la base de datos."""
    emojis_db = Emoji.query.order_by(Emoji.id).all()
    if not emojis_db:
        return [] # Should be populated by migration script
    return [e.emoji for e in emojis_db]


# --- API & AUTH ROUTES ---

@app.route('/api/get-emojis')
def api_get_emojis():
    """API endpoint to get all emojis and occupied ones."""
    all_emojis = get_emoji_list()
    occupied_users = User.query.with_entities(User.emoji).all()
    occupied_emojis = [user.emoji for user in occupied_users]
    return jsonify({
        'all_emojis': all_emojis,
        'occupied_emojis': occupied_emojis
    })


# --- AURA SYSTEM & ID GENERATORS ---

def get_user_aura_info(user_emoji):
    user = User.query.get(user_emoji)
    if not user:
        return None # Or handle as an error

    points = user.aura_points
    AURA_LEVELS = get_aura_levels()
    current_level_info = AURA_LEVELS[0] if AURA_LEVELS else {}
    for level_info in reversed(AURA_LEVELS):
        # Asegurar que points_needed es numérico
        points_needed = level_info["points_needed"]
        if isinstance(points_needed, str):
            try:
                points_needed = float(points_needed)
            except ValueError:
                points_needed = 0
        
        if points >= points_needed:
            current_level_info = level_info
            break

    character_gif = get_character_gif(points, current_level_info)
    current_level_info["character_gif"] = character_gif
    
    progress_bar_info = get_progress_bar_info(points, current_level_info, user_emoji)
    pending_rewards = check_pending_rewards(user_emoji)
    
    return {
        "points": points, 
        "level_info": current_level_info,
        "progress_bar": progress_bar_info,
        "pending_rewards": pending_rewards
    }

def get_character_gif(points, level_info):
    level = level_info.get("level", 0)
    AURA_LEVELS = get_aura_levels()
    
    if points == 0: return "f0.gif"
    if level == 1:
        next_level_points = next((l["points_needed"] for l in AURA_LEVELS if l["level"] == 2), None)
        if next_level_points:
            progress = points / next_level_points
            if progress < 1/3: return "f1a.gif"
            elif progress < 2/3: return "f1b.gif"
            else: return "f1c.gif"
        else: return "f1a.gif"
    elif 2 <= level <= 7: return f"f{level}.gif"
    return "f0.gif"

def get_progress_bar_info(points, current_level_info, user_emoji):
    """Función robusta para calcular información de la barra de progreso de aura."""
    level = current_level_info.get("level", 0)
    AURA_LEVELS = get_aura_levels()

    if level >= 7: 
        return {"bar_type": "barcom.gif", "exp_orbs": 0, "completed": True}
    
    next_level_info = next((l for l in AURA_LEVELS if l["level"] == level + 1), None)
    if not next_level_info: 
        return {"bar_type": "barcom.gif", "exp_orbs": 0, "completed": True}

    # Convertir todos los valores a números de forma segura
    def safe_float(value, default=0):
        try:
            if isinstance(value, str):
                return float(value)
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def safe_int(value, default=0):
        try:
            val = safe_float(value, default)
            if val == float('inf') or val == -float('inf') or val != val:  # NaN check
                return default
            return int(val)
        except (ValueError, TypeError, OverflowError):
            return default

    points = safe_float(points, 0)
    points_needed_for_next = safe_float(next_level_info["points_needed"], 1)
    current_points_needed = safe_float(current_level_info.get("points_needed", 0), 0)
    
    points_in_current_level = max(0, points - current_points_needed)
    points_needed_in_level = max(1, points_needed_for_next - current_points_needed)
    
    if points >= points_needed_for_next:
        user = User.query.get(user_emoji)
        claimed_levels = user.claimed_levels if user else []
        next_level = next_level_info["level"]
        return {
            "bar_type": "barcom.gif", "exp_orbs": 0, "completed": True,
            "level_up": next_level not in claimed_levels, "reward": next_level_info["prize"],
            "next_level": next_level, "points_in_level": safe_int(points_in_current_level),
            "points_needed_for_next": safe_int(points_needed_for_next)
        }
    
    # Cálculos seguros para orbes
    max_orbs = 8
    orb_value = max(240, points_needed_in_level / max_orbs) if points_needed_in_level > 0 else 240
    
    exp_orbs = safe_int(points_in_current_level / orb_value) if orb_value > 0 else 0
    exp_orbs = min(max_orbs, exp_orbs)
    
    bar_type = "barinic.png" if points_in_current_level >= 240 else "barva.png"
    progress_percent = safe_int((points_in_current_level / points_needed_in_level) * 100) if points_needed_in_level > 0 else 0
    
    return {
        "bar_type": bar_type, 
        "exp_orbs": exp_orbs, 
        "completed": False,
        "progress_percent": progress_percent, 
        "points_in_level": safe_int(points_in_current_level),
        "points_needed_for_next": safe_int(points_needed_for_next), 
        "orb_value": safe_int(orb_value)
    }

def codificar_numero(numero):
    if not isinstance(numero, int) or numero < 0: return str(numero)
    letras = string.ascii_uppercase
    indice_letra = numero % 26
    letra_codificada = letras[indice_letra]
    numero_ciclo = numero // 26
    return f"{letra_codificada}{numero_ciclo}" if numero_ciclo > 0 else letra_codificada

def generar_id_pedido():
    now = datetime.now()
    order_count = Order.query.count()
    parte_fecha = f"{codificar_numero(now.day - 1)}{codificar_numero(now.month - 1)}{now.strftime('%y')}"
    parte_hora = f"{codificar_numero(now.hour)}{codificar_numero(now.minute)}{codificar_numero(now.second)}"
    parte_pedido = codificar_numero(100 + order_count)
    sello_aleatorio = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{parte_fecha}-{parte_hora}-{parte_pedido}-{sello_aleatorio}"

def generar_codigo_recompensa():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def check_pending_rewards(user_emoji):
    user = User.query.get(user_emoji)
    if not user: return []

    AURA_LEVELS = get_aura_levels()
    current_points = user.aura_points
    claimed_levels = user.claimed_levels
    
    current_level = 0
    for level_info in reversed(AURA_LEVELS):
        # Asegurar que points_needed es numérico
        points_needed = level_info["points_needed"]
        if isinstance(points_needed, str):
            try:
                points_needed = float(points_needed)
            except ValueError:
                points_needed = 0
        
        if current_points >= points_needed:
            current_level = level_info["level"]
            break
    
    pending_rewards = []
    for level in range(1, current_level + 1):
        if level not in claimed_levels:
            level_info = next((l for l in AURA_LEVELS if l["level"] == level), None)
            if level_info:
                pending_rewards.append(level_info)
    return pending_rewards

def crear_mensaje_pedido(pedido, detalle_completo):
    delivery_info = pedido.get("delivery_info", {})
    mensaje_partes = [f"¡Que onda! 🛒", f"*Pedido #{pedido['id']}*"]
    for cart_id, info in detalle_completo.items():
        mensaje_partes.append(f"• {info['cantidad']}x {info['nombre']}")
    mensaje_partes.extend([f"*Total: ${pedido['total']:.2f}*",
                           f"📅 *Horario:* {delivery_info.get('day', 'N/A')} a las {delivery_info.get('time', 'N/A')}"])
    if delivery_info.get('station'): mensaje_partes.append(f"📍 *Zona:* {delivery_info.get('station', 'N/A')}")
    if delivery_info.get('instructions'): mensaje_partes.append(f"📝 *Notas:* {delivery_info['instructions']}")
    if delivery_info.get('phone'): mensaje_partes.append(f"📱 *Teléfono:* {delivery_info['phone']}")
    return "\n".join(mensaje_partes)

def determinar_whatsapp_destino(carrito, productos):
    CONFIG = get_config()
    whatsapp_counts = {"1": 0, "2": 0, "3": 0}
    for product_cart_id, cantidad in carrito.items():
        product_id = product_cart_id.split('-')[0]
        if product_id in productos:
            whatsapp_asignado = productos[product_id].get('whatsapp_asignado', '1')
            whatsapp_counts[whatsapp_asignado] += cantidad
    
    max_whatsapp = max(whatsapp_counts, key=whatsapp_counts.get)
    whatsapp_map = {
        "1": CONFIG.get('whatsapp_1'), "2": CONFIG.get('whatsapp_2'), "3": CONFIG.get('whatsapp_3')
    }
    whatsapp_numero = whatsapp_map.get(max_whatsapp) or CONFIG.get('whatsapp_principal')
    return whatsapp_numero, max_whatsapp
# --- MAIN VIEWS ---
@app.route("/entrar")
def entrar():
    return render_template("bienvenida.html")

@app.route("/")
def index():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    
    products_db = Product.query.order_by(Product.orden).all()
    productos_ordenados = [(p.id, p.to_dict()) for p in products_db]
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    return render_template("index.html",
                           PRODUCTOS_ORDENADOS=productos_ordenados,
                           PRODUCTOS=productos_dict,
                           aura_data=aura_data,
                           AURA_LEVELS=get_aura_levels())

@app.route("/perfil")
def perfil_usuario():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    
    pedidos_del_usuario = Order.query.filter_by(user_emoji=user_emoji).order_by(Order.timestamp.desc()).all()
    products_db = Product.query.all()
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    return render_template("perfil.html", user_emoji=user_emoji, pedidos=pedidos_del_usuario, PRODUCTOS=productos_dict, aura_data=aura_data, AURA_LEVELS=get_aura_levels())

@app.route('/procesar_pedido', methods=['POST'])
def procesar_pedido():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False, "message": "No has iniciado sesión."}), 401

    user_emoji = session["logged_in_user_emoji"]
    carrito = session.get('carrito', {})
    if not carrito:
        return jsonify({"success": False, "message": "Tu carrito está vacío."}), 400

    products_db = Product.query.all()
    productos_dict = {p.id: p for p in products_db}

    total = 0
    aura_total = 0
    detalle_completo = {}

    for cart_id, cant in carrito.items():
        parts = cart_id.split('-', 1)
        base_id = parts[0]
        prod_data = productos_dict.get(base_id)

        if not prod_data:
            return jsonify({"success": False, "message": f"Producto {base_id} no encontrado."}), 404

        precio_item = prod_data.precio or 0
        aura_multiplier = prod_data.aura_multiplier or 3.0

        if prod_data.bundle_precio is not None:
             precio_item = prod_data.bundle_precio
        elif len(parts) > 1 and prod_data.variaciones:
            variation_id = parts[1]
            variation_data = prod_data.variaciones.get(variation_id)
            if variation_data:
                precio_item = variation_data.get("precio", 0)

        total += precio_item * cant
        aura_total += int((precio_item * aura_multiplier) * cant)

        detalle_completo[cart_id] = {
            "nombre": prod_data.nombre,
            "precio": precio_item,
            "cantidad": cant,
            "subtotal": precio_item * cant
        }

    delivery_info = {
        "day": request.form.get("delivery_day"),
        "time": request.form.get("delivery_time"),
        "station": request.form.get("delivery_station"),
        "instructions": request.form.get("special_instructions"),
        "phone": request.form.get("phone_number"),
        "location_type": request.form.get("location_type")
    }

    new_order = Order(
        id=generar_id_pedido(),
        user_emoji=user_emoji,
        timestamp=datetime.now().isoformat(),
        detalle=carrito,
        detalle_completo=detalle_completo,
        total=total,
        aura_ganada=aura_total,
        delivery_info=delivery_info,
        completado=False
    )
    db.session.add(new_order)
    db.session.commit()

    session.pop('carrito', None)

    whatsapp_numero, _ = determinar_whatsapp_destino(carrito, {p.id: p.to_dict() for p in products_db})
    mensaje = crear_mensaje_pedido(new_order.to_dict(), detalle_completo)
    whatsapp_link = f"https://wa.me/{whatsapp_numero}?text={urllib.parse.quote(mensaje)}"

    return jsonify({
        "success": True,
        "message": "Pedido procesado con éxito. Serás redirigido a WhatsApp.",
        "whatsapp_link": whatsapp_link
    })

# ... Will continue to refactor all routes and helpers
# This is a very large file. The agent will continue refactoring.
# For brevity, I will now apply the fully refactored file.

@app.route("/login", methods=["GET", "POST"])
def login():
    if not ADMIN_PASSWORD_HASH:
        flash("La aplicación no está configurada correctamente. No se ha definido un hash de contraseña de administrador.", "error")
        return render_template("login.html")

    if request.method == "POST":
        password = request.form.get("password")
        if password and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            flash("Contraseña incorrecta.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("logged_in_user_emoji", None)
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("entrar"))

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    historial = []

    # Get all orders and add them to the history
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    for order in orders:
        try:
            # Assuming timestamp is stored in a format parsable by datetime
            timestamp = datetime.fromisoformat(str(order.timestamp))
        except (ValueError, TypeError):
            # Fallback for invalid or missing timestamps
            timestamp = datetime.now()

        historial.append({
            "id": order.id,
            "type": "pedido",
            "user_emoji": order.user_emoji,
            "timestamp_obj": timestamp,
            "timestamp_str": timestamp.strftime("%d/%m/%Y %H:%M"),
            "details": f"Pedido con {len(order.detalle or [])} items.",
            "total": order.total,
            "status": order.completado,
            "data": order.to_dict()
        })

    # Get all pending rewards and add them to the history
    users = User.query.all()
    for user in users:
        pending_rewards = check_pending_rewards(user.emoji)
        for reward in pending_rewards:
            historial.append({
                "id": f"{user.emoji}-{reward['level']}",
                "type": "recompensa",
                "user_emoji": user.emoji,
                "timestamp_obj": datetime.now(), # Rewards are always "current"
                "timestamp_str": "Reclamar ahora",
                "details": f"Recompensa Nivel {reward['level']}: {reward['prize']}",
                "total": 0,
                "status": False, # Not 'complete' until claimed
                "data": { "user_emoji": user.emoji, "level": reward['level'] }
            })

    # Sort the combined history by the timestamp object
    historial.sort(key=lambda x: x['timestamp_obj'], reverse=True)

    return render_template("admin.html", historial=historial)

@app.route("/admin/productos", methods=["GET"])
def admin_productos():
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = Product.query.order_by(Product.orden).all()
    return render_template("admin_productos.html", productos=productos, config=get_config())

@app.route("/admin/editar-producto/<product_id>", methods=["GET", "POST"])
def admin_editar_producto(product_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    producto = Product.query.get_or_404(product_id)
    
    if request.method == "POST":
        producto.nombre = request.form.get("nombre")
        producto.descripcion = request.form.get("descripcion", "")
        producto.whatsapp_asignado = request.form.get("whatsapp_asignado", "1")
        producto.promocion = 'promocion' in request.form

        product_type = request.form.get('product_type')
        if product_type == 'simple':
            producto.precio = float(request.form.get('precio', 0))
            producto.stock = int(request.form.get('stock', 0))
            producto.variaciones = None
        elif product_type == 'variable':
            new_variations = {}
            # Simplified form processing
            i = 0
            while f'variation-name-{i}' in request.form:
                name = request.form.get(f'variation-name-{i}')
                price = request.form.get(f'variation-price-{i}')
                stock = request.form.get(f'variation-stock-{i}')
                if name and price and stock:
                    new_variations[name] = {'precio': float(price), 'stock': int(stock)}
                i += 1
            producto.variaciones = new_variations
            producto.precio = None
            producto.stock = None

        if 'imagen' in request.files:
            imagen = request.files["imagen"]
            if imagen.filename:
                imagen_filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(UPLOAD_FOLDER, imagen_filename))
                producto.imagen = imagen_filename
        
        producto.aura_multiplier = float(request.form.get("aura_multiplier", 3.0))
        db.session.commit()
        flash(f"Producto '{producto.nombre}' actualizado.", "success")
        return redirect(url_for("admin_productos"))
    
    return render_template("edit_product.html", producto=producto, product_id=product_id, config=get_config())

@app.route("/admin/agregar-producto", methods=["GET", "POST"])
def admin_agregar_producto():
    if not session.get("logged_in"): return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form.get("nombre")
        product_id = nombre.lower().replace(" ", "_").replace("ñ", "n")
        if Product.query.get(product_id):
            flash("Un producto con este ID ya existe.", "error")
            return redirect(url_for("admin_agregar_producto"))

        imagen_filename = "default.png"
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename:
                imagen_filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(UPLOAD_FOLDER, imagen_filename))

        max_orden = db.session.query(db.func.max(Product.orden)).scalar() or 0
        
        nuevo_producto = Product(
            id=product_id,
            nombre=nombre,
            descripcion=request.form.get("descripcion", ""),
            precio=float(request.form.get("precio")),
            stock=int(request.form.get("stock")),
            whatsapp_asignado=request.form.get("whatsapp_asignado", "1"),
            imagen=imagen_filename,
            orden=max_orden + 1,
            promocion='promocion' in request.form,
            aura_multiplier=float(request.form.get("aura_multiplier", 3.0))
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash(f"Producto '{nombre}' agregado.", "success")
        return redirect(url_for("admin_productos"))
    return render_template("add_product.html", config=get_config())

@app.route("/admin/eliminar-producto/<product_id>", methods=["POST"])
def admin_eliminar_producto(product_id):
    if not session.get("logged_in"): return jsonify({"success": False}), 401
    
    producto = Product.query.get(product_id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/admin/completar-pedido/<pedido_id>", methods=["POST"])
def admin_completar_pedido(pedido_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    order = Order.query.get(pedido_id)
    if order:
        user = User.query.get(order.user_emoji)

        # Toggle completion status
        order.completado = not order.completado

        if user and order.aura_ganada:
            if order.completado:
                user.aura_points = (user.aura_points or 0) + order.aura_ganada
                flash(f"Pedido completado. Se sumaron {order.aura_ganada} puntos de Aura a {user.emoji}.", "success")
            else:
                user.aura_points = (user.aura_points or 0) - order.aura_ganada
                flash(f"Pedido desmarcado. Se restaron {order.aura_ganada} puntos de Aura a {user.emoji}.", "warning")

        db.session.commit()
    else:
        flash("Pedido no encontrado.", "error")

    return redirect(url_for("admin"))

@app.route("/admin/delete-order/<pedido_id>", methods=["POST"])
def admin_delete_order(pedido_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    order = Order.query.get(pedido_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash(f"Pedido {pedido_id} eliminado.", "success")
    else:
        flash("Pedido no encontrado.", "error")

    return redirect(url_for("admin"))

@app.route("/admin/recompensas", methods=["POST"])
def admin_recompensas():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "No autorizado"}), 401

    data = request.get_json()
    user_emoji = data.get("user_emoji")
    level = data.get("level")
    action = data.get("action")

    user = User.query.get(user_emoji)
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    claimed_levels = user.claimed_levels or []
    if level in claimed_levels:
        return jsonify({"success": False, "message": "Esta recompensa ya fue procesada."}), 400

    if action == "confirm":
        user.claimed_levels = claimed_levels + [level]

        reward_codes = user.reward_codes or {}
        new_code = generar_codigo_recompensa()
        reward_codes[str(level)] = new_code
        user.reward_codes = reward_codes

        db.session.commit()
        return jsonify({"success": True, "message": f"Recompensa para {user_emoji} confirmada. Código: {new_code}"})

    elif action == "reject":
        user.claimed_levels = claimed_levels + [level]
        db.session.commit()
        return jsonify({"success": True, "message": f"Recompensa para {user_emoji} rechazada."})

    else:
        return jsonify({"success": False, "message": "Acción no válida"}), 400

@app.route('/admin/emojis')
def admin_emojis():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    users = User.query.all()
    return render_template('admin_emojis.html', users=users)

@app.route('/admin/aura-levels', methods=['GET', 'POST'])
def admin_aura_levels():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('points_needed-'):
                level_id = int(key.split('-')[1])
                level = AuraLevel.query.get(level_id)
                if level:
                    try:
                        level.points_needed = float(value)
                        level.flame_color = request.form.get(f'flame_color-{level_id}')
                        level.name = request.form.get(f'name-{level_id}')
                        level.prize = request.form.get(f'prize-{level_id}')
                        level.character_size = int(request.form.get(f'character_size-{level_id}'))
                    except (ValueError, TypeError):
                        flash(f'Valor inválido para el nivel {level_id}', 'error')
        db.session.commit()
        flash('Niveles de Aura actualizados.', 'success')
        return redirect(url_for('admin_aura_levels'))

    levels = AuraLevel.query.order_by(AuraLevel.level).all()
    return render_template('admin_aura_levels.html', levels=levels)

@app.route('/api/get-emojis')
def get_emojis_api():
    all_emojis_from_db = get_emoji_list()
    users = User.query.all()
    occupied_emojis = [user.emoji for user in users]
    return jsonify({
        "all_emojis": all_emojis_from_db,
        "occupied_emojis": occupied_emojis
    })

@app.route('/api/emoji-access', methods=['POST'])
def emoji_access_api():
    data = request.get_json()
    emoji = data.get("emoji")
    password = data.get("password")

    if not emoji or not password:
        return jsonify({"success": False, "message": "Datos inválidos."})

    all_emojis_from_db = get_emoji_list()
    if emoji not in all_emojis_from_db:
        return jsonify({"success": False, "message": "Emoji no válido."})

    user = User.query.get(emoji)
    if user:
        if check_password_hash(user.password_hash, password):
            session["logged_in_user_emoji"] = emoji
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Contraseña incorrecta."})
    else:
        new_user = User(
            emoji=emoji,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        session["logged_in_user_emoji"] = emoji
        return jsonify({"success": True, "message": "¡Avatar registrado con éxito!"})

@app.route("/niveles")
def niveles_aura():
    if not session.get("logged_in_user_emoji"): 
        return redirect(url_for("entrar"))
    
    user_emoji = session["logged_in_user_emoji"]
    aura_data = get_user_aura_info(user_emoji)
    
    return render_template("niveles.html", 
                         aura_data=aura_data, 
                         AURA_LEVELS=get_aura_levels(),
                         config=get_config())

@app.route("/checkout")
def checkout():
    if not session.get("logged_in_user_emoji"): 
        return redirect(url_for("entrar"))
    
    carrito = session.get('carrito', {})
    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for("index"))
    
    products_db = Product.query.all()
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    # Calcular totales
    carrito_items = list(carrito.items())
    item_total = {}
    total = 0
    
    for cart_id, cantidad in carrito.items():
        base_id = cart_id.split('-')[0]
        if base_id in productos_dict:
            producto = productos_dict[base_id]
            precio = producto.get('precio', 0)
            subtotal = precio * cantidad
            item_total[cart_id] = subtotal
            total += subtotal
    
    return render_template("checkout.html",
                         carrito_items=carrito_items,
                         productos=productos_dict,
                         item_total=item_total,
                         total=total,
                         config=get_config())

# --- API RUTAS PARA CARRITO ---

@app.route('/api/carrito')
def api_carrito():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"carrito": {}, "productos_detalle": {}}), 401
    
    carrito = session.get('carrito', {})
    products_db = Product.query.all()
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    productos_detalle = {}
    for cart_id, cantidad in carrito.items():
        base_id = cart_id.split('-')[0]
        if base_id in productos_dict:
            producto = productos_dict[base_id]
            productos_detalle[cart_id] = {
                "nombre": producto["nombre"],
                "precio": producto.get("precio", 0),
                "imagen": producto.get("imagen", "")
            }
    
    return jsonify({
        "carrito": carrito,
        "productos_detalle": productos_detalle
    })

@app.route('/api/agregar/<product_id>', methods=['POST'])
def api_agregar_carrito(product_id):
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False}), 401
    
    carrito = session.get('carrito', {})
    carrito[product_id] = carrito.get(product_id, 0) + 1
    session['carrito'] = carrito
    
    # Retornar datos actualizados
    products_db = Product.query.all()
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    productos_detalle = {}
    for cart_id, cantidad in carrito.items():
        base_id = cart_id.split('-')[0]
        if base_id in productos_dict:
            producto = productos_dict[base_id]
            productos_detalle[cart_id] = {
                "nombre": producto["nombre"],
                "precio": producto.get("precio", 0),
                "imagen": producto.get("imagen", "")
            }
    
    return jsonify({
        "carrito": carrito,
        "productos_detalle": productos_detalle
    })

@app.route('/api/quitar/<product_id>', methods=['POST'])
def api_quitar_carrito(product_id):
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False}), 401
    
    carrito = session.get('carrito', {})
    if product_id in carrito:
        carrito[product_id] -= 1
        if carrito[product_id] <= 0:
            del carrito[product_id]
    session['carrito'] = carrito
    
    # Retornar datos actualizados
    products_db = Product.query.all()
    productos_dict = {p.id: p.to_dict() for p in products_db}
    
    productos_detalle = {}
    for cart_id, cantidad in carrito.items():
        base_id = cart_id.split('-')[0]
        if base_id in productos_dict:
            producto = productos_dict[base_id]
            productos_detalle[cart_id] = {
                "nombre": producto["nombre"],
                "precio": producto.get("precio", 0),
                "imagen": producto.get("imagen", "")
            }
    
    return jsonify({
        "carrito": carrito,
        "productos_detalle": productos_detalle
    })

@app.route('/api/limpiar', methods=['POST'])
def api_limpiar_carrito():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False}), 401
    
    session['carrito'] = {}
    return jsonify({
        "carrito": {},
        "productos_detalle": {}
    })

@app.route('/generate-reward-code', methods=['POST'])
def generate_reward_code():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False, "message": "No autorizado"}), 401
    
    user_emoji = session["logged_in_user_emoji"]
    data = request.get_json()
    level = data.get("level")
    
    user = User.query.get(user_emoji)
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    
    # Verificar que el usuario puede reclamar este nivel
    claimed_levels = user.claimed_levels or []
    if level in claimed_levels:
        return jsonify({"success": False, "message": "Esta recompensa ya fue reclamada"}), 400
    
    # Verificar que el usuario tiene suficientes puntos
    aura_levels = get_aura_levels()
    level_info = next((l for l in aura_levels if l["level"] == level), None)
    if not level_info or user.aura_points < level_info["points_needed"]:
        return jsonify({"success": False, "message": "No tienes suficientes puntos para este nivel"}), 400
    
    # Generar código y marcar como reclamado
    code = generar_codigo_recompensa()
    user.claimed_levels = claimed_levels + [level]
    
    reward_codes = user.reward_codes or {}
    reward_codes[str(level)] = code
    user.reward_codes = reward_codes
    
    db.session.commit()
    
    return jsonify({"success": True, "code": code})

@app.route('/reclamar_recompensa', methods=['POST'])
def reclamar_recompensa():
    if not session.get("logged_in_user_emoji"):
        return jsonify({"success": False, "message": "No autorizado"}), 401
    
    user_emoji = session["logged_in_user_emoji"]
    user = User.query.get(user_emoji)
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    
    # Obtener recompensas pendientes
    pending_rewards = check_pending_rewards(user_emoji)
    if not pending_rewards:
        return jsonify({"success": False, "message": "No tienes recompensas pendientes"}), 400
    
    # Reclamar la primera recompensa pendiente
    reward = pending_rewards[0]
    level = reward["level"]
    
    claimed_levels = user.claimed_levels or []
    user.claimed_levels = claimed_levels + [level]
    
    # Generar código de recompensa
    code = generar_codigo_recompensa()
    reward_codes = user.reward_codes or {}
    reward_codes[str(level)] = code
    user.reward_codes = reward_codes
    
    db.session.commit()
    
    return jsonify({"success": True, "code": code, "level": level, "prize": reward["prize"]})

@app.route("/admin/configuracion", methods=["GET", "POST"])
def admin_configuracion():
    if not session.get("logged_in"): return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_config":
            for key, value in request.form.items():
                if key != "action":
                    config_item = Config.query.get(key)
                    if config_item:
                        config_item.value = value
                    else:
                        db.session.add(Config(key=key, value=value))
            db.session.commit()
            flash("Configuración actualizada.", "success")

        elif action == "clear_orders":
            try:
                num_deleted = db.session.query(Order).delete()
                db.session.commit()
                flash(f"{num_deleted} pedidos eliminados.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al eliminar pedidos: {e}", "error")

        elif action == "reset_all_users":
            try:
                users = User.query.all()
                for user in users:
                    user.aura_points = 0
                    user.claimed_levels = []
                    user.reward_codes = {}
                db.session.commit()
                flash("Todos los usuarios reseteados.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al resetear usuarios: {e}", "error")

        return redirect(url_for("admin_configuracion"))
    
    return render_template("admin_config.html", config=get_config())

# --- INIT DB COMMAND ---
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

@app.cli.command("hash-password")
@click.argument("password")
def hash_password_command(password):
    """Hashes the given password."""
    hashed_password = generate_password_hash(password)
    print("--- Hashed Admin Password ---")
    print(hashed_password)
    print("--- End Hashed Admin Password ---")
    print("\nSet this value as the ADMIN_PASSWORD_HASH environment variable.")

if __name__ == "__main__":
    with app.app_context():
        # This is a simple way to ensure tables are created for local dev
        # For production, a proper migration tool like Alembic is recommended
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')