from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from whitenoise import WhiteNoise
from flask_socketio import SocketIO, emit, join_room, leave_room
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
# Configuración de SocketIO unificada y compatible
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    transports=['polling', 'websocket'],
    allow_upgrades=True,
    async_mode='threading'
)

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

# --- RUTAS DE ADMINISTRACIÓN ---
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
        estado_anterior = pedido_encontrado.get("completado", False)
        pedido_encontrado["completado"] = not estado_anterior
        user_emoji = pedido_encontrado.get("user_emoji")
        puntos_del_pedido = pedido_encontrado.get("puntos_ganados", 0)

        if user_emoji and user_emoji in usuarios:
            if pedido_encontrado["completado"] and not estado_anterior:
                usuarios[user_emoji]["aura_points"] = usuarios[user_emoji].get("aura_points", 0) + puntos_del_pedido
                flash(f"Pedido completado. Se sumaron {puntos_del_pedido} puntos de Aura a {user_emoji}.", "success")
            elif not pedido_encontrado["completado"] and estado_anterior:
                usuarios[user_emoji]["aura_points"] = usuarios[user_emoji].get("aura_points", 0) - puntos_del_pedido
                flash(f"Pedido desmarcado. Se restaron {puntos_del_pedido} puntos de Aura a {user_emoji}.", "success")
            guardar_usuarios(usuarios)
    guardar_pedidos(pedidos)
    return redirect(url_for("admin_view"))

@app.route("/admin/toggle-promocion/<product_id>", methods=["POST"])
def admin_toggle_promocion(product_id):
    if not session.get("logged_in"): return redirect(url_for("login"))
    productos = cargar_productos()
    if product_id in productos:
        productos[product_id]["promocion"] = not productos[product_id].get("promocion", False)
    guardar_productos(productos)
    flash("Estado de promoción actualizado.", "success")
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_nombre)
                file.save(file_path)
        nuevo_producto = {
            "nombre": request.form.get("nombre"), "descripcion": request.form.get("descripcion"),
            "imagen": imagen_nombre, "stock": int(request.form.get("stock", 0)),
            "precio": float(request.form.get("precio", 0.0)),
            "aura_multiplier": int(request.form.get("aura_multiplier", 1)),
            "orden": int(request.form.get("orden", 999))
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
            producto_a_editar["aura_multiplier"] = int(request.form.get("aura_multiplier", 1))
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                imagen_nombre = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_nombre)
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], producto_eliminado['imagen'])
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_nombre)
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
                "bundle_items": bundle_items, "promocion": True,
                "orden": int(request.form.get("orden", 999))
            }
            productos[paquete_id] = nuevo_paquete
            guardar_productos(productos)
            flash(f"Paquete '{nuevo_paquete['nombre']}' creado con éxito.", "success")
            return redirect(url_for("admin_view"))
        else:
            flash("Error: Un paquete debe contener al menos un producto.", "error")
    productos_simples = {pid: pdata for pid, pdata in productos.items() if "precio" in pdata}
    return render_template("add_bundle.html", productos_simples=productos_simples)

# --- LÓGICA DE LA ARENA Y SOCKETIO MEJORADA ---
@app.route("/lobby")
def lobby():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    return render_template("lobby_simple.html")

@app.route("/lobby-old")
def lobby_old():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    return render_template("lobby.html")

@app.route("/arena")
def arena():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    return render_template("arena_tactica.html")

@app.route("/arena-snake")
def arena_snake():
    if not session.get("logged_in_user_emoji"): return redirect(url_for("entrar"))
    return render_template("arena.html")

# Estado global del lobby - SIMPLIFICADO
lobby_state = {
    "spectators": {},      
    "searching": {},       
    "in_combat": {}        
}

active_games = {}

# Lógica del juego de táctica
def create_tactical_game(player1_id, player2_id):
    """Crear una nueva partida de táctica"""
    game = {
        "players": [player1_id, player2_id],
        "turn": player1_id,  # El primer jugador empieza
        "gameOver": False,
        "winner": None,
        "units": [],
        "selectedUnit": None
    }
    
    # Crear unidades iniciales para cada jugador
    # Jugador 1 (abajo)
    game["units"].extend([
        {"x": 1, "y": 4, "type": "soldier", "owner": player1_id, "hp": 3, "maxHp": 3},
        {"x": 2, "y": 4, "type": "archer", "owner": player1_id, "hp": 2, "maxHp": 2},
        {"x": 3, "y": 4, "type": "soldier", "owner": player1_id, "hp": 3, "maxHp": 3}
    ])
    
    # Jugador 2 (arriba)
    game["units"].extend([
        {"x": 1, "y": 0, "type": "soldier", "owner": player2_id, "hp": 3, "maxHp": 3},
        {"x": 2, "y": 0, "type": "archer", "owner": player2_id, "hp": 2, "maxHp": 2},
        {"x": 3, "y": 0, "type": "soldier", "owner": player2_id, "hp": 3, "maxHp": 3}
    ])
    
    return game

def get_user_data(user_emoji):
    """Obtiene los datos del usuario incluyendo puntos de aura"""
    usuarios = cargar_usuarios()
    user_data = usuarios.get(user_emoji, {})
    aura_points = user_data.get("aura_points", 0)
    return {"emoji": user_emoji, "aura_points": aura_points}

# FUNCIÓN DESHABILITADA - LOBBY SIMPLIFICADO
def broadcast_lobby_state():
    """DESHABILITADO - Lobby simplificado sin broadcasts"""
    pass

def try_match_players():
    """Intenta emparejar jugadores que están buscando duelo - VERSIÓN TÁCTICA"""
    if len(lobby_state["searching"]) >= 2:
        # Tomar los dos primeros jugadores
        players_list = list(lobby_state["searching"].items())
        player1_sid, player1_data = players_list[0]
        player2_sid, player2_data = players_list[1]
        
        # Crear sala de juego
        room_name = f"tactical-{player1_sid[:8]}-{player2_sid[:8]}"
        
        # Remover de búsqueda y agregar a combate
        del lobby_state["searching"][player1_sid]
        del lobby_state["searching"][player2_sid]
        
        lobby_state["in_combat"][room_name] = {
            "player1": player1_data,
            "player2": player2_data,
            "room_id": room_name
        }
        
        # Unir a la sala de Socket.IO
        join_room(room_name, sid=player1_sid)
        join_room(room_name, sid=player2_sid)
        
        # Crear juego táctico activo
        active_games[room_name] = create_tactical_game(player1_sid, player2_sid)
        
        # Notificar inicio del juego a los jugadores
        emit('init', {"playerId": player1_sid}, room=player1_sid)
        emit('init', {"playerId": player2_sid}, room=player2_sid)
        
        # Enviar estado inicial del juego
        emit('game_state', active_games[room_name], room=room_name)
        
        # Actualizar lobby para todos
        broadcast_lobby_state()
        
        print(f"[TACTICAL] Nueva partida: {player1_data['emoji']} vs {player2_data['emoji']}")
        return True
    return False

@socketio.on('connect')
def handle_connect():
    print(f"[CONNECT] Cliente conectado: {request.sid}")
    # Enviar inicialización al cliente
    emit('init', {'playerId': request.sid})

# HANDLERS DE LOBBY DESHABILITADOS
@socketio.on('join_lobby')
def handle_join_lobby(data):
    """DESHABILITADO - Lobby simplificado"""
    print(f"[JOIN] Lobby join request ignored - using simple lobby")

@socketio.on('search_for_game')
def handle_search_for_game():
    """DESHABILITADO - Lobby simplificado"""
    print(f"[SEARCH] Search request ignored - using simple lobby")

@socketio.on('cancel_search')
def handle_cancel_search():
    """DESHABILITADO - Lobby simplificado"""
    print(f"[CANCEL] Cancel request ignored - using simple lobby")

@socketio.on('ping')
def handle_ping():
    """Heartbeat para mantener conexión activa"""
    emit('pong')

@socketio.on('select_cell')
def handle_select_cell(data):
    """Manejar selección de celda en el juego de táctica"""
    player_sid = request.sid
    x = data.get('x')
    y = data.get('y')
    
    # Encontrar la partida del jugador
    current_room = None
    for room, game_data in active_games.items():
        if player_sid in game_data["players"]:
            current_room = room
            break
    
    if not current_room:
        emit('invalid_move', {'reason': 'No estás en una partida'})
        return
        
    game = active_games[current_room]
    
    if game["gameOver"]:
        emit('invalid_move', {'reason': 'El juego ha terminado'})
        return
    
    if game["turn"] != player_sid:
        emit('invalid_move', {'reason': 'No es tu turno'})
        return
    
    # Verificar si hay una unidad seleccionada
    if game["selectedUnit"] is None:
        # Intentar seleccionar unidad
        selected_unit = None
        for unit in game["units"]:
            if unit["x"] == x and unit["y"] == y and unit["owner"] == player_sid:
                selected_unit = unit
                break
        
        if selected_unit:
            game["selectedUnit"] = selected_unit
            emit('unit_selected', {'unit': selected_unit}, room=current_room)
            print(f"[TACTICAL] Unidad seleccionada: {selected_unit}")
        else:
            emit('invalid_move', {'reason': 'No hay unidad tuya en esa posición'})
    else:
        # Intentar mover la unidad seleccionada
        move_unit(current_room, game["selectedUnit"], x, y)

def move_unit(room_name, unit, target_x, target_y):
    """Mover una unidad en el juego de táctica"""
    game = active_games[room_name]
    
    # Verificar si el movimiento es válido
    if not is_valid_move(unit, target_x, target_y, game):
        emit('invalid_move', {'reason': 'Movimiento inválido'})
        return
    
    # Verificar si hay una unidad enemiga en la posición objetivo
    target_unit = None
    for u in game["units"]:
        if u["x"] == target_x and u["y"] == target_y:
            target_unit = u
            break
    
    if target_unit and target_unit["owner"] != unit["owner"]:
        # Combate!
        damage = 1
        if unit["type"] == "archer":
            damage = 2
        
        target_unit["hp"] -= damage
        print(f"[TACTICAL] {unit['type']} ataca a {target_unit['type']} por {damage} daño")
        
        if target_unit["hp"] <= 0:
            # Eliminar unidad muerta
            game["units"].remove(target_unit)
            print(f"[TACTICAL] {target_unit['type']} eliminado")
    
    # Mover la unidad
    unit["x"] = target_x
    unit["y"] = target_y
    
    # Limpiar selección
    game["selectedUnit"] = None
    
    # Cambiar turno
    current_player_index = game["players"].index(game["turn"])
    next_player_index = (current_player_index + 1) % len(game["players"])
    game["turn"] = game["players"][next_player_index]
    
    # Verificar condición de victoria
    check_victory(room_name)
    
    # Enviar estado actualizado
    emit('game_state', game, room=room_name)
    
def is_valid_move(unit, target_x, target_y, game):
    """Verificar si un movimiento es válido"""
    # Verificar límites del tablero
    if target_x < 0 or target_x >= 5 or target_y < 0 or target_y >= 5:
        return False
    
    # Verificar que no se mueva a la misma posición
    if unit["x"] == target_x and unit["y"] == target_y:
        return False
    
    # Verificar que el movimiento sea adyacente (solo una casilla)
    dx = abs(unit["x"] - target_x)
    dy = abs(unit["y"] - target_y)
    
    if dx + dy != 1:  # Movimiento Manhattan de 1
        return False
    
    # Verificar que no haya unidad aliada en la posición objetivo
    for u in game["units"]:
        if u["x"] == target_x and u["y"] == target_y and u["owner"] == unit["owner"]:
            return False
    
    return True

def check_victory(room_name):
    """Verificar condiciones de victoria"""
    game = active_games[room_name]
    
    # Contar unidades de cada jugador
    player_units = {}
    for unit in game["units"]:
        if unit["owner"] not in player_units:
            player_units[unit["owner"]] = 0
        player_units[unit["owner"]] += 1
    
    # Verificar si algún jugador perdió todas sus unidades
    for player in game["players"]:
        if player not in player_units or player_units[player] == 0:
            # Este jugador perdió
            winner = game["players"][1] if game["players"][0] == player else game["players"][0]
            game["gameOver"] = True
            game["winner"] = winner
            
            emit('game_over', {'winner': winner}, room=room_name)
            print(f"[TACTICAL] Juego terminado. Ganador: {winner}")
            break

def update_game(room_name):
    """Función heredada del Snake - Ya no se usa en juego de táctica"""
    # El juego de táctica se maneja por eventos, no por updates constantes
    pass

# GAME LOOP DESHABILITADO - LOBBY SIMPLIFICADO
# El juego se maneja por eventos, no por loop constante
import threading
import time

def game_loop():
    """DESHABILITADO - Consume muchos recursos"""
    pass  # Loop deshabilitado para mejorar rendimiento

# Game thread deshabilitado
# game_thread = threading.Thread(target=game_loop, daemon=True)
# game_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    """Usuario se desconecta - SIMPLIFICADO"""
    player_sid = request.sid
    
    # Solo limpiar juegos activos si es necesario
    for room_name in list(active_games.keys()):
        if player_sid in active_games[room_name].get("players", {}):
            emit('player_disconnected', room=room_name)
            del active_games[room_name]
            print(f"[DISCONNECT] Juego {room_name} terminado por desconexión")
            break
    
    print(f"[DISCONNECT] Cliente {player_sid} se desconectó")

def handle_game_over(room_name, winner_data=None):
    """Maneja el final de un juego y devuelve jugadores al lobby"""
    if room_name in lobby_state["in_combat"]:
        combat_data = lobby_state["in_combat"][room_name]
        
        # Agregar jugadores de vuelta como espectadores
        for player_key in ["player1", "player2"]:
            if player_key in combat_data:
                player_data = combat_data[player_key]
                # Buscar el session_id del jugador
                for sid, game_players in active_games.get(room_name, {}).get("players", {}).items():
                    if game_players.get("emoji") == player_data["emoji"]:
                        lobby_state["spectators"][sid] = player_data
                        break
        
        # Remover de combate
        del lobby_state["in_combat"][room_name]
        
        # Actualizar lobby
        broadcast_lobby_state()
        
        print(f"[GAME_END] Juego {room_name} terminado, jugadores devueltos al lobby")

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
    
    # Este bloque busca información detallada de los productos
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


# --- ACCIÓN DE COMPRA ---
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
        puntos_aura_ganados += (precio_item * multiplier) * cant

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
    print("Iniciando servidor...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    
    