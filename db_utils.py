import sqlite3
import random
from faker import Faker

fake = Faker("es_ES")
DB_NAME = "productos_soles.db"
NUM_PRODUCTS = 500

def generate_random_product(product_id):
    families = ['Electrónica', 'Hogar', 'Oficina', 'Deportes', 'Accesorios']
    family = random.choice(families)

    if family == 'Electrónica':
        prod_name = f"{random.choice(['Smart TV', 'Laptop', 'Auriculares'])} {fake.bs()}"
        prod_desc = f"Un {prod_name} con {random.randint(4, 16)}GB de RAM."
    elif family == 'Hogar':
        prod_name = f"Robot Aspirador {fake.word().capitalize()}"
        prod_desc = "Aspiradora inteligente con mapeo."
    elif family == 'Oficina':
        prod_name = f"Silla Ergonómica {fake.word().capitalize()}"
        prod_desc = "Silla con soporte lumbar ajustable."
    else:
        prod_name = f"Zapatillas {fake.color_name()} {fake.word()}"
        prod_desc = f"Calzado talla {random.randint(35, 45)}."

    cost = round(random.uniform(50, 5000), 2)
    price = round(cost * random.uniform(1.2, 2.5), 2)
    status = random.choice([True, True, True, False])

    return (
        f"PROD{product_id:04d}",
        fake.user_name(),
        prod_name,
        prod_desc,
        fake.url(),
        "PEN",
        cost,
        price,
        None,
        family,
        fake.word(),
        random.choice(["Unidad", "Caja"]),
        fake.md5(),
        random.randint(5, 50),
        status,
    )

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS tbl_product")

    cur.execute("""
        CREATE TABLE tbl_product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prod_id TEXT,
            account_id TEXT,
            prod_name TEXT,
            prod_desc TEXT,
            prod_photo TEXT,
            prod_currency TEXT,
            prod_cost REAL,
            prod_price REAL,
            prod_suggested_prod_id TEXT,
            prod_family TEXT,
            prod_subfamily TEXT,
            prod_uom TEXT,
            prod_qr_code TEXT,
            prod_min_stock INTEGER,
            status BOOLEAN
        )
    """)

    products = [generate_random_product(i+1) for i in range(NUM_PRODUCTS)]

    cur.executemany("""
        INSERT INTO tbl_product (
            prod_id, account_id, prod_name, prod_desc, prod_photo, prod_currency,
            prod_cost, prod_price, prod_suggested_prod_id, prod_family,
            prod_subfamily, prod_uom, prod_qr_code, prod_min_stock, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)

    conn.commit()
    conn.close()
