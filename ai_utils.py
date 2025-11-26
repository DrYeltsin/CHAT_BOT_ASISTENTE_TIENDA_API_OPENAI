import json
import sqlite3
from openai import OpenAI

client = None  # Se inicializa en app.py


def generate_sql(user_query):
    prompt = f"""
Convierte esta consulta del usuario en SQL para SQLite.

Reglas:
- SOLO SQL, sin explicaciones.
- LIMIT máximo = 5.
- Si piden "más caro": ORDER BY prod_price DESC LIMIT 1.
- Si piden "baratos": ORDER BY prod_price ASC LIMIT 5.
- Si piden "ejemplo": ORDER BY RANDOM() LIMIT 1.
- Solo productos con status = 1.
- Si piden por categoría/familia: WHERE prod_family LIKE '%texto%' LIMIT 5.

Consulta: {user_query}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message["content"].strip()


def run_sql_query(sql_query):
    conn = sqlite3.connect("productos_soles.db")
    cur = conn.cursor()

    results = []
    queries = [q.strip() for q in sql_query.split(";") if q.strip()]

    for q in queries:
        if not q.lower().startswith("select"):
            continue
        try:
            cur.execute(q)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            results.extend([dict(zip(cols, r)) for r in rows])
        except:
            continue

    conn.close()
    return results


def generate_chatbot_response(user_query, product_data):
    system_msg = """
Eres un asistente de ventas amable.
Si hay productos, descríbelos con precio en Soles (S/).
Si no hay productos, di que solo puedes ayudar con el catálogo.
"""

    if product_data:
        data = json.dumps(product_data, indent=2)
        prompt = f"El usuario preguntó: {user_query}\nProductos encontrados:\n{data}\nCrea una respuesta clara y amable."
    else:
        prompt = f"El usuario preguntó: {user_query}\nNo hay productos."

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message["content"]
