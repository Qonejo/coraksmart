#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script optimizado para iniciar el servidor con Gevent
"""
import os
import sys

def start_server():
    """Inicia el servidor con configuración optimizada para Gevent"""
    
    # Configurar el entorno para Gevent
    os.environ['GEVENT_SUPPORT'] = 'True'
    
    # Importar la aplicación
    try:
        from app import app, socketio
        print("[OK] Aplicacion cargada correctamente")
        print("[CONFIG] Configuracion del servidor:")
        print("   - Motor: Gevent (async)")
        print("   - Puerto: 5000")
        print("   - Host: 0.0.0.0")
        print("   - Debug: True")
        print("   - SocketIO: Habilitado")
        print("\n[START] Iniciando servidor...")
        
        # Iniciar servidor con Gevent
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            use_reloader=False  # Desactivar reloader para mejor rendimiento con Gevent
        )
        
    except ImportError as e:
        print(f"[ERROR] Error al importar la aplicacion: {e}")
        print("[INFO] Instala las dependencias con: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
