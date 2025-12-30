import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os

# 1. CONFIGURACIÓN VISUAL E ICONO
st.set_page_config(
    page_title="Puntos Würth", 
    page_icon="logo_UY.png", 
    layout="centered"
)

# Estilo Rojo Würth
st.markdown("""
    <style>
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; width: 100%; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CONEXIÓN A GOOGLE SHEETS
# Esto usa el link que pegaste en los Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 asegura que siempre lea los datos más recientes de Google Sheets
    return conn.read(ttl=0)

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["🔍 Consultar mis Puntos", "🏬 Registro Staff (Interno)"])

if opcion == "🏬 Registro Staff (Interno)":
    st.subheader("Acceso Restringido")
    CLAVE_CORRECTA = "089020011" # <--- CAMBIA ESTO POR TU CLAVE
    
    password = st.text_input("Introduce la clave de vendedor", type="password")
    
    if password == CLAVE_CORRECTA:
        st.success("Acceso concedido")
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                id_c = st.text_input("ID o DNI Cliente")
                nom = st.text_input("Nombre Completo")
            with col2:
                fac = st.text_input("Número de Factura")
                mon = st.number_input("Monto de Compra ($)", min_value=0.0)
            
            btn_enviar = st.form_submit_button("REGISTRAR PUNTOS")
            
            if btn_enviar:
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    # Preparamos la nueva fila
                    nueva_fila = pd.DataFrame([[str(id_c), nom, fac, mon, puntos, str(datetime.date.today())]], 
                                             columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])
                    
                    # Combinamos con lo que ya existe en Google Sheets
                    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    # ENVIAR A GOOGLE SHEETS
                    conn.update(data=df_actualizado)
                    st.success(f"✅ ¡Registrado en Google Sheets! {nom} sumó {puntos} pts.")
                    st.balloons()
                else:
                    st.error("Por favor completa todos los campos.")
    elif password != "":
        st.error("Clave incorrecta")

else:
    st.subheader("¡Bienvenido!")
    busqueda = st.text_input("Ingresa tu ID de Cliente")
    if busqueda:
        # Buscamos en el DataFrame que viene de Google Sheets
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda)]
        if not datos.empty:
            total_puntos = int(datos["Puntos_Ganados"].sum())
            st.markdown(f"### Hola, **{datos['Nombre_Cliente'].iloc[0]}**")
            st.metric("Tu saldo actual:", f"{total_puntos} Puntos")
            with st.expander("Ver historial de puntos"):
                st.table(datos[["Fecha", "Nro_Factura", "Puntos_Ganados"]])
        else:
            st.warning("ID no encontrado en nuestra base de datos.")
