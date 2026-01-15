import streamlit as st
import pandas as pd
from datetime import date
import os
import io
import time

# 1. CONFIGURACIÓN DE PÁGINA Y SEGURIDAD
st.set_page_config(
    page_title="Puntos Würth Uruguay",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- DISEÑO CORPORATIVO Y BLOQUEO DE MENÚS (CSS) ---
st.markdown("""
    <style>
    /* BLOQUEO DE VULNERABILIDADES VISUALES */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* FONDO Y TIPOGRAFÍA GENERAL */
    .stApp {
        background: linear-gradient(180deg, #FFFFFF 0%, #F0F2F5 100%);
    }
    
    /* PERSONALIZACIÓN DEL SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0;
    }
    [data-testid="stSidebarNav"] span {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ESTILO DE TARJETAS PARA MÉTRICAS */
    div[data-testid="stMetricValue"] {
        color: #E60002 !important;
        font-size: 60px !important;
        font-weight: 800;
    }
    
    /* BOTONES ESTILO WÜRTH */
    .stButton>button { 
        background-color: #E60002 !important; 
        color: white !important; 
        border-radius: 8px !important; 
        border: none !important;
        height: 3.5rem !important;
        font-size: 18px !important;
        font-weight: bold !important;
        transition: 0.3s all ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #CC0000 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(230,0,2,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Logo centrado en la parte superior
if os.path.exists('logo_UY.png'):
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    with col_l2:
        st.image('logo_UY.png', use_container_width=True)

DB_FILE = "base_datos_puntos.csv"
COLUMNAS_ESTANDAR = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str)
    return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

df = cargar_datos()

# --- NAVEGACIÓN LATERAL ---
st.sidebar.markdown("## 🛡️ Mi Cuenta")
opcion = st.sidebar.radio("Ir a:", ["🔍 Consultar mis Puntos", "🎁 Premios y Beneficios", "ℹ️ Ayuda"])

st.sidebar.divider()
acceso_staff = st.sidebar.checkbox("🔐 Acceso Staff Würth")

# --- FLUJO DE USUARIO (CLIENTE) ---
if not acceso_staff:
    if opcion == "🔍 Consultar mis Puntos":
        st.markdown("<h2 style='text-align: center; color: #333;'>Bienvenido al Portal de Fidelidad</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Ingresa tu ID de cliente para ver tu saldo actual</p>", unsafe_allow_html=True)
        
        id_busqueda = st.text_input("", placeholder="Número de Cliente (ej: 12345678)").strip()
        
        if id_busqueda:
            datos_cliente = df[df["ID_Cliente"] == id_busqueda]
            if not datos_cliente.empty:
                nombre = datos_cliente["Nombre_Cliente"].iloc[0]
                puntos_num = pd.to_numeric(datos_cliente["Puntos_Ganados"], errors='coerce').fillna(0)
                total = int(puntos_num.sum())
                
                st.markdown(f"<h3 style='text-align: center;'>¡Hola, {nombre}!</h3>", unsafe_allow_html=True)
                
                # Tarjeta de puntos
                col_m1, col_m2, col_m3 = st.columns([1,3,1])
                with col_m2:
                    st.metric("PUNTOS DISPONIBLES", f"{total}")
                
                with st.expander("📂 Ver detalle de mis últimas facturas"):
                    st.dataframe(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False), use_container_width=True)
                st.balloons()
            else:
                st.error("Número de cliente no encontrado. Por favor, consulta con tu vendedor asignado.")

    elif opcion == "🎁 Premios y Beneficios":
        st.markdown("## Catálogo de Premios")
        st.info("Próximamente podrás canjear tus puntos directamente desde aquí.")
        st.link_button("🚀 IR A LA WEB OFICIAL", "https://www.wurth.com.uy/")

    elif opcion == "ℹ️ Ayuda":
        st.markdown("### ¿Cómo funciona el sistema?")
        st.write("1. Por cada **$100** en tus compras sumas **1 punto**.")
        st.write("2. Los puntos se actualizan semanalmente.")
        st.write("3. Los canjes se gestionan a través de tu asesor comercial.")

# --- FLUJO ADMINISTRATIVO (STAFF) ---
else:
    st.markdown("<h2 style='color: #E60002;'>Panel de Administración</h2>", unsafe_allow_html=True)
    password = st.text_input("Clave de Seguridad", type="password")
    
    if password == "089020011":
        st.success("Acceso Staff verificado")
        tab1, tab2, tab3 = st.tabs(["📊 CARGA EXCEL", "➕ REGISTRO MANUAL", "🗑️ GESTIÓN BASE"])
        
        with tab1:
            st.markdown("#### Importar desde BI")
            archivo = st.file_uploader("Subir .xlsx", type=['xlsx'])
            if archivo:
                df_nuevo = pd.read_excel(archivo, dtype=str)
                # ... (Lógica de filtrado y carga que ya tenemos ...)
                if st.button("PROCESAR ARCHIVO"):
                    with st.spinner('Actualizando base de datos...'):
