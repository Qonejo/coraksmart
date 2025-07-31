from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import urllib.parse
import os
import json
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from collections import OrderedDict

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- CONFIGURACIÓN DE ARCHIVOS ---
ADMIN_PASSWORD = "coraker"
PEDIDOS_FILE = "pedidos.json"
PRODUCTOS_FILE = "productos.json"
USUARIOS_FILE = "usuarios.json"

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
    {"level": 1, "points_needed": 0,   "flame_color": "white",  "prize": "Acceso Básico"},
    {"level": 2, "points_needed": 5,   "flame_color": "blue",   "prize": "Cupón de 5% de Descuento"},
    {"level": 3, "points_needed": 15,  "flame_color": "green",  "prize": "Producto Sorpresa Pequeño"},
    {"level": 4, "points_needed": 30,  "flame_color": "yellow", "prize": "Cupón de 10% de Descuento"},
    {"level": 5, "points_needed": 50,  "flame_color": "orange", "prize": "Envío Gratis"},
    {"level": 6, "points_needed": 75,  "flame_color": "red",    "prize": "Acceso a Productos Exclusivos"},
    {"level": 7, "points_needed": 100, "flame_color": "purple", "prize": "Regalo Misterioso de Alto Valor"}
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

    productos_ordenados = sorted(productos_dict.items(), key=lambda item: item[1].get('orden', 999))

    # --- ¡CAMBIO IMPORTANTE AQUÍ! ---
    # Pasamos la lista ordenada como 'PRODUCTOS_ORDENADOS'
    # y el diccionario original como 'PRODUCTOS_DICT'
    return render_template(
        "index.html",
        PRODUCTOS_ORDENADOS=productos_ordenados,
        PRODUCTOS_DICT=productos_dict,
        aura_data=aura_data
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

    # --- LÓGICA DE ORDENAMIENTO (TAMBIÉN GENERA UNA LISTA) ---
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

# --- RUTAS DE ADMINISTRACIÓN COMPLETAS ---
@app.route("/admin/actualizar-productos", methods=["POST"])
def admin_actualizar_productos():
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = cargar_productos()
    for key, value in request.form.items():
        try:
            if key.startswith("orden-"):
                product_id = key.replace("orden-", "", 1)
                if product_id in productos:
                    productos[product_id]["orden"] = int(value) if value else 999
            elif key.startswith("stock-"):
                if not value.strip(): continue
                full_id = key.replace("stock-", "", 1)
                parts = full_id.split('-', 1)
                base_id = parts[0]
                variation_id = parts[1] if len(parts) > 1 else None
                if base_id in productos:
                    nuevo_stock = int(value)
                    if variation_id and "variaciones" in productos[base_id]:
                        if variation_id in productos[base_id]["variaciones"]:
                            productos[base_id]["variaciones"][variation_id]["stock"] = nuevo_stock
                    elif not variation_id and "stock" in productos[base_id]:
                        productos[base_id]["stock"] = nuevo_stock
        except (ValueError, TypeError): continue
    guardar_productos(productos)
    flash("¡Productos actualizados con éxito!", "success")
    return redirect(url_for("admin_view"))

@app.route("/admin/completar-pedido/<pedido_id>", methods=["POST"])
def admin_completar_pedido(pedido_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    pedidos = cargar_pedidos()
    usuarios = cargar_usuarios()
    pedido_encontrado = None
    for pedido in pedidos:
        if pedido.get("id") == pedido_id:
            pedido_encontrado = pedido
            break
    if pedido_encontrado:
        pedido_encontrado["completado"] = not pedido_encontrado.get("completado", False)
        user_emoji = pedido_encontrado.get("user_emoji")
        if user_emoji and user_emoji in usuarios:
            if pedido_encontrado["completado"]:
                usuarios[user_emoji]["aura_points"] = usuarios[user_emoji].get("aura_points", 0) + 1
                flash(f"Pedido completado. Se sumó 1 punto de Aura a {user_emoji}.", "success")
            else:
                usuarios[user_emoji]["aura_points"] = usuarios[user_emoji].get("aura_points", 0) - 1
                if usuarios[user_emoji]["aura_points"] < 0:
                    usuarios[user_emoji]["aura_points"] = 0
                flash(f"Pedido desmarcado. Se restó 1 punto de Aura a {user_emoji}.", "success")
            guardar_usuarios(usuarios)
    guardar_pedidos(pedidos)
    return redirect(url_for("admin_view"))

@app.route("/admin/agregar-producto", methods=["GET", "POST"])
def admin_agregar_producto():
    if not session.get("logged_in"): return redirect(url_for("login"))
    if request.method == "POST":
        productos = cargar_productos()
        nombre_base = request.form.get("nombre", "nuevo_producto").lower().replace(" ", "_")
        product_id = "".join(c for c in nombre_base if c.isalnum() or c == '_')
        contador = 1
        while product_id in productos:
            product_id = f"{nombre_base}_{contador}"
            contador += 1
        imagen_nombre = "default.png"
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                imagen_nombre = secure_filename(file.filename)
                file_path = os.path.join('/home/Qonejo/coraksmart/', app.config['UPLOAD_FOLDER'], imagen_nombre)
                file.save(file_path)
        nuevo_producto = {
            "nombre": request.form.get("nombre"), "descripcion": request.form.get("descripcion"),
            "imagen": imagen_nombre, "stock": int(request.form.get("stock", 0)),
            "precio": float(request.form.get("precio", 0.0))
        }
        productos[product_id] = nuevo_producto
        guardar_productos(productos)
        flash(f"Producto '{nuevo_producto['nombre']}' añadido con éxito.", "success")
        return redirect(url_for("admin_view"))
    return render_template("add_product.html")

@app.route("/admin/editar-producto/<product_id>", methods=["GET", "POST"])
def admin_editar_producto(product_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = cargar_productos()
    producto_a_editar = productos.get(product_id)
    if not producto_a_editar:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("admin_view"))
    if request.method == "POST":
        producto_a_editar["nombre"] = request.form.get("nombre")
        producto_a_editar["descripcion"] = request.form.get("descripcion")
        if "variaciones" not in producto_a_editar and "bundle_items" not in producto_a_editar:
            producto_a_editar["stock"] = int(request.form.get("stock", 0))
            producto_a_editar["precio"] = float(request.form.get("precio", 0.0))
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                imagen_nombre = secure_filename(file.filename)
                file_path = os.path.join('/home/Qonejo/coraksmart/', app.config['UPLOAD_FOLDER'], imagen_nombre)
                file.save(file_path)
                producto_a_editar["imagen"] = imagen_nombre
        productos[product_id] = producto_a_editar
        guardar_productos(productos)
        flash(f"Producto '{producto_a_editar['nombre']}' actualizado.", "success")
        return redirect(url_for("admin_view"))
    return render_template("edit_product.html", producto=producto_a_editar, product_id=product_id)

@app.route("/admin/eliminar-producto/<product_id>", methods=["POST"])
def admin_eliminar_producto(product_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = cargar_productos()
    if product_id in productos:
        producto_eliminado = productos.pop(product_id)
        try:
            if producto_eliminado.get('imagen') and producto_eliminado.get('imagen') != 'default.png':
                file_path = os.path.join('/home/Qonejo/coraksmart/', app.config['UPLOAD_FOLDER'], producto_eliminado['imagen'])
                os.remove(file_path)
        except (FileNotFoundError, KeyError): pass
        guardar_productos(productos)
        flash(f"Producto '{producto_eliminado.get('nombre', 'ID: '+product_id)}' eliminado.", "success")
    else:
        flash("Producto no encontrado.", "error")
    return redirect(url_for("admin_view"))

@app.route("/admin/crear-paquete", methods=["GET", "POST"])
def admin_crear_paquete():
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = cargar_productos()
    if request.method == "POST":
        nombre_base = request.form.get("nombre", "nuevo_paquete").lower().replace(" ", "_")
        paquete_id = "".join(c for c in nombre_base if c.isalnum() or c == '_')
        contador = 1
        while paquete_id in productos:
            paquete_id = f"{nombre_base}_{contador}"
            contador += 1
        imagen_nombre = "default.png"
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                imagen_nombre = secure_filename(file.filename)
                file_path = os.path.join('/home/Qonejo/coraksmart/', app.config['UPLOAD_FOLDER'], imagen_nombre)
                file.save(file_path)
        bundle_items = {}
        for key, value in request.form.items():
            if key.startswith("item-"):
                product_id = key.replace("item-", "", 1)
                try:
                    cantidad = int(value)
                    if cantidad > 0:
                        bundle_items[product_id] = cantidad
                except (ValueError, TypeError): continue
        if bundle_items:
            nuevo_paquete = {
                "nombre": request.form.get("nombre"), "descripcion": request.form.get("descripcion"),
                "imagen": imagen_nombre, "bundle_precio": float(request.form.get("bundle_precio", 0.0)),
                "bundle_items": bundle_items, "promocion": True
            }
            productos[paquete_id] = nuevo_paquete
            guardar_productos(productos)
            flash(f"Paquete '{nuevo_paquete['nombre']}' creado con éxito.", "success")
            return redirect(url_for("admin_view"))
        else:
            flash("Error: Un paquete debe contener al menos un producto.", "error")
    productos_simples = {pid: pdata for pid, pdata in productos.items() if "precio" in pdata}
    return render_template("add_bundle.html", productos_simples=productos_simples)

@app.route("/admin/toggle-promocion/<product_id>", methods=["POST"])
def admin_toggle_promocion(product_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    productos = cargar_productos()
    if product_id in productos:
        # Si la clave 'promocion' existe y es True, la quita. Si no, la pone a True.
        productos[product_id]["promocion"] = not productos[product_id].get("promocion", False)

    guardar_productos(productos)
    flash("Estado de promoción actualizado.", "success")
    return redirect(url_for("admin_view"))

# --- API PARA EMOJIS ---
EMOJI_LIST = ["😀", "🚀", "🌟", "🍕", "🤖", "👻", "👽", "👾", "🦊", "🧙", "🌮", "💎", "🌙", "🔮", "🧬", "🌵", "🎉", "🔥", "💯", "👑", "💡", "🎮", "🛰️", "🛸", "🗿", "🌴", "🧪", "✨", "🔑", "🗺️", "🐙", "🦋", "🐲", "🍩", "⚡", "🎯", "⚓", "🌈", "🌌", "🌠", "🎱", "🎰", "🕹️", "🏆", "💊", "🎁", "💌", "📈", "🗿"]
@app.route("/api/get-emojis")
def get_emojis():
    usuarios = cargar_usuarios()
    return jsonify({ "all_emojis": EMOJI_LIST, "occupied_emojis": list(usuarios.keys()) })

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
            stocks_posibles = [productos[item_id]["stock"] // cant_nec for item_id, cant_nec in prod_data["bundle_items"].items() if item_id in productos]
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

# --- ACCIÓN DE COMPRA ---
@app.route("/comprar")
def comprar():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    productos = cargar_productos()
    carrito = session.get('carrito', {})
    if not carrito: return redirect(url_for("index"))
    for cart_id, cant in carrito.items():
        prod_data = productos.get(cart_id)
        if prod_data and "bundle_items" in prod_data:
            for item_id, cant_nec in prod_data["bundle_items"].items():
                if productos.get(item_id, {}).get("stock", 0) < (cant_nec * cant):
                    flash(f"No hay suficiente stock para el paquete '{prod_data['nombre']}'.", "error")
                    return redirect(url_for("index"))
            for item_id, cant_nec in prod_data["bundle_items"].items():
                productos[item_id]["stock"] -= (cant_nec * cant)
        else:
            parts = cart_id.split('-', 1)
            base_id = parts[0]
            variation_id = parts[1] if len(parts) > 1 else None
            prod_data_var = productos.get(base_id)
            if not prod_data_var:
                flash(f"Producto '{base_id}' ya no existe.", "error")
                return redirect(url_for("index"))
            if variation_id and "variaciones" in prod_data_var:
                if prod_data_var["variaciones"][variation_id]["stock"] >= cant:
                    prod_data_var["variaciones"][variation_id]["stock"] -= cant
                else:
                    flash(f"No hay suficiente stock para {prod_data_var['nombre']} ({variation_id}).", "error")
                    return redirect(url_for("index"))
            elif not variation_id and "stock" in prod_data_var:
                if prod_data_var["stock"] >= cant:
                    prod_data_var["stock"] -= cant
                else:
                    flash(f"No hay suficiente stock para {prod_data_var['nombre']}.", "error")
                    return redirect(url_for("index"))
            else:
                flash(f"Producto '{base_id}' no encontrado o mal configurado.", "error")
                return redirect(url_for("index"))
    guardar_productos(productos)
    cart_data = _get_cart_data()
    total_general = cart_data["total"]
    libro_de_pedidos = cargar_pedidos()
    nuevo_id_pedido = generar_id_pedido()
    nuevo_pedido = {
        "id": nuevo_id_pedido, "timestamp": datetime.now().strftime("%d de %B, %Y a las %H:%M"),
        "detalle": carrito.copy(), "total": round(total_general, 2), "completado": False,
        "user_emoji": session.get("logged_in_user_emoji")
    }
    libro_de_pedidos.append(nuevo_pedido)
    guardar_pedidos(libro_de_pedidos)
    mensaje_partes = [f"*¡Que onda Corak! ocupo:* 🛍️\n\n*Pedido #{nuevo_id_pedido}*\nResumen:"]
    for cart_id, cant in carrito.items():
        nombre_item = cart_data["productos_detalle"].get(cart_id, {}).get("nombre", "Item")
        precio_total_item = cant * cart_data["productos_detalle"].get(cart_id, {}).get("precio", 0)
        mensaje_partes.append(f"• {cant}x {nombre_item} - *${precio_total_item:.2f}*")
    mensaje_partes.append(f"\n*TOTAL DEL PEDIDO: ${total_general:.2f}*")
    mensaje_final = "\n".join(mensaje_partes)
    mensaje_formateado = urllib.parse.quote(mensaje_final)
    whatsapp_url = f"https://wa.me/5215513361764?text={mensaje_formateado}"
    session.pop('carrito', None)
    return redirect(whatsapp_url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)