import streamlit as st
import pandas as pd
from datetime import date
import os
import io
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Puntos Würth",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

DB_FILE = "base_datos_puntos.csv"
COLUMNAS_ESTANDAR = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str)
    return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

df = cargar_datos()

# --- MENÚ LATERAL ---
st.sidebar.header("MENÚ PRINCIPAL")
opcion = st.sidebar.radio("Seleccione una opción:", ["🔍 Consultar Puntos", "ℹ️ ¿De qué se trata?", "🎁 Ver Beneficios", "🏬 Registro Staff"])

# --- SECCIÓN: CONSULTAR PUNTOS ---
if opcion == "🔍 Consultar Puntos":
    st.subheader("Consulta tus puntos acumulados")
    id_busqueda = st.text_input("Ingresa tu número de cliente").strip()
    
    if id_busqueda:
        datos_cliente = df[df["ID_Cliente"] == id_busqueda]
        if not datos_cliente.empty:
            nombre = datos_cliente["Nombre_Cliente"].iloc[0]
            puntos_num = pd.to_numeric(datos_cliente["Puntos_Ganados"], errors='coerce').fillna(0)
            total = int(puntos_num.sum())
            st.markdown(f"## ¡Hola, **{nombre}**!")
            st.metric("Tu saldo actual es de:", f"{total} Puntos")
            with st.expander("Ver historial de facturas"):
                st.table(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
            st.balloons()
        else:
            st.warning("No se encontró el ID.")

# --- SECCIÓN: REGISTRO STAFF ---
elif opcion == "🏬 Registro Staff":
    st.subheader("Panel Administrativo")
    password = st.text_input("Introduce la clave de seguridad", type="password")
    
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        
        # --- BLOQUE 1: CARGA MANUAL ---
        with st.expander("➕ Carga Manual (Individual)"):
            with st.form("registro", clear_on_submit=True):
                col1, col2 = st.columns(2)
                id_c = col1.text_input("ID Cliente").strip()
                nom = col1.text_input("Nombre del Cliente").strip()
                fac = col2.text_input("Número de Factura").strip()
                mon = col2.number_input("Monto de Compra ($)", min_value=0.0)
                if st.form_submit_button("REGISTRAR PUNTOS"):
                    if id_c and nom and fac and mon > 0:
                        if fac in df['Nro_Factura'].values:
                            st.error(f"Error: La factura {fac} ya existe.")
                        else:
                            puntos = str(int(mon // 100))
                            nueva_fila = pd.DataFrame([[id_c, nom, fac, str(mon), puntos, str(date.today())]], columns=COLUMNAS_ESTANDAR)
                            df_final = pd.concat([df, nueva_fila], ignore_index=True)
                            df_final.to_csv(DB_FILE, index=False)
                            st.success("✅ ¡Puntos registrados!")
                            time.sleep(1)
                            st.rerun()

        # --- BLOQUE 2: CARGA MASIVA ---
