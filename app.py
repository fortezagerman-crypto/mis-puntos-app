import streamlit as st
import pandas as pd
from datetime import date
import os
import io
import time

# 1. CONFIGURACIÓN DE SEGURIDAD Y PÁGINA
st.set_page_config(
    page_title="Puntos Würth Uruguay",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- DISEÑO AVANZADO (CSS) ---
st.markdown("""
    <style>
    /* OCULTAR ELEMENTOS DE DESARROLLO (SEGURIDAD) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* FONDO DE LA APP */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f4f4f4 100%);
    }

    /* AGRANDAR MENÚ LATERAL */
    [data-testid="stSidebarNav"] span {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #333;
    }
    
    /* ESTILO DE TARJETAS (CARD) PARA CONTENIDO */
    .stMarkdown div[data-testid="stMarkdownContainer"] p {
        font-size: 18px;
    }
    
    /* BOTÓN ROJO WÜRTH */
    .stButton>button { 
        background-color: #E60002 !important; 
        color: white !important; 
        border: none !important;
        border-radius: 8px !important; 
        height: 3em !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #b30001 !important;
        transform: scale(1.02);
    }

    /* MÉTRICA DE PUNTOS */
    [data-testid="stMetricValue"] {
        color: #E60002 !important;
        font-size: 48px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo centrado
if os.path.exists('logo_UY.png'):
    col_logo1, col_logo2, col_logo3 = st.columns([1,1,1])
    with col_logo2:
        st.image('logo_UY.png', width=180)

DB_FILE = "base_datos_puntos.csv"
COLUMNAS_ESTANDAR = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str)
    return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

df = cargar_datos()

# --- MENÚ LATERAL ---
st.sidebar.image('logo_UY.png', width=150) if os.path.exists('logo_UY.png') else None
st.sidebar.markdown("### 👤 SECCIÓN CLIENTES")
opcion_cliente = st.sidebar.radio("Ir a:", ["🔍 Mi Saldo de Puntos", "ℹ️ Información", "🎁 Catálogo"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 ACCESO RESTRINGIDO")
opcion_staff = st.sidebar.checkbox("Ingreso Staff Würth")

# --- LÓGICA DE CLIENTE ---
if not opcion_staff:
    if opcion_cliente == "🔍 Mi Saldo de Puntos":
        st.markdown("<h1 style='text-align: center; color: #333;'>¡Bienvenido!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Ingresa tu número de cliente para conocer tus beneficios.</p>", unsafe_allow_html=True)
        
        id_busqueda = st.text_input("", placeholder="Número de Cliente (ej: 123456)").strip()
        
        if id_busqueda:
            datos_cliente = df[df["ID_Cliente"] == id_busqueda]
            if not datos_cliente.empty:
                nombre = datos_cliente["Nombre_Cliente"].iloc[0]
                puntos_num = pd.to_numeric(datos_cliente["Puntos_Ganados"], errors='coerce').fillna(0)
                total = int(puntos_num.sum())
                
                st.markdown(f"<h2 style='text-align: center;'>Hola, {nombre} 👋</h2>", unsafe_allow_html=True)
                
                col_m1, col_m2, col_m3 = st.columns([1,2,1])
                with col_m2:
                    st.metric("Puntos Acumulados", f"{total}")
                
                with st.expander("📄 Ver detalle de mis facturas"):
                    st.table(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
                st.balloons()
            else:
                st.error("❌ El número de cliente no existe. Por favor, contacta a tu asesor comercial.")

    elif opcion_cliente == "ℹ️ Información":
        st.title("Programa de Puntos")
        st.markdown("""
        ### ¿Cómo sumar?
        Por cada **$100** en tus facturas, sumas **1 punto** automáticamente.
        
        ### ¿Cuándo canjear?
        Puedes realizar canjes en cualquier momento comunicándote con el Staff. Los puntos vencen a los 12 meses de la compra.
        """)

    elif opcion_cliente == "🎁 Catálogo":
        st.title("Premios Disponibles")
        st.info("Próximamente podrás ver el catálogo aquí mismo.")
        st.link_button("🌐 Visitar Würth Uruguay", "https://www.wurth.com.uy/")

# --- LÓGICA DE STAFF ---
else:
    st.markdown("<h2 style='color: #E60002;'>Acceso Administrativo</h2>", unsafe_allow_html=True)
    password = st.text_input("Clave de Seguridad", type="password")
    
    if password == "089020011":
        st.success("Verificado correctamente")
        
        tab_masiva, tab_manual, tab_base = st.tabs(["🚀 CARGA MASIVA", "✍️ MANUAL", "📂 BASE DATOS"])
        
        with tab_masiva:
            archivo = st.file_uploader("Subir Excel de BI", type=['xlsx'])
            if archivo:
                df_nuevo = pd.read_excel(archivo, dtype=str)
                # (Lógica de carga masiva que ya teníamos funcionando...)
                if all(c in df_nuevo.columns for c in ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra"]):
                    df_nuevo = df_nuevo.drop_duplicates(subset=['Nro_Factura'])
                    df_nuevo['Monto_Compra_Num'] = pd.to_numeric(df_nuevo['Monto_Compra'], errors='coerce').fillna(0)
                    df_nuevo['Puntos_Ganados'] = (df_nuevo['Monto_Compra_Num'] // 100).astype(int).astype(str)
                    df_nuevo['Monto_Compra'] = df_nuevo['Monto_Compra_Num'].astype(str)
                    df_nuevo['Fecha'] = str(date.today())
                    
                    facturas_en_base = df['Nro_Factura'].values
                    df_filtrado = df_nuevo[~df_nuevo['Nro_Factura'].isin(facturas_en_base)]
                    
                    if not df_filtrado.empty:
                        st.dataframe(df_filtrado[COLUMNAS_ESTANDAR])
                        if st.button("PROCESAR EXCEL"):
                            pd.concat([df, df_filtrado[COLUMNAS_ESTANDAR]], ignore_index=True).to_csv(DB_FILE, index=False)
                            st.success("¡Base actualizada!")
                            time.sleep(2)
                            st.rerun()
                    else: st.warning("No hay facturas nuevas.")

        with tab_manual:
            with st.form("man"):
                c1, c2 = st.columns(2)
                id_i = c1.text_input("ID Cliente")
                nom_i = c1.text_input("Nombre")
                fac_i = c2.text_input("Factura")
                mon_i = c2.number_input("Monto", min_value=0.0)
                if st.form_submit_button("GUARDAR"):
                    p = str(int(mon_i // 100))
                    nueva = pd.DataFrame([[id_i, nom_i, fac_i, str(mon_i), p, str(date.today())]], columns=COLUMNAS_ESTANDAR)
                    pd.concat([df, nueva], ignore_index=True).to_csv(DB_FILE, index=False)
                    st.rerun()

        with tab_base:
            st.dataframe(df)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Descargar Base Completa", buffer.getvalue(), "puntos.xlsx")
    elif password:
        st.error("Contraseña incorrecta")
