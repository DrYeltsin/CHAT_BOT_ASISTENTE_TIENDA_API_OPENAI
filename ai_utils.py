import json
import sqlite3


SYSTEM_MESSAGE = """
Eres KRATOS, un asistente virtual especializado exclusivamente en responder preguntas 
sobre el catálogo de productos almacenado en la base de datos.

Reglas:
- SOLO puedes responder preguntas relacionadas al catálogo.
- La única información válida proviene de products_data.
- Si el usuario pregunta algo fuera del catálogo, responde:
  "Puedo ayudarte únicamente con consultas sobre nuestro catálogo de productos."
- Mantén un tono amable, profesional y claro.
- La moneda es el Sol Peruano (S/).
- Si se devuelven 5 productos, menciona que es una muestra limitada.
- No inventes información externa.
"""


# ---------------------------
# GENERAR SQL
# ---------------------------

def generate_sql(client, user_query):
    prompt = f"""
Convierte esta consulta del usuario en SQL válido para SQLite.

Reglas:
- SOLO devolver SQL.
- Máximo LIMIT 5.
- "más caro" → ORDER BY prod_price DESC LIMIT 1
- "más baratos" → ORDER BY prod_price ASC LIMIT 5
- "ejemplo" → ORDER BY RANDOM() LIMIT 1
- Solo productos con status = 1.
- Categorías → WHERE prod_family LIKE '%texto%' LIMIT 5

Consulta del usuario: {user_query}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message["content"].strip()


# ---------------------------
# EJECUTAR SQL
# ---------------------------

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


# ---------------------------
# GENERAR RESPUESTA PARA KRATOS
# ---------------------------

def generate_chatbot_response(client, user_query, product_data, first_message=False):

    if first_message:
        intro = (
            "Hola, soy **KRATOS**, tu asistente virtual del catálogo.\n"
            "Fui desarrollado por el **Dr. Yeltsin**.\n"
            "Estoy aquí para ayudarte únicamente con consultas sobre nuestros productos.\n\n"
        )
    else:
        intro = ""

    if product_data:
        data_json = json.dumps(product_data, indent=2)
        user_prompt = (
            f"{intro}"
            f"El usuario consultó: {user_query}\n"
            f"Productos encontrados:\n{data_json}\n\n"
            "Crea una respuesta clara usando solo estos datos."
        )
    else:
        user_prompt = (
            f"{intro}"
            f"El usuario consultó: {user_query}\n"
            "No se encontraron productos.\n"
            "Recuerda que solo puedes responder sobre el catálogo."
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message["content"]
