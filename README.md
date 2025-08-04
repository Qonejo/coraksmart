# CorakSmart - Sistema de Tienda y Arena PvP

Sistema web completo con tienda de productos, gestión de pedidos, sistema de puntos de aura y arena PvP táctica.

## 🚀 Características

### 🛒 **Sistema de Tienda**
- Catálogo de productos con imágenes
- Carrito de compras interactivo
- Sistema de pedidos con WhatsApp
- Gestión de stock en tiempo real
- Productos con variaciones y paquetes

### 👑 **Sistema de Aura (Puntos)**
- 7 niveles de rango con recompensas
- Multiplicadores por producto
- Sistema de logros y premios
- Interfaz con llamas de colores

### ⚔️ **Arena PvP Táctica**
- Juego por turnos estratégico
- Sistema de unidades (soldados, arqueros)
- Sprites y gráficos retro
- Matchmaking automático
- Recompensas por victoria

### 🔧 **Panel de Administración**
- Gestión completa de productos
- Control de pedidos y estados
- Estadísticas de usuarios
- Configuración de promociones

## 📋 Requisitos

- Python 3.7+
- Flask
- Flask-SocketIO
- WhiteNoise
- Werkzeug

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/coraksmart.git
cd coraksmart
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar archivos de datos** (si es la primera vez)
```bash
# Los archivos JSON se crearán automáticamente al iniciar
# O puedes crear versiones vacías:
echo "{}" > productos.json
echo "[]" > pedidos.json
echo "{}" > usuarios.json
```

5. **Iniciar el servidor**
```bash
python app.py
# O usar el script de inicio:
python start_server.py
```

## 🎮 Uso

### **Acceso de Usuario**
1. Ve a `http://localhost:5000/entrar`
2. Selecciona tu emoji de usuario
3. Explora productos y añade al carrito
4. Ve al perfil para ver tu progreso de aura
5. Accede a la arena PvP desde el lobby

### **Acceso de Administrador**
1. Ve a `http://localhost:5000/login`
2. Ingresa la contraseña de administrador
3. Gestiona productos, pedidos y usuarios

## 📁 Estructura del Proyecto

```
coraksmart/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── start_server.py       # Script de inicio
├── start.bat            # Script Windows
├── templates/           # Plantillas HTML
│   ├── index.html       # Tienda principal
│   ├── arena_tactica.html # Arena PvP
│   ├── lobby_simple.html  # Lobby de juegos
│   ├── admin.html       # Panel admin
│   └── ...
├── static/              # Archivos estáticos
│   ├── sprites/         # Sprites del juego
│   ├── style.css        # Estilos principales
│   ├── script_fast.js   # JavaScript arena
│   └── *.png           # Imágenes productos
├── productos.json       # Base de datos productos
├── pedidos.json        # Base de datos pedidos
└── usuarios.json       # Base de datos usuarios
```

## 🎯 Arena PvP Táctica

### **Mecánicas de Juego**
- **Tablero**: Grid 5x5
- **Unidades**: Soldados (3 HP) y Arqueros (2 HP)
- **Turnos**: Alternados entre jugadores
- **Victoria**: Eliminar todas las unidades enemigas
- **Recompensas**: +200 puntos por enemigo eliminado

### **Controles**
- Click en unidad propia para seleccionar
- Click en casilla adyacente para mover
- Click en enemigo adyacente para atacar
- El juego indica de quién es el turno

## 🔧 Configuración

### **Variables de Entorno**
```python
# En app.py puedes modificar:
ADMIN_PASSWORD = "tu_contraseña_aqui"
PEDIDOS_FILE = "pedidos.json"
PRODUCTOS_FILE = "productos.json"
USUARIOS_FILE = "usuarios.json"
```

### **Niveles de Aura**
Los niveles se configuran en `AURA_LEVELS` en app.py:
- Nivel 1: 0 puntos (Llama Blanca)
- Nivel 2: 8,000 puntos (Llama Azul)
- Nivel 3: 20,000 puntos (Llama Verde)
- ... hasta Nivel 7: 500,000 puntos (Llama Púrpura)

## 🚀 Despliegue

### **Render (Recomendado)**
1. **Conecta tu repositorio en render.com**
2. **Configuración automática**: 
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --config gunicorn.conf.py app:app`
3. **Variables de entorno**:
   - `FLASK_ENV`: `production`
   - `WEB_CONCURRENCY`: `1` (importante para Socket.IO)

### **Heroku**
```bash
# Instalar Heroku CLI y luego:
heroku create tu-app-name
heroku config:set FLASK_ENV=production
heroku config:set WEB_CONCURRENCY=1
git push heroku main
```

### **Railway**
- Conecta tu repositorio
- Variables de entorno: `FLASK_ENV=production`, `WEB_CONCURRENCY=1`
- Comando de inicio automático desde `Procfile`

### **Configuración importante para producción:**
- ✅ **Solo 1 worker** (Socket.IO no funciona con múltiples workers)
- ✅ **Eventlet** como motor asíncrono
- ✅ **Timeouts aumentados** para WebSockets
- ✅ **Manejo de errores** mejorado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🐛 Problemas Conocidos

- Los sprites requieren conexión a internet para cargar
- El sistema de WhatsApp requiere configuración del número
- Los archivos JSON deben tener permisos de escritura

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la sección de Issues en GitHub
2. Crea un nuevo Issue con detalles del problema
3. Incluye logs de error si los hay

---

**Desarrollado con ❤️ usando Flask y Socket.IO**
