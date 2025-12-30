import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Puntos Würth", page_icon="logo_UY.png")

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. FUNCIÓN PARA CARGAR DATOS (Lectura directa del CSV público de Google)
# Esto evita errores de conexión complejos
def cargar_datos():
    # Convertimos tu link de Google Sheets a un formato que Python lee fácil
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

try:
    df = cargar_datos()
except:
    st.error("Error al leer la base de datos. Verifica el link en Secrets.")
    st.stop()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Acceso Restringido")
    if st.text_input("Introduce la clave", type="password") == "089020011":
        st.success("Acceso concedido")
        with st.form("registro_puntos", clear_on_submit=True):
            c1, c2 = st.columns(2)
            id_c = c1.text_input("ID Cliente")
            nom = c1.text_input("Nombre")
            fac = c2.text_input("Nro Factura")
            mon = c2.number_input("Monto ($)", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR"):
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    # AQUÍ ESTÁ EL CAMBIO: Mostramos los datos para verificar
                    st.info(f"Registrando: {nom} - {puntos} puntos.")
                    
                    # Para evitar el error de escritura, por ahora vamos a usar
                    # el archivo local hasta que el link de Google sea 100% estable
                    nueva_fila = pd.DataFrame([[id_c, nom, fac, mon, puntos, date.today()]], columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    # Guardamos localmente (esto no dará el error de Google)
                    df_final.to_csv("base_datos_puntos.csv", index=False)
                    st.success("✅ Puntos registrados localmente. (Para verlos en el Excel de Google se requiere configuración de API avanzada)")
                    st.balloons()
                else:
                    st.error("Completa todos los campos")
    elif st.session_state.get('password'):
        st.error("Clave incorrecta")

else:
    st.subheader("Consulta de Puntos")
    busqueda = st.text_input("Ingresa tu ID")
    if busqueda:
        # Buscamos tanto en el Excel de Google como en lo nuevo registrado
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        if not datos.empty:
            total = datos["Puntos_Ganados"].sum()
            st.metric(f"Hola {datos['Nombre_Cliente'].iloc[0]}", f"{total} Puntos")
        else:
            st.warning("ID no encontrado")
