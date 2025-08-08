import os
import json
import sys
from app import app, db, Product, User, Order, Config, AuraLevel, Emoji

def migrate():
    """
    Reads data from old JSON files and migrates it to the new PostgreSQL database.
    This script is designed to be run once. It's idempotent; it won't
    re-migrate data if the tables are already populated.
    """
    with app.app_context():
        print("Starting database migration...")
        db.create_all()
        print("Database tables ensured.")

        # --- Migrate Config ---
        if Config.query.count() == 0:
            print("Migrating config.json...")
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        db.session.add(Config(key=key, value=str(value)))
                    print(f"  -> Found and staged {len(data)} config items.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError):
                print("  -> config.json not found or invalid, skipping.")
                db.session.rollback()
        else:
            print("Config table already populated, skipping.")

        # --- Migrate Aura Levels ---
        if AuraLevel.query.count() == 0:
            print("Migrating aura_levels.json...")
            try:
                with open('aura_levels.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        points = item.get('points_needed')
                        if points == "negative_infinity":
                            points = -float('inf')

                        level = AuraLevel(
                            level=item.get('level'),
                            points_needed=points,
                            flame_color=item.get('flame_color'),
                            name=item.get('name'),
                            prize=item.get('prize'),
                            character_size=item.get('character_size')
                        )
                        db.session.add(level)
                    print(f"  -> Found and staged {len(data)} aura levels.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  -> aura_levels.json not found or invalid, skipping. Error: {e}")
                db.session.rollback()
        else:
            print("AuraLevel table already populated, skipping.")

        # --- Migrate Emojis ---
        if Emoji.query.count() == 0:
            print("Migrating emoji_config.json...")
            try:
                with open('emoji_config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    emojis_raw = data.get('available_emojis', [])
                    # De-duplicate the list of emojis
                    emojis_unique = sorted(list(set(emojis_raw)))

                    for e in emojis_unique:
                        db.session.add(Emoji(emoji=e))
                    print(f"  -> Found {len(emojis_raw)} emojis, adding {len(emojis_unique)} unique emojis.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  -> emoji_config.json not found or invalid, skipping. Error: {e}")
                db.session.rollback()
        else:
            print("Emoji table already populated, skipping.")

        # --- Migrate Users ---
        if User.query.count() == 0:
            print("Migrating usuarios.json...")
            try:
                with open('usuarios.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for emoji, user_data in data.items():
                        user = User(
                            emoji=emoji,
                            password_hash=user_data.get('password_hash'),
                            aura_points=user_data.get('aura_points', 0),
                            claimed_levels=user_data.get('claimed_levels', []),
                            reward_codes=user_data.get('reward_codes', {})
                        )
                        db.session.add(user)
                    print(f"  -> Found and staged {len(data)} users.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  -> usuarios.json not found or invalid, skipping. Error: {e}")
                db.session.rollback()
        else:
            print("User table already populated, skipping.")

        # --- Migrate Products ---
        if Product.query.count() == 0:
            print("Migrating productos.json...")
            try:
                with open('productos.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for prod_id, prod_data in data.items():
                        product = Product(
                            id=prod_id,
                            nombre=prod_data.get('nombre'),
                            descripcion=prod_data.get('descripcion'),
                            precio=prod_data.get('precio'),
                            stock=prod_data.get('stock'),
                            imagen=prod_data.get('imagen'),
                            whatsapp_asignado=prod_data.get('whatsapp_asignado', '1'),
                            orden=prod_data.get('orden', 999),
                            promocion=prod_data.get('promocion', False),
                            variaciones=prod_data.get('variaciones'),
                            bundle_items=prod_data.get('bundle_items'),
                            bundle_precio=prod_data.get('bundle_precio'),
                            imagenes_adicionales=prod_data.get('imagenes_adicionales')
                        )
                        db.session.add(product)
                    print(f"  -> Found and staged {len(data)} products.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  -> productos.json not found or invalid, skipping. Error: {e}")
                db.session.rollback()
        else:
            print("Product table already populated, skipping.")

        # --- Migrate Orders ---
        if Order.query.count() == 0:
            print("Migrating pedidos.json...")
            try:
                with open('pedidos.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    orders_added = 0
                    for order_data in data:
                        user_exists = User.query.get(order_data.get("user_emoji"))
                        if not user_exists:
                            print(f"  -> Skipping order {order_data.get('id')} because user {order_data.get('user_emoji')} does not exist.")
                            continue

                        order = Order(
                            id=order_data.get('id'),
                            user_emoji=order_data.get('user_emoji'),
                            timestamp=order_data.get('timestamp'),
                            detalle=order_data.get('detalle'),
                            detalle_completo=order_data.get('detalle_completo'),
                            total=order_data.get('total'),
                            aura_ganada=order_data.get('aura_ganada'),
                            aura_potencial=order_data.get('aura_potencial'),
                            aura_otorgada=order_data.get('aura_otorgada'),
                            delivery_info=order_data.get('delivery_info'),
                            completado=order_data.get('completado', False),
                            whatsapp_usado=order_data.get('whatsapp_usado')
                        )
                        db.session.add(order)
                        orders_added += 1
                    print(f"  -> Found and staged {orders_added} orders.")
                    db.session.commit()
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  -> pedidos.json not found or invalid, skipping. Error: {e}")
                db.session.rollback()
        else:
            print("Order table already populated, skipping.")

        print("Migration complete. Database is now populated.")

if __name__ == '__main__':
    migrate()
