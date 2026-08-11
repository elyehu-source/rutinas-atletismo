import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
import datetime
import requests

# HIBRIDACIÓN DE BASE DE DATOS (Local JSON / Google Sheets)
# Deja "URL_DE_TU_WEB_APP" para usar el archivo local "atletas.json" por defecto.
# Cuando tengas tu URL de Google Apps Script Web App, pégala aquí.
GSHEET_API_URL = "https://script.google.com/macros/s/AKfycbziF5BBITSs1WhbKOf5njDRGC-eeOze_ay_ZlIluVmlLjThK4K6W3QHWLc_7DSsSFCT/exec"

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Generador 0 a 5K - Atletismo Salud",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Sporty Theme (Dark Mode optimized)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply font family globally */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom headers and text styling */
    .title-text {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00E5FF 0%, #C0FF00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }
    
    .caption-text {
        font-size: 1.15rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }

    /* Premium Custom Metric Card */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: 0 8px 30px rgba(0, 229, 255, 0.15);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00E5FF, #C0FF00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94A3B8;
        font-weight: 600;
    }

    /* Calendar Day Layout styling */
    .calendar-container {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        margin-top: 1rem;
    }
    
    .day-card {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #00E5FF;
        border-radius: 8px;
        padding: 1rem;
        transition: transform 0.2s ease;
        border-top: 1px solid rgba(255,255,255,0.03);
        border-right: 1px solid rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.03);
        min-height: 140px;
    }
    .day-card:hover {
        transform: translateX(4px);
        background: rgba(30, 41, 59, 0.6);
    }
    
    .day-card-special {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #C0FF00;
        border-radius: 8px;
        padding: 1rem;
        transition: transform 0.2s ease;
        border-top: 1px solid rgba(255,255,255,0.03);
        border-right: 1px solid rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.03);
        min-height: 140px;
    }
    .day-card-special:hover {
        transform: translateX(4px);
        background: rgba(30, 41, 59, 0.6);
    }

    .day-card-rest {
        background: rgba(15, 23, 42, 0.2);
        border-left: 4px solid #64748B;
        border-radius: 8px;
        padding: 1rem;
        opacity: 0.85;
        min-height: 140px;
    }

    .day-name {
        font-weight: 700;
        font-size: 0.95rem;
        color: #F8FAFC;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .day-type {
        font-size: 0.8rem;
        font-weight: 600;
        color: #00E5FF;
        margin-bottom: 0.3rem;
    }
    .day-type-special {
        font-size: 0.8rem;
        font-weight: 600;
        color: #C0FF00;
        margin-bottom: 0.3rem;
    }
    .day-type-rest {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 0.3rem;
    }

    .day-description {
        font-size: 0.85rem;
        color: #CBD5E1;
        line-height: 1.4;
    }

    /* Section Cards styling */
    .section-card {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Adjust sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display banner if it exists
if os.path.exists("runner_banner.jpg"):
    st.image("runner_banner.jpg", width='stretch')

# Main Title and Subtitle
st.markdown('<div class="title-text">🏃‍♂️ Generador de Planes de Atletismo: 0 a 5K</div>', unsafe_allow_html=True)
st.markdown('<div class="caption-text">Diseñado científicamente para iniciación, prevención de lesiones y poblaciones sedentarias. Optimizado para tu salud.</div>', unsafe_allow_html=True)

# ==========================================
# 2. PERSISTENCIA DE DATOS DE ATLETAS (HÍBRIDA)
# ==========================================
DB_PATH = "atletas.json"

def cargar_atletas():
    # Intentar cargar desde Google Sheets si está configurada la URL de la API
    if GSHEET_API_URL != "URL_DE_TU_WEB_APP" and GSHEET_API_URL.strip() != "":
        try:
            response = requests.get(GSHEET_API_URL, timeout=8)
            if response.status_code == 200:
                data = response.json()
                # Si la hoja de cálculo de Google Sheets está vacía ([]) pero tenemos una base de datos local
                # con registros, los subimos automáticamente para inicializar la nube!
                if not data and os.path.exists(DB_PATH):
                    try:
                        with open(DB_PATH, "r", encoding="utf-8") as f:
                            local_data = json.load(f)
                            if local_data:
                                guardar_atletas(local_data)
                                return local_data
                    except Exception:
                        pass
                return data
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error al conectar con Google Sheets: {e}. Usando base de datos local.")

    # Fallback local
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_atletas(atletas_list):
    local_saved = False
    # Guardar siempre respaldo local
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(atletas_list, f, indent=4, ensure_ascii=False)
        local_saved = True
    except Exception:
        pass
        
    # Guardar en Google Sheets si está configurada la URL de la API
    if GSHEET_API_URL != "URL_DE_TU_WEB_APP" and GSHEET_API_URL.strip() != "":
        try:
            response = requests.post(GSHEET_API_URL, json=atletas_list, timeout=8)
            if response.status_code == 200:
                return True
        except Exception as e:
            st.sidebar.error(f"⚠️ No se pudo guardar en Google Sheets: {e}. Respaldo local guardado.")
            return False
            
    return local_saved

# Cargar atletas de la base de datos local o remota
atletas = cargar_atletas()

# Inicialización segura de variables de autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = "atleta"

# Inicialización segura de variables del session_state para widgets vinculados
if "nombre_input" not in st.session_state:
    st.session_state.nombre_input = "Atleta"
if "edad_input" not in st.session_state:
    st.session_state.edad_input = 40
if "peso_input" not in st.session_state:
    st.session_state.peso_input = 70.0
if "talla_input" not in st.session_state:
    st.session_state.talla_input = 170
if "hipertension_input" not in st.session_state:
    st.session_state.hipertension_input = False
if "diabetes_input" not in st.session_state:
    st.session_state.diabetes_input = False
if "articulaciones_input" not in st.session_state:
    st.session_state.articulaciones_input = False
if "sobrepeso_input" not in st.session_state:
    st.session_state.sobrepeso_input = False
if "dias_semana_input" not in st.session_state:
    st.session_state.dias_semana_input = 3
if "sobrepeso_unclicked" not in st.session_state:
    st.session_state.sobrepeso_unclicked = False
if "clave_input" not in st.session_state:
    st.session_state.clave_input = ""

# Callback al seleccionar un atleta registrado
def cambiar_atleta():
    # Bloquear la página y limpiar entradas de sesión
    st.session_state.autenticado = False
    if "login_usuario_input" in st.session_state:
        st.session_state.login_usuario_input = ""
    if "login_clave_input" in st.session_state:
        st.session_state.login_clave_input = ""
        
    sel = st.session_state.atleta_seleccionado
    if sel == "-- Crear Nuevo Perfil --":
        st.session_state.nombre_input = "Atleta"
        st.session_state.edad_input = 40
        st.session_state.peso_input = 70.0
        st.session_state.talla_input = 170
        st.session_state.hipertension_input = False
        st.session_state.diabetes_input = False
        st.session_state.articulaciones_input = False
        st.session_state.sobrepeso_input = False
        st.session_state.dias_semana_input = 3
        st.session_state.sobrepeso_unclicked = False
        st.session_state.clave_input = ""
    else:
        atleta_data = next((a for a in atletas if a["nombre"] == sel), None)
        if atleta_data:
            st.session_state.nombre_input = atleta_data["nombre"]
            st.session_state.edad_input = atleta_data["edad"]
            st.session_state.peso_input = float(atleta_data["peso"])
            st.session_state.talla_input = int(atleta_data["talla"])
            st.session_state.hipertension_input = atleta_data.get("hipertension", False)
            st.session_state.diabetes_input = atleta_data.get("diabetes", False)
            st.session_state.articulaciones_input = atleta_data.get("articulaciones", False)
            st.session_state.sobrepeso_input = atleta_data.get("sobrepeso", False)
            st.session_state.dias_semana_input = int(atleta_data.get("dias_semana", 3))
            st.session_state.sobrepeso_unclicked = not atleta_data.get("sobrepeso", False)
            st.session_state.clave_input = atleta_data.get("clave", "")

# Reasignar selectbox antes de instanciarse en la re-ejecución y forzar sincronización de campos
if "atleta_reciente" in st.session_state:
    st.session_state.atleta_seleccionado = st.session_state.pop("atleta_reciente")
    cambiar_atleta()

# Reasignar peso y sobrepeso antes de renderizar inputs en la barra lateral
if "peso_reciente" in st.session_state:
    st.session_state.peso_input = st.session_state.pop("peso_reciente")
if "sobrepeso_reciente" in st.session_state:
    st.session_state.sobrepeso_input = st.session_state.pop("sobrepeso_reciente")

# ==========================================
# 3. BASE DE DATOS Y LÓGICA DEL PROGRAMA
# ==========================================
PLAN_BASE_5K = [
    # FASE 1
    {"semana": 1, "fase": "Fase 1: Adaptación", "estruc": "5' Calentamiento + 20' Caminata a paso firme + 5' Calm", "trote_min": 0, "rpe": "3-4", "objetivo": "Romper el sedentarismo sin impacto"},
    {"semana": 2, "fase": "Fase 1: Adaptación", "estruc": "5' Calentamiento + 25' Caminata a paso firme + 5' Calm", "trote_min": 0, "rpe": "3-4", "objetivo": "Aumentar capacidad aeróbica base"},
    {"semana": 3, "fase": "Fase 1: Adaptación", "estruc": "5' Calentamiento + 30' Caminata a paso firme + 5' Calm", "trote_min": 0, "rpe": "4", "objetivo": "Mantener ritmo constante y fluido"},
    {"semana": 4, "fase": "Fase 1: Adaptación", "estruc": "5' Calentamiento + 10x (1' Cam. rápida / 1' Cam. suave) + 5' Calm", "trote_min": 0, "rpe": "4-5", "objetivo": "Introducir cambios de ritmo suaves"},
    {"semana": 5, "fase": "Fase 1: Adaptación", "estruc": "5' Calentamiento + 35' Caminata continua + Fuerza suave", "trote_min": 0, "rpe": "4", "objetivo": "Evaluación de tolerancia articular"},
    
    # FASE 2
    {"semana": 6, "fase": "Fase 2: Método CACO", "estruc": "8 x (1' Trote suave / 2' Caminata)", "trote_min": 8, "rpe": "4-5", "objetivo": "Primer contacto con el impacto"},
    {"semana": 7, "fase": "Fase 2: Método CACO", "estruc": "6 x (2' Trote suave / 2' Caminata)", "trote_min": 12, "rpe": "4-5", "objetivo": "Aumentar volumen de trote"},
    {"semana": 8, "fase": "Fase 2: Método CACO", "estruc": "5 x (3' Trote suave / 2' Caminata)", "trote_min": 15, "rpe": "5", "objetivo": "Consolidación de intervalos"},
    {"semana": 9, "fase": "Fase 2: Método CACO", "estruc": "4 x (4' Trote suave / 2' Caminata)", "trote_min": 16, "rpe": "5", "objetivo": "Aumentar tiempo continuo de trote"},
    {"semana": 10, "fase": "Fase 2: Método CACO", "estruc": "Descarga: 30' Caminata + 3 x 2' Trote suave", "trote_min": 6, "rpe": "3-4", "objetivo": "Semana de asimilación e hidratación"},

    # FASE 3
    {"semana": 11, "fase": "Fase 3: Trote Continuo", "estruc": "3 x (6' Trote suave / 2' Caminata)", "trote_min": 18, "rpe": "5", "objetivo": "Dominio de bloques largos"},
    {"semana": 12, "fase": "Fase 3: Trote Continuo", "estruc": "3 x (7' Trote suave / 2' Caminata)", "trote_min": 21, "rpe": "5", "objetivo": "Aumento de densidad aeróbica"},
    {"semana": 13, "fase": "Fase 3: Trote Continuo", "estruc": "2 x (10' Trote suave / 2' Caminata)", "trote_min": 20, "rpe": "5", "objetivo": "Resistencia cardiovascular sostenida"},
    {"semana": 14, "fase": "Fase 3: Trote Continuo", "estruc": "2 x (12' Trote suave / 2' Caminata)", "trote_min": 24, "rpe": "5", "objetivo": "Fortalecimiento articular"},
    {"semana": 15, "fase": "Fase 3: Trote Continuo", "estruc": "15' Trote suave + 3' Caminata + 10' Trote suave", "trote_min": 25, "rpe": "5-6", "objetivo": "Transición a carrera continua"},

    # FASE 4
    {"semana": 16, "fase": "Fase 4: Consolidación 5K", "estruc": "5' Calentamiento + 20' Trote continuo + 5' Calm", "trote_min": 20, "rpe": "5-6", "objetivo": "Primera prueba continua (~2.5 - 3 km)"},
    {"semana": 17, "fase": "Fase 4: Consolidación 5K", "estruc": "5' Calentamiento + 25' Trote continuo + 5' Calm", "trote_min": 25, "rpe": "5-6", "objetivo": "Expansión de distancia (~3.5 km)"},
    {"semana": 18, "fase": "Fase 4: Consolidación 5K", "estruc": "5' Calentamiento + 30' Trote continuo + 5' Calm", "trote_min": 30, "rpe": "6", "objetivo": "Dominio de los 30 minutos (~4 km)"},
    {"semana": 19, "fase": "Fase 4: Consolidación 5K", "estruc": "5' Calentamiento + 35' Trote continuo a ritmo suave", "trote_min": 35, "rpe": "6", "objetivo": "Simulación pre-evento"},
    {"semana": 20, "fase": "Fase 4: Consolidación 5K", "estruc": "META 5K: Trote constante con breves pausas de hidratación", "trote_min": 40, "rpe": "6-7", "objetivo": "Completar los 5 Kilómetros"}
]

# Helper to generate the structured weekly calendar
def get_weekly_calendar(estruc, dias):
    run_day_desc = f"Sesión de carrera/caminata activa: {estruc}."
    
    if dias == 3:
        return [
            {"day": "Lunes", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Martes", "type": "Descanso", "desc": "Descanso total para permitir la asimilación muscular y articular.", "is_special": False, "is_rest": True},
            {"day": "Miércoles", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Jueves", "type": "Descanso", "desc": "Descanso total. Enfócate en una buena hidratación.", "is_special": False, "is_rest": True},
            {"day": "Viernes", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Sábado", "type": "Descanso Activo", "desc": "Caminata suave libre de 20 a 30 minutos o movilidad general muy ligera.", "is_special": True, "is_rest": False},
            {"day": "Domingo", "type": "Descanso", "desc": "Descanso completo. Recarga energías para la siguiente semana.", "is_special": False, "is_rest": True}
        ]
    elif dias == 4:
        return [
            {"day": "Lunes", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Martes", "type": "Descanso", "desc": "Descanso total y estiramientos suaves de tren inferior.", "is_special": False, "is_rest": True},
            {"day": "Miércoles", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Jueves", "type": "Fuerza y Core", "desc": "Ejercicios de fuerza para corredores (30 min): sentadillas, puentes de glúteo, pantorrillas y planchas. Ejercicios sin saltos.", "is_special": True, "is_rest": False},
            {"day": "Viernes", "type": "Descanso", "desc": "Descanso total para recuperarse de la sesión de fuerza.", "is_special": False, "is_rest": True},
            {"day": "Sábado", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Domingo", "type": "Descanso", "desc": "Descanso completo para asimilación articular de los entrenamientos.", "is_special": False, "is_rest": True}
        ]
    else:  # dias == 5
        return [
            {"day": "Lunes", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Martes", "type": "Movilidad & Flexibilidad", "desc": "Sesión de movilidad articular activa (20 min) enfocada en tobillo, rodillas, cadera y estiramientos dinámicos.", "is_special": True, "is_rest": False},
            {"day": "Miércoles", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Jueves", "type": "Fuerza Funcional", "desc": "Ejercicios con peso corporal (30 min) para ganar estabilidad articular: desplantes estáticos, core y flexores de cadera.", "is_special": True, "is_rest": False},
            {"day": "Viernes", "type": "Entrenamiento", "desc": run_day_desc, "is_special": False, "is_rest": False},
            {"day": "Sábado", "type": "Caminata Regenerativa", "desc": "Paseo recreativo muy ligero de 20-30 minutos a paso conversacional sin prisas ni exigencias.", "is_special": True, "is_rest": False},
            {"day": "Domingo", "type": "Descanso", "desc": "Descanso absoluto. Preparación integral para el ciclo semanal entrante.", "is_special": False, "is_rest": True}
        ]

# ==========================================
# 4. SIDEBAR / FORMULARIO DEL ATLETA
# ==========================================
with st.sidebar:
    st.markdown("### 📂 Perfiles Registrados")
    nombres_atletas = ["-- Crear Nuevo Perfil --"] + [a["nombre"] for a in atletas]
    st.selectbox(
        "Cargar atleta guardado:", 
        options=nombres_atletas, 
        key="atleta_seleccionado", 
        on_change=cambiar_atleta
    )
    
    # 🔒 SISTEMA DE ACCESO SEGURO
    st.markdown("---")
    st.markdown("### 🔒 Acceso Seguro")
    is_new_profile = (st.session_state.atleta_seleccionado == "-- Crear Nuevo Perfil --")
    
    if is_new_profile:
        st.session_state.autenticado = True
        st.session_state.rol_usuario = "atleta"
        st.markdown(
            '<div style="color: #34D399; font-size: 0.85rem; font-weight: 600; margin-bottom: 10px;">🟢 Modo Registro: Rellena los datos para guardar tu perfil.</div>',
            unsafe_allow_html=True
        )
    else:
        atleta_sel_data = next((a for a in atletas if a["nombre"] == st.session_state.atleta_seleccionado), None)
        
        col_login_u, col_login_p = st.columns(2)
        with col_login_u:
            usuario_login = st.text_input("Usuario", value="", key="login_usuario_input")
        with col_login_p:
            clave_login = st.text_input("Contraseña", type="password", value="", key="login_clave_input")
            
        # Validaciones de contraseñas y roles (Admin YEHU / YEHU1981)
        if usuario_login == "YEHU" and clave_login == "YEHU1981":
            st.session_state.autenticado = True
            st.session_state.rol_usuario = "admin"
            st.markdown(
                '<div style="color: #34D399; font-size: 0.85rem; font-weight: 600; margin-bottom: 10px;">🔓 Acceso: Administrador Conectado</div>',
                unsafe_allow_html=True
            )
        elif atleta_sel_data and usuario_login == atleta_sel_data["nombre"] and clave_login == atleta_sel_data.get("clave", ""):
            st.session_state.autenticado = True
            st.session_state.rol_usuario = "atleta"
            st.markdown(
                f'<div style="color: #00E5FF; font-size: 0.85rem; font-weight: 600; margin-bottom: 10px;">🔓 Acceso: Perfil de {usuario_login} Desbloqueado</div>',
                unsafe_allow_html=True
            )
        else:
            st.session_state.autenticado = False
            st.session_state.rol_usuario = "atleta"
            if usuario_login != "" or clave_login != "":
                st.markdown(
                    '<div style="color: #F87171; font-size: 0.85rem; font-weight: 600; margin-bottom: 10px;">❌ Credenciales Incorrectas</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="color: #94A3B8; font-size: 0.85rem; font-weight: 500; margin-bottom: 10px;">🔒 Ingresa datos de acceso para desbloquear.</div>',
                    unsafe_allow_html=True
                )
                
    st.markdown("---")
    st.markdown("### 📋 Registro de Atleta")
    nombre = st.text_input("Nombre del Atleta/Paciente", key="nombre_input")
    edad = st.number_input("Edad", min_value=18, max_value=90, key="edad_input")
    
    # Weight and Height for BMI
    st.markdown("##### Métricas Antropométricas")
    col_w, col_h = st.columns(2)
    with col_w:
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, key="peso_input", step=0.1)
    with col_h:
        talla = st.number_input("Estatura (cm)", min_value=100, max_value=220, key="talla_input", step=1)
        
    # Dynamic BMI (IMC) Calculation
    estatura_m = talla / 100.0
    imc = peso / (estatura_m ** 2)
    
    if imc < 18.5:
        imc_cat = "Bajo Peso"
        imc_color = "#38BDF8"  # Light Blue
    elif imc < 25.0:
        imc_cat = "Normal"
        imc_color = "#34D399"  # Green
    elif imc < 30.0:
        imc_cat = "Sobrepeso"
        imc_color = "#FBBF24"  # Amber
    else:
        imc_cat = "Obesidad"
        imc_color = "#F87171"  # Red
        
    # Auto overweight condition trigger
    auto_sobrepeso = (imc >= 25.0)
    if auto_sobrepeso and not st.session_state.sobrepeso_unclicked:
        st.session_state.sobrepeso_input = True
        
    def on_sobrepeso_change():
        if not st.session_state.sobrepeso_input:
            st.session_state.sobrepeso_unclicked = True
        else:
            st.session_state.sobrepeso_unclicked = False

    # Heart Rate (Frecuencia Cardíaca) Calculations (Tanaka formula)
    fc_max = int(208 - (0.7 * edad))
    # Initiation zone (55% to 70%)
    fc_rec_min = int(0.55 * fc_max)
    fc_rec_max = int(0.70 * fc_max)
    # Break down zones
    fc_z1_min = int(0.55 * fc_max)
    fc_z1_max = int(0.62 * fc_max)
    fc_z2_min = int(0.62 * fc_max)
    fc_z2_max = int(0.70 * fc_max)

    st.markdown("---")
    st.markdown("### 🏥 Condiciones de Salud")
    st.caption("Selecciona antecedentes médicos diagnosticados:")
    hipertension = st.checkbox("Hipertensión Arterial", key="hipertension_input")
    diabetes = st.checkbox("Diabetes Tipo 2", key="diabetes_input")
    articulaciones = st.checkbox("Molestias articulares previas", key="articulaciones_input")
    sobrepeso = st.checkbox("Sobrepeso u Obesidad", key="sobrepeso_input", on_change=on_sobrepeso_change)
    
    st.markdown("---")
    st.markdown("### ⚙️ Planificación")
    dias_semana = st.slider("Días de actividad a la semana", min_value=3, max_value=5, key="dias_semana_input")
    
    st.markdown("---")
    st.markdown("### 🔑 Clave del Perfil")
    clave = st.text_input("Definir contraseña para este perfil", type="password", key="clave_input")
    
    # Save/Update profile button
    st.markdown("---")
    if st.button("💾 Guardar/Registrar Atleta", width='stretch'):
        if not clave:
            st.error("⚠️ Debes definir una contraseña para proteger el perfil.")
        else:
            hoy_str = datetime.date.today().strftime("%Y-%m-%d")
            
            # Translate month to Spanish
            meses_es = {
                "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
            }
            month_en = datetime.date.today().strftime("%B")
            month_es = meses_es.get(month_en, month_en)
            mes_actual_txt = f"{month_es} {datetime.date.today().strftime('%Y')}"

            # Check if already exists to update
            atleta_idx = next((i for i, a in enumerate(atletas) if a["nombre"] == nombre), -1)
            
            if atleta_idx >= 0:
                existing_atleta = atletas[atleta_idx]
                fecha_reg = existing_atleta.get("fecha_registro", hoy_str)
                historial = existing_atleta.get("historial", [])
                
                nuevo_atleta = {
                    "nombre": nombre,
                    "edad": edad,
                    "peso": round(peso, 1),
                    "talla": talla,
                    "imc": round(imc, 2),
                    "imc_cat": imc_cat,
                    "hipertension": hipertension,
                    "diabetes": diabetes,
                    "articulaciones": articulaciones,
                    "sobrepeso": sobrepeso,
                    "dias_semana": dias_semana,
                    "fc_max": fc_max,
                    "fc_min_recom": fc_rec_min,
                    "fc_max_recom": fc_rec_max,
                    "fecha_registro": fecha_reg,
                    "clave": clave,
                    "historial": historial
                }
                atletas[atleta_idx] = nuevo_atleta
                st.toast(f"✅ ¡Perfil de {nombre} actualizado con éxito!")
            else:
                fecha_reg = hoy_str
                # Add initial registration weight to history log
                inicial_historial = [
                    {
                        "fecha": hoy_str,
                        "mes_control": mes_actual_txt,
                        "peso": round(peso, 1),
                        "talla": talla,
                        "imc": round(imc, 2),
                        "comentario": "Registro inicial del perfil."
                    }
                ]
                
                nuevo_atleta = {
                    "nombre": nombre,
                    "edad": edad,
                    "peso": round(peso, 1),
                    "talla": talla,
                    "imc": round(imc, 2),
                    "imc_cat": imc_cat,
                    "hipertension": hipertension,
                    "diabetes": diabetes,
                    "articulaciones": articulaciones,
                    "sobrepeso": sobrepeso,
                    "dias_semana": dias_semana,
                    "fc_max": fc_max,
                    "fc_min_recom": fc_rec_min,
                    "fc_max_recom": fc_rec_max,
                    "fecha_registro": fecha_reg,
                    "clave": clave,
                    "historial": inicial_historial
                }
                atletas.append(nuevo_atleta)
                st.toast(f"✅ ¡Atleta {nombre} registrado con éxito!")
                
            guardar_atletas(atletas)
            st.session_state.atleta_reciente = nombre
            st.rerun()

    st.markdown(
        """
        <div style="background: rgba(14, 116, 144, 0.15); border-left: 4px solid #0E7490; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #E2E8F0; line-height: 1.4; margin-top: 10px;">
            💡 <strong>Regla de Seguridad:</strong> La intensidad debe mantenerse en el <strong>"Test del Habla"</strong> (poder mantener una conversación sin jadear).
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 5. DASHBOARD Y VISUALIZACIÓN
# ==========================================

# 🔒 RESTRICCIÓN DE PANTALLA PRINCIPAL SI NO ESTÁ AUTENTICADO
if not st.session_state.get("autenticado", False):
    st.markdown("---")
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(239, 68, 68, 0.2); border-left: 5px solid #EF4444; border-radius: 12px; padding: 2.5rem; text-align: center; margin-top: 2rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);">
            <h2 style="color: #F8FAFC; margin-top: 0; font-weight: 700; letter-spacing: -0.5px;">🔒 Acceso Restringido</h2>
            <p style="color: #94A3B8; font-size: 1.05rem; max-width: 600px; margin: 0.5rem auto 1.5rem auto; line-height: 1.5;">
                Este perfil de entrenamiento está protegido para garantizar la confidencialidad de la información antropométrica y médica.
            </p>
            <div style="font-size: 0.9rem; color: #E2E8F0; background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 6px; display: inline-block;">
                🔑 Ingresa tu <strong>Usuario</strong> y <strong>Contraseña</strong> correspondientes en la barra lateral para desbloquear el plan.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

st.subheader(f"Plan Personalizado para: {nombre}")

# Dynamic Health metrics block in the sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Métricas de Salud Calculadas")
    
    # IMC Display card
    st.markdown(
        f"""
        <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Índice de Masa Corporal (IMC)</div>
            <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px;">
                <span style="font-size: 1.8rem; font-weight: 700; color: {imc_color};">{imc:.2f}</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: {imc_color};">({imc_cat})</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Peso: {peso:.1f} kg | Talla: {talla} cm</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Recommended HR Display card
    st.markdown(
        f"""
        <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Frecuencia Cardíaca de Corredor</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #FF4B4B; margin-top: 4px;">
                {fc_rec_min} - {fc_rec_max} <span style="font-size: 0.85rem; font-weight: 500; color: #94A3B8;">ppm</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Rango aeróbico saludable sugerido (55%-70% de la FC Máx: {fc_max} ppm).</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Monthly progress entry expander (Only if a valid registered profile is active)
    if st.session_state.atleta_seleccionado != "-- Crear Nuevo Perfil --":
        st.markdown("---")
        with st.expander("📈 Registrar Control Mensual"):
            st.caption("Añade un nuevo control de peso para el histórico:")
            
            meses_opciones = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                              "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            anio_actual = int(datetime.date.today().strftime("%Y"))
            
            col_sel_mes, col_sel_anio = st.columns(2)
            with col_sel_mes:
                mes_sel = st.selectbox("Mes", options=meses_opciones, index=datetime.date.today().month - 1)
            with col_sel_anio:
                anio_sel = st.selectbox("Año", options=[anio_actual, anio_actual + 1], index=0)
                
            peso_ctrl = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=peso, step=0.1, key="peso_ctrl_input")
            comentario_ctrl = st.text_input("Nota/Comentario", value="Control rutinario.", key="comentario_ctrl_input")
            
            if st.button("💾 Guardar Control", width='stretch'):
                act_atleta_idx = next((i for i, a in enumerate(atletas) if a["nombre"] == nombre), -1)
                if act_atleta_idx >= 0:
                    imc_ctrl = peso_ctrl / ((talla / 100.0) ** 2)
                    mes_control_txt = f"{mes_sel} {anio_sel}"
                    
                    nuevo_control = {
                        "fecha": datetime.date.today().strftime("%Y-%m-%d"),
                        "mes_control": mes_control_txt,
                        "peso": round(peso_ctrl, 1),
                        "talla": talla,
                        "imc": round(imc_ctrl, 2),
                        "comentario": comentario_ctrl
                    }
                    
                    hist = atletas[act_atleta_idx].get("historial", [])
                    exist_idx = next((i for i, h in enumerate(hist) if h["mes_control"] == mes_control_txt), -1)
                    
                    if exist_idx >= 0:
                        hist[exist_idx] = nuevo_control
                        st.toast(f"✅ Control de {mes_control_txt} actualizado.")
                    else:
                        hist.append(nuevo_control)
                        st.toast(f"✅ Nuevo control de {mes_control_txt} añadido.")
                        
                    atletas[act_atleta_idx]["historial"] = hist
                    
                    # Update active weight and BMI to the latest control
                    atletas[act_atleta_idx]["peso"] = round(peso_ctrl, 1)
                    atletas[act_atleta_idx]["imc"] = round(imc_ctrl, 2)
                    if imc_ctrl >= 25.0:
                        atletas[act_atleta_idx]["sobrepeso"] = True
                        
                    guardar_atletas(atletas)
                    
                    st.session_state.peso_reciente = float(peso_ctrl)
                    st.session_state.sobrepeso_reciente = (imc_ctrl >= 25.0)
                    st.session_state.atleta_reciente = nombre
                    st.rerun()

# Render main dashboard metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown('<div class="metric-card"><div class="metric-value">20 Semanas</div><div class="metric-label">Duración Total</div></div>', width='stretch')
with col_m2:
    st.markdown('<div class="metric-card"><div class="metric-value">5.0 KM</div><div class="metric-label">Meta de Distancia</div></div>', width='stretch')
with col_m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{dias_semana} Días</div><div class="metric-label">Frecuencia Semanal</div></div>', width='stretch')
with col_m4:
    has_condition = hipertension or diabetes or articulaciones or sobrepeso
    status_text = "Especial" if has_condition else "Estándar"
    status_color_style = "background: linear-gradient(135deg, #FF4B4B, #FFB703); -webkit-background-clip: text; -webkit-text-fill-color: transparent;" if has_condition else "background: linear-gradient(135deg, #00E5FF, #C0FF00); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="{status_color_style}">{status_text}</div><div class="metric-label">Perfil de Salud</div></div>', width='stretch')

st.write("")
st.write("")

# Organizar en pestañas estilizadas (Hiding management and export tabs for standard athlete users)
if st.session_state.get("rol_usuario", "atleta") == "admin":
    tab_tabla, tab_semanal, tab_gestion, tab_export = st.tabs([
        "📊 Macrociclo y Progreso", 
        "🔍 Detalle Semanal y Calendario", 
        "👥 Gestión de Atletas", 
        "📥 Exportar Datos"
    ])
else:
    tab_tabla, tab_semanal = st.tabs([
        "📊 Macrociclo y Progreso", 
        "🔍 Detalle Semanal y Calendario"
    ])

# Pre-generate DataFrame for Plotly and general table
df_plan = pd.DataFrame(PLAN_BASE_5K)

with tab_tabla:
    # Generar la estructura del macrociclo diaria de forma dinámica según la frecuencia de entrenamiento
    macro_rows = []
    for row in PLAN_BASE_5K:
        sem = row["semana"]
        fase = row["fase"]
        estruc = row["estruc"]
        trote = row["trote_min"]
        rpe = row["rpe"]
        obj = row["objetivo"]
        
        cal_days = get_weekly_calendar(estruc, dias_semana)
        
        def get_concise_desc(day):
            dtype = day["type"]
            if dtype == "Entrenamiento":
                return estruc
            elif dtype == "Descanso":
                return "Descanso"
            elif dtype == "Descanso Activo":
                return "Caminata Suave"
            elif dtype == "Fuerza y Core":
                return "Fuerza/Core (30m)"
            elif dtype == "Fuerza Funcional":
                return "Fuerza (30m)"
            elif dtype == "Movilidad & Flexibilidad":
                return "Movilidad (20m)"
            elif dtype == "Caminata Regenerativa":
                return "Caminata Suave"
            return dtype
            
        week_row = {
            "Semana": f"Sem. {sem}",
            "Fase del Plan": fase,
            "Lunes": get_concise_desc(cal_days[0]),
            "Martes": get_concise_desc(cal_days[1]),
            "Miércoles": get_concise_desc(cal_days[2]),
            "Jueves": get_concise_desc(cal_days[3]),
            "Viernes": get_concise_desc(cal_days[4]),
            "Sábado": get_concise_desc(cal_days[5]),
            "Domingo": get_concise_desc(cal_days[6]),
            "Trote (min)": trote,
            "Esfuerzo (RPE)": rpe,
            "Objetivo Fisiológico": obj
        }
        macro_rows.append(week_row)
        
    df_macro_diario = pd.DataFrame(macro_rows)
    
    st.write("#### 📈 Progresión del Volumen de Trote")
    st.caption("Gráfico interactivo de sobrecarga progresiva (minutos totales de trote acumulado por sesión).")
    
    # Plotly chart creation with premium dark sports styling
    fig = px.line(
        df_plan,
        x='semana',
        y='trote_min',
        labels={'semana': 'Semana de Entrenamiento', 'trote_min': 'Minutos de Trote'},
        markers=True
    )
    
    fig.update_traces(
        line=dict(color='#00E5FF', width=3),
        marker=dict(size=8, color='#C0FF00', symbol='circle', line=dict(color='#0F172A', width=1.5)),
        hovertemplate="<b>Semana %{x}</b><br>Trote: %{y} min"
    )
    
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor='rgba(15, 23, 42, 0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F8FAFC',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickmode='linear',
            tick0=1,
            dtick=1,
            title="Semana"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="Minutos de Trote"
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=280
    )
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.write(f"#### 📅 Estructura Diaria del Macrociclo (20 Semanas) — Plan de {dias_semana} Días")
    st.caption("Distribución completa día por día. Muestra las sesiones del plan y actividades complementarias de forma interactiva.")
    st.dataframe(df_macro_diario, width='stretch', hide_index=True)

    # 4. Monthly progress charts section (Only shown if historical entries exist)
    atleta_sel_data = next((a for a in atletas if a["nombre"] == nombre), None)
    if atleta_sel_data and len(atleta_sel_data.get("historial", [])) > 1:
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
        st.write("#### 📈 Evolución Corporal Histórica del Atleta")
        st.caption("Gráficos interactivos de seguimiento del peso y del Índice de Masa Corporal (IMC) por mes.")
        
        df_hist = pd.DataFrame(atleta_sel_data["historial"])
        
        col_h_peso, col_h_imc = st.columns(2)
        with col_h_peso:
            fig_peso = px.line(
                df_hist,
                x="mes_control",
                y="peso",
                labels={"mes_control": "Mes", "peso": "Peso (kg)"},
                markers=True
            )
            fig_peso.update_traces(
                line=dict(color='#00E5FF', width=3),
                marker=dict(size=8, color='#C0FF00', symbol='circle', line=dict(color='#0F172A', width=1.5)),
                hovertemplate="<b>Mes: %{x}</b><br>Peso: %{y} kg"
            )
            fig_peso.update_layout(
                hovermode="x unified",
                plot_bgcolor='rgba(15, 23, 42, 0.4)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Peso (kg)"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=250
            )
            st.plotly_chart(fig_peso, width='stretch')
            
        with col_h_imc:
            fig_imc = px.line(
                df_hist,
                x="mes_control",
                y="imc",
                labels={"mes_control": "Mes", "imc": "IMC"},
                markers=True
            )
            fig_imc.update_traces(
                line=dict(color='#EC4899', width=3),
                marker=dict(size=8, color='#FF85A2', symbol='circle', line=dict(color='#0F172A', width=1.5)),
                hovertemplate="<b>Mes: %{x}</b><br>IMC: %{y}"
            )
            fig_imc.update_layout(
                hovermode="x unified",
                plot_bgcolor='rgba(15, 23, 42, 0.4)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="IMC"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=250
            )
            st.plotly_chart(fig_imc, width='stretch')
            
        with st.expander("👁️ Ver Registro Detallado del Historial Mensual"):
            df_hist_table = df_hist[["fecha", "mes_control", "peso", "imc", "comentario"]].rename(columns={
                "fecha": "Fecha Registro",
                "mes_control": "Mes Control",
                "peso": "Peso (kg)",
                "imc": "IMC",
                "comentario": "Comentario / Notas"
            })
            st.dataframe(df_hist_table, width='stretch', hide_index=True)

with tab_semanal:
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        semana_sel = st.selectbox("Selecciona la semana de entrenamiento a consultar:", options=list(range(1, 21)))
    with col_sel2:
        # Progress indicator through the 20 weeks
        st.write(f"**Progreso del Plan: {int((semana_sel/20)*100)}%**")
        st.progress(semana_sel / 20)
        
    datos_sem = PLAN_BASE_5K[semana_sel - 1]
    
    # Custom colored banner per phase
    phase_colors = {
        "Fase 1: Adaptación": "border-left: 5px solid #64748B; background: rgba(100, 116, 139, 0.1);",
        "Fase 2: Método CACO": "border-left: 5px solid #3B82F6; background: rgba(59, 130, 246, 0.1);",
        "Fase 3: Trote Continuo": "border-left: 5px solid #10B981; background: rgba(16, 185, 129, 0.1);",
        "Fase 4: Consolidación 5K": "border-left: 5px solid #D97706; background: rgba(217, 119, 6, 0.1);"
    }
    
    phase_style = phase_colors.get(datos_sem['fase'], "border-left: 5px solid #00E5FF; background: rgba(0, 229, 255, 0.1);")
    
    st.markdown(
        f"""
        <div style="{phase_style} border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem;">
            <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #CBD5E1;">Fase Actual</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.3rem;">{datos_sem['fase']} — Semana {datos_sem['semana']}</div>
            <div style="font-size: 1rem; color: #94A3B8; font-weight: 500;">🎯 Objetivo: {datos_sem['objetivo']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Detail columns
    col_routine, col_safety = st.columns([1.2, 1])
    
    with col_routine:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("##### 🏃‍♂️ Estructura de la Sesión de Trote")
        st.info(f"👉 **Rutina:** {datos_sem['estruc']}")
        
        # Display intensity recommendation and Heart Rate targets
        rpe_val = datos_sem['rpe']
        st.markdown(
            f"""
            <div style="display: inline-flex; flex-direction: column; gap: 0.4rem; background: rgba(255, 255, 255, 0.05); padding: 0.75rem 1.25rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-top: 0.5rem; width: 100%;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Esfuerzo Percibido Sugerido (RPE):</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #00E5FF;">{rpe_val} / 10</span>
                </div>
                <hr style="border-color: rgba(255,255,255,0.05); margin: 6px 0;">
                <div>
                    <span style="font-size: 0.85rem; color: #94A3B8; font-weight: 600; display: block; margin-bottom: 2px;">Rango Frecuencia Cardíaca Recomendada para {nombre}:</span>
                    <span style="font-size: 0.95rem; font-weight: 700; color: #FF4B4B;">
                        • Caminata Ligera (Z1): {fc_z1_min} - {fc_z1_max} ppm<br>
                        • Trote Aeróbico (Z2): {fc_z2_min} - {fc_z2_max} ppm
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("###### Guía RPE Simplificada para Principiantes:")
        st.caption("• **RPE 3-4 (Muy suave)**: Ritmo conversacional completo, puedes cantar mientras corres.\n"
                   "• **RPE 5-6 (Suave - Moderado)**: Puedes hablar cómodamente con oraciones largas.\n"
                   "• **RPE 7 (Moderado)**: Respiración más profunda, puedes responder preguntas cortas pero no mantener charlas largas.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_safety:
        if has_condition:
            st.markdown('<div class="section-card" style="border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.03);">', unsafe_allow_html=True)
            st.write("##### 🩺 Directrices de Salud Personalizadas")
            
            if hipertension:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 0.8rem; font-size: 0.88rem; color: #F8FAFC; line-height: 1.4;">
                        <span style="color: #FF5A5F; font-weight: 700;">⚠️ HIPERTENSIÓN ARTERIAL:</span>
                        <ul>
                            <li>Mantén la intensidad rigurosamente bajo el "test del habla" (RPE ≤ 5).</li>
                            <li><strong>Límite de FC:</strong> Se recomienda no superar el 65% de la FC Máx (máximo <strong>{int(0.65 * fc_max)} ppm</strong>) para entrenar con seguridad.</li>
                            <li>Realiza respiraciones fluidas. Evita contener el aire (apnea).</li>
                            <li>Toma sorbos constantes de agua durante la caminata de recuperación.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            if diabetes:
                st.markdown(
                    """
                    <div style="margin-bottom: 0.8rem; font-size: 0.88rem; color: #F8FAFC; line-height: 1.4;">
                        <span style="color: #60A5FA; font-weight: 700;">💙 DIABETES TIPO 2:</span>
                        <ul>
                            <li>Mide tu glucemia antes del esfuerzo. Si es menor de 100 mg/dL, consume carbohidratos simples.</li>
                            <li>Lleva siempre contigo una ración de emergencia de carbohidratos de absorción rápida.</li>
                            <li>Usa medias/calcetines de algodón sin costuras gruesas y revisa tus pies al descalzarte.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            if articulaciones:
                st.markdown(
                    """
                    <div style="margin-bottom: 0.8rem; font-size: 0.88rem; color: #F8FAFC; line-height: 1.4;">
                        <span style="color: #FBBF24; font-weight: 700;">🦵 MOLESTIAS ARTICULARES PREVIAS:</span>
                        <ul>
                            <li>Entrena en superficies blandas y llanas (tierra, césped) en vez de hormigón.</li>
                            <li>Mantén una zancada corta y aumenta la cadencia para mitigar las cargas de impacto.</li>
                            <li>Ante un dolor articular agudo, suspende la sesión. No corras con molestias punzantes.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            if sobrepeso:
                st.markdown(
                    """
                    <div style="margin-bottom: 0.2rem; font-size: 0.88rem; color: #F8FAFC; line-height: 1.4;">
                        <span style="color: #EC4899; font-weight: 700;">⚖️ SOBREPESO U OBESIDAD:</span>
                        <ul>
                            <li><strong>Impacto articular:</strong> Alterna caminar rápido con trote muy suave. El calzado de running con excelente amortiguación es tu mejor aliado.</li>
                            <li><strong>Entrenamiento cruzado:</strong> En los días que no corres, realiza elíptica, natación o ciclismo de baja intensidad para mantener el gasto calórico con cero impacto articular.</li>
                            <li><strong>Progreso conservador:</strong> Escucha a tus rodillas y tobillos. Si hay molestia persistente, detén la sesión o vuelve a caminar rápido.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write("##### 💡 Reglas Generales de Seguridad")
            st.write("• Realiza siempre caminata a ritmo de paseo cómodo para calentar y enfriar.")
            st.write("• Si sientes que tu ritmo cardíaco se eleva bruscamente o sientes asfixia, pasa inmediatamente a caminar suave.")
            st.write("• Las sesiones principales de caminata o carrera deben distribuirse en días alternos.")
            st.markdown('</div>', unsafe_allow_html=True)

    # Dynamic weekly calendar schedule rendering (Splitting 4 and 3)
    st.write("#### 📆 Distribución Semanal del Planificador")
    st.caption(f"Cronograma semanal recomendado para una frecuencia de **{dias_semana} días** de entrenamiento:")
    
    cal = get_weekly_calendar(datos_sem['estruc'], dias_semana)
    
    col_r1 = st.columns(4)
    col_r2 = st.columns(3)
    
    for idx, day in enumerate(cal):
        if day["is_rest"]:
            card_class = "day-card-rest"
            type_class = "day-type-rest"
        elif day["is_special"]:
            card_class = "day-card-special"
            type_class = "day-type-special"
        else:
            card_class = "day-card"
            type_class = "day-type"
            
        card_html = f"""
        <div class="{card_class}">
            <div class="day-name">{day['day']}</div>
            <div class="{type_class}">{day['type']}</div>
            <div class="day-description">{day['desc']}</div>
        </div>
        """
        
        if idx < 4:
            with col_r1[idx]:
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col_r2[idx - 4]:
                st.markdown(card_html, unsafe_allow_html=True)

    # Guía detallada de ejercicios complementarios para días de no carrera
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2.5rem 0;'>", unsafe_allow_html=True)
    st.write("#### 🏋️‍♀️ Guías y Rutinas de Ejercicios Complementarios")
    st.caption("Detalle técnico de los ejercicios recomendados para tus días de Fuerza, Movilidad y Caminata Regenerativa:")
    
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        card1_html = """
        <div class="section-card" style="min-height: 480px; background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h5 style="color: #F8FAFC; margin-top: 0; font-size: 1.1rem; font-weight: 600;">⚡ Fuerza Funcional (30 min)</h5>
            <p style="font-size: 0.82rem; color: #94A3B8; margin-top: -5px; margin-bottom: 10px;">Objetivo: Fortalecer tendones y core para estabilizar las articulaciones al correr.</p>
            <ul style="font-size: 0.88rem; color: #CBD5E1; padding-left: 20px; line-height: 1.5; margin-bottom: 15px;">
                <li style="margin-bottom: 8px;"><strong>Sentadillas con peso corporal (Squats):</strong> 3 series x 10-12 reps. <span style="color: #94A3B8; font-size: 0.8rem;">Bajar despacio con rodillas alineadas a la punta de los pies.</span></li>
                <li style="margin-bottom: 8px;"><strong>Puentes de Glúteo (Glute Bridges):</strong> 3 series x 12-15 reps. <span style="color: #94A3B8; font-size: 0.8rem;">Contraer glúteos arriba por 1 segundo.</span></li>
                <li style="margin-bottom: 8px;"><strong>Plancha Abdominal Estática (Planks):</strong> 3 series x 20-40 segundos. <span style="color: #94A3B8; font-size: 0.8rem;">Mantener cuerpo alineado, sin elevar la cadera.</span></li>
                <li style="margin-bottom: 8px;"><strong>Elevación de Pantorrillas (Calf Raises):</strong> 3 series x 15 reps. <span style="color: #94A3B8; font-size: 0.8rem;">Apoyarse en escalón, hacer el rango completo.</span></li>
                <li style="margin-bottom: 8px;"><strong>Desplantes Estáticos (Split Squats):</strong> 2 series x 8-10 reps/pierna. <span style="color: #94A3B8; font-size: 0.8rem;">Controlar el descenso, torso erguido.</span></li>
            </ul>
            <div style="font-size: 0.8rem; color: #C0FF00; margin-top: 10px; background: rgba(192, 255, 0, 0.08); border-left: 3px solid #C0FF00; padding: 6px 10px; border-radius: 4px;">
                💡 <strong>Consejo:</strong> Descansa 60 segundos entre series. Realiza los movimientos de forma lenta y controlada.
            </div>
        </div>
        """
        st.markdown(card1_html, unsafe_allow_html=True)
        
    with col_ex2:
        card2_html = """
        <div class="section-card" style="min-height: 480px; background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h5 style="color: #F8FAFC; margin-top: 0; font-size: 1.1rem; font-weight: 600;">🤸‍♂️ Movilidad y Flexibilidad (20 min)</h5>
            <p style="font-size: 0.82rem; color: #94A3B8; margin-top: -5px; margin-bottom: 10px;">Objetivo: Incrementar el rango de movimiento y lubricar tobillos, rodillas y cadera.</p>
            <div style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
                <strong style="color: #00E5FF;">1. Movilidad Dinámica (10 reps cada uno):</strong>
                <ul style="padding-left: 20px; margin-top: 4px; margin-bottom: 10px;">
                    <li style="margin-bottom: 4px;"><em>Tobillo contra pared:</em> Adelantar rodilla sin levantar el talón.</li>
                    <li style="margin-bottom: 4px;"><em>Péndulos de cadera:</em> Balanceos controlados al frente y costado.</li>
                    <li style="margin-bottom: 4px;"><em>Rotaciones:</em> Giros lentos de cadera y tobillos.</li>
                </ul>
                <strong style="color: #00E5FF;">2. Estiramientos Estáticos (Mantenidos 30s):</strong>
                <ul style="padding-left: 20px; margin-top: 4px;">
                    <li style="margin-bottom: 4px;"><em>Pantorrilla:</em> Apoyando manos en pared, pierna trasera bien estirada.</li>
                    <li style="margin-bottom: 4px;"><em>Psoas (Flexores):</em> En desplante con rodilla en suelo, empujar cadera adelante.</li>
                    <li style="margin-bottom: 4px;"><em>Isquiotibiales:</em> Sentado en suelo, pierna estirada, torso al frente.</li>
                    <li style="margin-bottom: 4px;"><em>Cuádriceps:</em> De pie, sujetar tobillo acercando talón al glúteo.</li>
                </ul>
            </div>
        </div>
        """
        st.markdown(card2_html, unsafe_allow_html=True)
        
    with col_ex3:
        card3_html = """
        <div class="section-card" style="min-height: 480px; background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h5 style="color: #F8FAFC; margin-top: 0; font-size: 1.1rem; font-weight: 600;">🚶‍♂️ Pautas de Caminata Regenerativa</h5>
            <p style="font-size: 0.82rem; color: #94A3B8; margin-top: -5px; margin-bottom: 10px;">Objetivo: Acelerar la recuperación muscular aumentando el flujo sanguíneo sin impacto.</p>
            <ul style="font-size: 0.88rem; color: #CBD5E1; padding-left: 20px; line-height: 1.5; margin-bottom: 15px;">
                <li style="margin-bottom: 8px;"><strong>Esfuerzo Sugerido (RPE 2-3):</strong> Ritmo de paseo fluido y cómodo. Debes respirar por la nariz y poder hablar o cantar sin esfuerzo.</li>
                <li style="margin-bottom: 8px;"><strong>Duración Recomendada:</strong> 20 a 30 minutos continuos.</li>
                <li style="margin-bottom: 8px;"><strong>Técnica de Caminata:</strong> Mantener una postura erguida pero relajada, braceo natural al costado, pasos cortos que aterricen planos en el suelo.</li>
                <li style="margin-bottom: 8px;"><strong>Frecuencia:</strong> Ideal para días de descanso activo para aliviar agujetas o fatiga de rodillas.</li>
            </ul>
            <div style="font-size: 0.8rem; color: #00E5FF; margin-top: 10px; background: rgba(0, 229, 255, 0.08); border-left: 3px solid #00E5FF; padding: 6px 10px; border-radius: 4px;">
                💡 <strong>Dato:</strong> Caminar aumenta el riego sanguíneo, aportando nutrientes que aceleran la reparación celular.
            </div>
        </div>
        """
        st.markdown(card3_html, unsafe_allow_html=True)

# 🔒 RESTRICCIÓN DE PESTAÑAS SÓLO VISIBLES PARA EL ADMINISTRADOR
if st.session_state.get("rol_usuario", "atleta") == "admin":
    with tab_gestion:
        st.write("#### 👥 Gestión de la Base de Datos de Atletas")
        st.caption("Administra, visualiza y analiza el perfil de las personas registradas en el sistema.")
        
        if not atletas:
            st.info("Aún no hay atletas registrados. Utiliza el formulario de la barra lateral para ingresar y guardar tu primer atleta.")
        else:
            # Render database metrics
            df_db = pd.DataFrame(atletas)
            
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_db)}</div><div class="metric-label">Total Atletas</div></div>', width='stretch')
            with col_g2:
                avg_imc_val = df_db["imc"].mean()
                st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_imc_val:.2f}</div><div class="metric-label">Promedio IMC</div></div>', width='stretch')
            with col_g3:
                overweight_count = len(df_db[df_db["imc"] >= 25.0])
                overweight_pct = (overweight_count / len(df_db)) * 100 if len(df_db) > 0 else 0
                st.markdown(f'<div class="metric-card"><div class="metric-value">{overweight_pct:.1f}%</div><div class="metric-label">Con Sobrepeso/Obesidad</div></div>', width='stretch')
                
            st.write("")
            st.write("##### 📋 Censo de Atletas Registrados")
            
            # Formatear el historial de pesos mes a mes para visualizarlo en la tabla del censo
            def formatear_historial_tabla(h_list):
                if not isinstance(h_list, list) or len(h_list) == 0:
                    return "Sin registros"
                return " ➔ ".join([f"{h['mes_control']}: {h['peso']} kg" for h in h_list])
                
            df_db["Historial de Peso (Mes a Mes)"] = df_db["historial"].apply(formatear_historial_tabla)
            
            # Clean columns for display
            df_db_display = df_db[[
                "nombre", "edad", "talla", "peso", "imc", "imc_cat", "Historial de Peso (Mes a Mes)", "dias_semana"
            ]].rename(columns={
                "nombre": "Nombre",
                "edad": "Edad",
                "talla": "Estatura (cm)",
                "peso": "Peso Actual (kg)",
                "imc": "IMC",
                "imc_cat": "Categoría IMC",
                "dias_semana": "Frecuencia (días/sem)"
            })
            st.dataframe(df_db_display, width='stretch', hide_index=True)
            
            # Historical control entry deletion actions
            if atleta_sel_data and len(atleta_sel_data.get("historial", [])) > 0:
                st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
                st.write(f"##### 📈 Gestión de Historial Mensual para: **{nombre}**")
                st.caption("Elimina controles mensuales incorrectos registrados para el perfil seleccionado.")
                
                historial_list = atleta_sel_data["historial"]
                
                col_hist_sel, col_hist_btn = st.columns([2, 1])
                with col_hist_sel:
                    control_a_eliminar = st.selectbox(
                        "Selecciona un control mensual a eliminar:", 
                        options=[h["mes_control"] for h in historial_list], 
                        key="del_control_sel"
                    )
                with col_hist_btn:
                    st.write("") # Spacer
                    if st.button("🗑️ Eliminar Control Mensual", width='stretch'):
                        # Filter history list
                        hist_nuevo = [h for h in historial_list if h["mes_control"] != control_a_eliminar]
                        
                        # Update in athletes data list
                        atleta_idx = next((i for i, a in enumerate(atletas) if a["nombre"] == nombre), -1)
                        if atleta_idx >= 0:
                            atletas[atleta_idx]["historial"] = hist_nuevo
                            
                            # Re-sync active metrics with latest remaining control, if any
                            if len(hist_nuevo) > 0:
                                ultimo_ctrl = hist_nuevo[-1]
                                atletas[atleta_idx]["peso"] = ultimo_ctrl["peso"]
                                atletas[atleta_idx]["imc"] = ultimo_ctrl["imc"]
                                st.session_state.peso_reciente = float(ultimo_ctrl["peso"])
                                st.session_state.sobrepeso_reciente = (ultimo_ctrl["imc"] >= 25.0)
                            
                            guardar_atletas(atletas)
                            st.toast(f"🗑️ Control de {control_a_eliminar} eliminado con éxito.")
                            st.session_state.atleta_reciente = nombre
                            st.rerun()

            # Database management actions
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
            st.write("##### ⚙️ Acciones Generales de Base de Datos")
            col_del_sel, col_del_btn = st.columns([2, 1])
            with col_del_sel:
                atleta_a_eliminar = st.selectbox("Selecciona un atleta para eliminar de los registros:", options=[a["nombre"] for a in atletas], key="del_atleta_sel")
            with col_del_btn:
                st.write("") # Spacer for vertical alignment
                if st.button("❌ Eliminar Perfil de Atleta", width='stretch'):
                    atletas_nuevos = [a for a in atletas if a["nombre"] != atleta_a_eliminar]
                    guardar_atletas(atletas_nuevos)
                    st.toast(f"🗑️ Registro de {atleta_a_eliminar} eliminado con éxito.")
                    st.session_state.atleta_reciente = "-- Crear Nuevo Perfil --"
                    st.rerun()

    with tab_export:
        st.write("#### 📥 Descarga la planificación de tu entrenamiento")
        st.caption("Exporta los datos estructurados adaptados con tu nombre y configuraciones para usarlos libremente.")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write("##### 📄 Exportar en Formato JSON")
            st.caption("Estructura de datos completa y jerárquica lista para integrarse con apps de calendario o código de software.")
            
            # Export JSON
            # Include current athlete anthropometric info in JSON export for personalization
            json_export_data = {
                "atleta": {
                    "nombre": nombre,
                    "edad": edad,
                    "peso_kg": peso,
                    "talla_cm": talla,
                    "imc": round(imc, 2),
                    "imc_cat": imc_cat,
                    "fc_max": fc_max,
                    "frecuencia_semanal": dias_semana,
                    "historial_mensual": atleta_sel_data.get("historial", []) if atleta_sel_data else []
                },
                "plan": PLAN_BASE_5K
            }
            
            json_data = json.dumps(json_export_data, indent=4, ensure_ascii=False)
            st.download_button(
                label="Descargar Plan en JSON 💾",
                data=json_data,
                file_name=f"plan_5k_{nombre.lower().replace(' ', '_')}.json",
                mime="application/json",
                width='stretch'
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_exp2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write("##### 📊 Exportar en Formato CSV (Excel)")
            st.caption("Planificación en tabla compatible con Microsoft Excel, Google Sheets o para impresión directa en hojas de cálculo.")
            
            # Export CSV
            csv_data = pd.DataFrame(PLAN_BASE_5K).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Plan en CSV 💾",
                data=csv_data,
                file_name=f"plan_5k_{nombre.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                width='stretch'
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with st.expander("👁️ Ver Vista Previa de los Datos Exportados (Plan)"):
            st.write(df_plan)
            
        # ☁️ GUÍA DE CONEXIÓN A GOOGLE SHEETS PARA EL ADMINISTRADOR
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
        st.write("##### ☁️ Sincronizar Base de Datos en Google Sheets (Acceso 24/7)")
        st.caption("Sigue estos pasos para conectar tu aplicación a Google Sheets y evitar perder registros al desplegar la app en la nube:")
        
        guia_html = """
        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.5rem; color: #CBD5E1; line-height: 1.6; margin-bottom: 1.5rem;">
            <strong style="color: #00E5FF; font-size: 1rem; display: block; margin-bottom: 8px;">📋 Instrucciones de Conexión:</strong>
            <ol style="margin-left: 20px; font-size: 0.9rem;">
                <li style="margin-bottom: 6px;">Crea una hoja de cálculo nueva en blanco dentro de tu cuenta de <strong>Google Drive</strong>.</li>
                <li style="margin-bottom: 6px;">En el menú superior de la hoja de cálculo, haz clic en <strong>Extensiones &gt; Apps Script</strong>.</li>
                <li style="margin-bottom: 6px;">Borra el código que aparece por defecto en el editor de Apps Script y pega el script de abajo (cópialo completo).</li>
                <li style="margin-bottom: 6px;">Haz clic en el icono de <strong>Guardar</strong> (disquete) y luego haz clic en el botón azul <strong>Implementar &gt; Nueva implementación</strong>.</li>
                <li style="margin-bottom: 6px;">Haz clic en el icono de engrane a la izquierda de "Seleccionar tipo" y elige <strong>Aplicación web</strong>.</li>
                <li style="margin-bottom: 6px;">Configura los campos exactamente así:
                    <ul style="margin-left: 15px; margin-top: 4px;">
                        <li><em>Descripción:</em> Base de datos Atletismo 0 a 5K.</li>
                        <li><em>Ejecutar como:</em> <strong>Tú (tu correo de Google)</strong>.</li>
                        <li><em>Quién tiene acceso:</em> <strong>Cualquiera</strong> (esto permite que Streamlit pueda comunicarse con la hoja).</li>
                    </ul>
                </li>
                <li style="margin-bottom: 6px;">Haz clic en <strong>Implementar</strong>. Te pedirá que presiones <em>Autorizar acceso</em> para otorgar permisos a tu cuenta de Google. Concédele los permisos (si te sale advertencia de seguridad, haz clic en "Configuración avanzada" y luego en "Ir a Proyecto sin título (no seguro)").</li>
                <li style="margin-bottom: 6px;">Una vez implementado, Google te proporcionará una <strong>URL de la aplicación web</strong> (debe terminar en <code>/exec</code>). Cópiala.</li>
                <li style="margin-bottom: 6px;">Abre tu archivo local <code>app.py</code> en tu PC y edita la **línea 10**. Reemplaza <code>"URL_DE_TU_WEB_APP"</code> por la URL que copiaste. Guarda el archivo y listo.</li>
            </ol>
            <div style="font-size: 0.82rem; color: #C0FF00; margin-top: 10px; background: rgba(192, 255, 0, 0.08); border-left: 3px solid #C0FF00; padding: 6px 12px; border-radius: 4px;">
                💡 <strong>Dato Premium:</strong> Al guardar atletas, el script de Google actualizará automáticamente dos pestañas en tu hoja de cálculo: <code>Censo Atletas</code> e <code>Historial Mensual</code> para que puedas revisar y descargar tus datos directamente desde Google Sheets de forma perfectamente formateada en tablas.
            </div>
        </div>
        """
        st.markdown(guia_html, unsafe_allow_html=True)
        
        apps_script_code = """// CÓDIGO GOOGLE APPS SCRIPT (Pegar completo en Extensiones > Apps Script)
function doGet(e) {
  var doc = SpreadsheetApp.getActiveSpreadsheet();
  var sheetJson = doc.getSheetByName("JSON_DB") || doc.insertSheet("JSON_DB");
  var data = sheetJson.getRange(1, 1).getValue();
  if (!data) {
    return ContentService.createTextOutput("[]").setMimeType(ContentService.MimeType.JSON);
  }
  return ContentService.createTextOutput(data).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var doc = SpreadsheetApp.getActiveSpreadsheet();
  var sheetJson = doc.getSheetByName("JSON_DB") || doc.insertSheet("JSON_DB");
  var postData = e.postData.contents;
  sheetJson.getRange(1, 1).setValue(postData);
  
  // Sincronizar en pestañas visuales legibles
  try {
    var atletas = JSON.parse(postData);
    
    // 1. Pestaña de Censo General
    var sheetCenso = doc.getSheetByName("Censo Atletas") || doc.insertSheet("Censo Atletas");
    sheetCenso.clear();
    sheetCenso.appendRow(["Nombre", "Edad", "Estatura (cm)", "Peso Actual (kg)", "IMC", "Categoría IMC", "Frecuencia (días)", "Clave"]);
    
    // 2. Pestaña de Historial Mensual
    var sheetHistorial = doc.getSheetByName("Historial Mensual") || doc.insertSheet("Historial Mensual");
    sheetHistorial.clear();
    sheetHistorial.appendRow(["Nombre", "Fecha Registro", "Mes Control", "Peso (kg)", "IMC", "Comentario / Notas"]);
    
    for (var i = 0; i < atletas.length; i++) {
      var a = atletas[i];
      sheetCenso.appendRow([a.nombre, a.edad, a.talla, a.peso, a.imc, a.imc_cat, a.dias_semana, a.clave]);
      
      var hist = a.historial || [];
      for (var j = 0; j < hist.length; j++) {
        var h = hist[j];
        sheetHistorial.appendRow([a.nombre, h.fecha, h.mes_control, h.peso, h.imc, h.comentario]);
      }
    }
  } catch (err) {}
  
  return ContentService.createTextOutput(JSON.stringify({status: "success"})).setMimeType(ContentService.MimeType.JSON);
}"""
        st.write("**Código a copiar en Apps Script:**")
        st.code(apps_script_code, language="javascript")
