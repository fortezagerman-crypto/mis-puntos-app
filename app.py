import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Puntos Würth", page_icon="logo_UY.png", layout="centered")

st.markdown("""
    <style>
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Leemos la hoja completa
    return conn.read(ttl=0)

try:
    df = cargar_datos()
except:
    st.error("No se pudo leer la hoja. Revisa el link en Secrets.")
    st.stop()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["🔍 Consultar", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Acceso Restringido")
    CLAVE_CORRECTA = "089020011"
    password = st.text_input("Clave de vendedor", type="password")
    
    if password.strip() == CLAVE_CORRECTA:
        st.success("Acceso concedido")
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_c = col1.text_input("ID Cliente")
            nom = col1.text_input("Nombre")
            fac = col2.text_input("Nro Factura")
            mon = col2.number_input("Monto ($)", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR PUNTOS"):
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    nueva_fila = pd.DataFrame([{
                        "ID_Cliente": str(id_c),
                        "Nombre_Cliente": nom,
                        "Nro_Factura": str(fac),
                        "Monto_Compra": float(mon),
                        "Puntos_Ganados": int(puntos),
                        "Fecha": str(datetime.date.today())
                    }])
                    
                    # MÉTODO DE ACTUALIZACIÓN REFORZADO
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(data=df_final)
                    
                    st.success("✅ ¡Guardado en Google Sheets!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Faltan datos")
    elif password != "":
        st.error("Clave incorrecta")

else:
    st.subheader("Consulta de Puntos")
    busqueda = st.text_input("ID Cliente")
    if busqueda:
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        if not datos.empty:
            st.metric("Puntos Totales", int(datos["Puntos_Ganados"].sum()))
            st.table(datos[["Fecha", "Nro_Factura", "Puntos_Ganados"]])
        else:
            st.warning("No encontrado")
