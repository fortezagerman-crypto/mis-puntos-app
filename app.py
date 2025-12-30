import streamlit as st
import pandas as pd
import datetime
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Sistema de Puntos Würth", page_icon="🏆", layout="centered")

st.markdown("""
    <style>
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=200)

def cargar_datos():
    if os.path.exists('base_datos_puntos.csv'):
        return pd.read_csv('base_datos_puntos.csv', dtype={'ID_Cliente': str})
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")

opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["🔍 Consultar mis Puntos", "🏬 Registro Staff (Interno)"])

# --- LÓGICA DE SEGURIDAD PARA EL STAFF ---
if opcion == "🏬 Registro Staff (Interno)":
    st.subheader("Acceso Restringido")
    
    # Definimos una clave sencilla (puedes cambiarla aquí abajo)
    CLAVE_CORRECTA = "Wurth2025" 
    
    password = st.text_input("Introduce la clave de vendedor", type="password")
    
    if password == CLAVE_CORRECTA:
        st.success("Acceso concedido")
        st.subheader("Carga de Compras")
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
                    nueva_fila = pd.DataFrame([[str(id_c), nom, fac, mon, puntos, datetime.date.today()]], columns=df.columns)
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                    df.to_csv('base_datos_puntos.csv', index=False)
                    st.success(f"✅ ¡Puntos cargados! {nom} ha sumado {puntos} pts.")
                else:
                    st.error("Completa todos los campos.")
    elif password != "":
        st.error("❌ Clave incorrecta. Contacta al administrador.")

# --- VISTA DEL CLIENTE ---
else:
    st.subheader("¡Bienvenido a tu cuenta de puntos!")
    busqueda = st.text_input("Ingresa tu ID de Cliente para consultar")
    
    if busqueda:
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda)]
        if not datos.empty:
            nombre_cliente = datos["Nombre_Cliente"].iloc[0]
            total_puntos = int(datos["Puntos_Ganados"].sum())
            st.markdown(f"### Hola, **{nombre_cliente}**")
            st.metric("Tu saldo actual es de:", f"{total_puntos} Puntos")
            with st.expander("Ver detalle de mis facturas"):
                st.table(datos[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
        else:
            st.warning("ID no encontrado.")
