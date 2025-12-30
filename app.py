
import streamlit as st
import pandas as pd
import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Puntos Würth", layout="centered")

# Función para cargar datos
def cargar_datos():
    if os.path.exists('base_datos_puntos.csv'):
        return pd.read_csv('base_datos_puntos.csv')
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("🏆 Sistema de Fidelidad")

# Menú lateral para separar Vendedor de Cliente
opcion = st.sidebar.selectbox("¿Quién eres?", ["Soy Cliente", "Soy Vendedor"])

if opcion == "Soy Vendedor":
    st.header("Sección Administrativa")
    with st.form("registro"):
        id_c = st.text_input("ID Cliente")
        nom = st.text_input("Nombre")
        fac = st.text_input("Nro Factura")
        mon = st.number_input("Monto ($)", min_value=0.0)
        enviar = st.form_submit_button("Registrar Puntos")
        
        if enviar:
            puntos = int(mon // 100)
            nueva_fila = pd.DataFrame([[id_c, nom, fac, mon, puntos, datetime.date.today()]], 
                                     columns=df.columns)
            df = pd.concat([df, nueva_fila], ignore_index=True)
            df.to_csv('base_datos_puntos.csv', index=False)
            st.success(f"¡Registrado! {nom} sumó {puntos} puntos.")

else:
    st.header("Consulta tus Puntos")
    busqueda = st.text_input("Ingresa tu ID de Cliente")
    if busqueda:
        datos = df[df["ID_Cliente"] == busqueda]
        if not datos.empty:
            st.metric("Tus Puntos Totales", int(datos["Puntos_Ganados"].sum()))
            st.subheader("Tus últimas facturas")
            st.table(datos[["Nro_Factura", "Puntos_Ganados", "Fecha"]].tail(5))
        else:
            st.error("No se encontró ese ID.")
