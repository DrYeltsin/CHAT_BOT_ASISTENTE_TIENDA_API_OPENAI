# CHAT_BOT_ASISTENTE_TIENDA_API_OPENAI

# 🤖 KRATOS — Asistente Virtual de Catálogo (Streamlit + OpenAI + WebRTC)

KRATOS es un asistente virtual diseñado para responder preguntas sobre un catálogo de productos almacenado en una base de datos SQLite.
Permite consultas por texto y por voz (micrófono), usando inteligencia artificial para generar SQL, consultar la base de datos y dar respuestas claras al usuario.

Desarrollado por: **Dr. Yeltsin**
Tecnologías: **Streamlit, OpenAI GPT-4 Turbo, Whisper-1, WebRTC, SQLite**

---

## 🚀 Características principales

### ✔️ Chatbot inteligente

* Procesa lenguaje natural.
* Genera consultas SQL dinámicas usando GPT-4.
* Solo responde preguntas relacionadas al catálogo.
* Entrega respuestas amables, claras y con formato profesional.

### ✔️ Base de datos automática (500 productos)

* Productos ficticios, realistas y variados.
* Familias: Electrónica, Hogar, Oficina, Deportes y Accesorios.
* Precios en Soles (S/).
* Estado de disponibilidad.

### ✔️ Búsquedas avanzadas

KRATOS entiende:

* “Muéstrame el producto más caro”
* “Cinco productos baratos”
* “Un ejemplo de electrónica”
* “Zapatillas deportivas”
* “Dame laptops”, etc.

### ✔️ Entrada por voz (Speech-to-Text)

* Captura audio del micrófono usando **streamlit-webrtc**.
* Transcribe voz utilizando **Whisper-1**.
* Responde automáticamente según tu consulta hablada.

### ✔️ Sin errores en Streamlit Cloud

Usa **openai==0.28.1** (cliente legacy estable), que evita los errores de proxies del SDK nuevo.

---

## 🧩 Arquitectura

```
Streamlit UI 
 ├── Chat (st.chat_input)
 ├── WebRTC (micrófono)
 │     └── Audio → WAV → Whisper-1
 ├── Botón: Crear base de datos (SQLite)
 └── Render del historial
           
IA / Lógica
 ├── GPT-4 Turbo → Generación de SQL
 ├── Whisper-1 → Transcripción de voz
 └── GPT-4 Turbo → Respuestas del asistente (KRATOS)

Backend
 ├── SQLite (productos_soles.db)
 ├── db_utils.py
 ├── ai_utils.py
 └── webrtc_utils.py
```

---

## 📁 Estructura del proyecto

```
chat_bot_asistente_tienda_api_openai/
│
├── app.py
├── ai_utils.py
├── db_utils.py
├── webrtc_utils.py
├── requirements.txt
├── runtime.txt
└── README.md
```

---

## 🔧 Instalación local

### 1️⃣ Crear el entorno

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Configurar tu API Key

En macOS/Linux:

```bash
export OPENAI_API_KEY="TU_API_KEY_AQUI"
```

En Windows:

```powershell
setx OPENAI_API_KEY "TU_API_KEY_AQUI"
```

### 4️⃣ Ejecutar KRATOS

```bash
streamlit run app.py
```

---

## ☁️ Despliegue en Streamlit Cloud

1. Sube los archivos a GitHub.
2. Ve a: [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Selecciona **New App**
4. Apunta al repositorio y rama
5. En “Advanced Settings” agrega:

**Secrets:**

```
OPENAI_API_KEY="TU_API_KEY_AQUI"
```

6. Crear la aplicación.

### Importante

El archivo `runtime.txt` debe contener:

```
python-3.10
```

Esto garantiza compatibilidad con WebRTC + PyDub + AV.

---

## 🎙️ ¿Cómo funciona el modo por voz?

1. KRATOS activa WebRTC.
2. Captura audio del micrófono en frames.
3. Convierte los frames a formato WAV.
4. Envía el audio a **Whisper-1**.
5. Whisper devuelve la transcripción.
6. GPT-4 Turbo analiza la consulta.
7. KRATOS responde naturalmente.

---

## 🛠 Tecnologías utilizadas

* **Python 3.10**
* **Streamlit 1.39**
* **OpenAI (Legacy SDK 0.28.1)**
* **GPT-4 Turbo (gpt-4-1106-preview)**
* **Whisper-1**
* **streamlit-webrtc**
* **SQLite**
* **Faker**
* **NumPy**
* **PyDub**
* **AV**

---

## 📦 Generación de la base de datos

KRATOS permite crear automáticamente la base de datos con:

```sql
500 productos simulados en soles (S/)
```

Simplemente usa el botón:

```
📦 Crear Base de Datos (500 productos)
```

---

## 🛡 Limitaciones del asistente

KRATOS:

* **solo responde sobre el catálogo**
* no inventa datos externos
* solo usa la información de la base de datos
* no responde preguntas fuera del contexto

---

## 📌 Autor

Proyecto desarrollado por:

### **Dr. Yeltsin**

Desarrollador & Arquitecto IA
Perú 🇵🇪

---

## 📄 Licencia

MIT License — libre para uso académico, comercial y personal.

---

## ⭐ ¿Deseas agregar más funciones?

Puedo ayudarte a integrar:

* 🔊 Text-to-Speech (KRATOS habla)
* 🖼 Generación de imágenes (OpenAI / DALL-E)
* 📊 Dashboard PowerBI-style dentro de Streamlit
* 💬 Chat con memoria larga
* 🛒 Un módulo de carrito de compras en KRATOS
* 🏪 API REST para tu tienda

Solo dímelo.

---

# 🎉 ¡KRATOS está listo para producción!

---
