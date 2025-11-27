import json
import sqlite3
import openai

SYSTEM_MESSAGE = """
Eres KRATOS, un asistente virtual especializado en responder únicamente preguntas
sobre el catálogo de productos.

Reglas:
- Solo puedes responder sobre el catálogo.
- Usa únicamente los datos entregados por la base de datos.
- Si la pregunta no es del catálogo, responde:
  "Puedo ayudarte únicamente con consultas sobre nuestro catálogo de productos."
- Tono amable, profesional y claro.
- Moneda: Sol Peruano (S/).
- Si retornas 5 productos, di que es una muestra limitada.
"""

# ---------------------------------------------
# SQL generation
# ---------------------------------------------
def generate_sql(user_query):
    prompt = f"""
Convierte esta consulta del usuario en SQL válido para SQLite.

Reglas:
- SOLO devuelve SQL puro.
- Máximo LIMIT 5.
- "más caro" → ORDER BY prod_price DESC LIMIT 1
- "más barato" → ORDER BY prod_price ASC LIMIT 5
- "ejemplo" → ORDER BY RANDOM() LIMIT 1
- Solo productos con status = 1.
- Categoría/familia: WHERE prod_family LIKE '%texto%' LIMIT 5

Consulta del usuario: {user_query}
"""

    resp = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = resp["choices"][0]["message"]["content"].strip()
    if not sql.lower().startswith("select"):
        sql = "SELECT * FROM tbl_product WHERE status = 1 LIMIT 5"

    return sql

# ---------------------------------------------
# SQL execution
# ---------------------------------------------
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

# ---------------------------------------------
# Chat response
# ---------------------------------------------
def generate_chatbot_response(user_query, product_data, first_message=False):
    if first_message:
        intro = (
            "Hola, soy **KRATOS**, tu asistente virtual.\n"
            "Fui desarrollado por el Dr. Yeltsin.\n"
            "Estoy aquí para ayudarte solo con consultas del catálogo.\n\n"
        )
    else:
        intro = ""

    if product_data:
        pjson = json.dumps(product_data, indent=2)
        user_prompt = (
            f"{intro}El usuario preguntó: {user_query}\n"
            f"Productos encontrados:\n{pjson}\n\n"
            "Genera una respuesta clara usando solo esta información."
        )
    else:
        user_prompt = (
            f"{intro}El usuario preguntó: {user_query}\n"
            "No se encontraron productos.\n"
            "Recuerda que solo puedes responder sobre el catálogo."
        )

    resp = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt}
        ]
    )

    return resp["choices"][0]["message"]["content"]
