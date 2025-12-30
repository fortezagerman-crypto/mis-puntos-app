import streamlit as st
import pandas as pd
from datetime import date
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Puntos Würth", page_icon="logo_UY.png")

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CARGA DE DATOS
# Priorizamos el archivo CSV que es donde se guardarán los nuevos registros
def cargar_datos():
    if os.path.exists('base_datos_puntos.csv'):
        return pd.read_csv('base_datos_puntos.csv')
    # Si no existe, creamos uno vacío con los encabezados correctos
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Acceso Restringido")
    # Tu clave de producto
    if st.text_input("Introduce la clave", type="password") == "089020011":
        st.success("Acceso concedido")
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_c = col1.text_input("ID Cliente")
            nom = col1.text_input("Nombre")
            fac = col2.text_input("Nro Factura")
            mon = col2.number_input("Monto ($)", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR"):
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    nueva_fila = pd.DataFrame([[id_c, nom, fac, mon, puntos, date.today()]], columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    # GUARDADO LOCAL (Seguro, no depende de permisos de Google)
                    df_final.to_csv("base_datos_puntos.csv", index=False)
                    
                    st.success(f"✅ ¡Puntos cargados! {nom} sumó {puntos} pts.")
                    st.balloons()
                    st.info("Nota: Los datos se guardaron en el archivo del sistema.")
                else:
                    st.error("Completa todos los campos")
    elif st.session_state.get('password'):
        st.error("Clave incorrecta")

else:
    st.subheader("Consulta de Puntos")
    busqueda = st.text_input("Ingresa tu ID de Cliente")
    if busqueda:
        # Buscamos en los datos cargados
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        if not datos.empty:
            total = datos["Puntos_Ganados"].sum()
            st.metric(f"Hola {datos['Nombre_Cliente'].iloc[0]}", f"{total} Puntos")
            with st.expander("Ver historial"):
                st.table(datos[["Fecha", "Nro_Factura", "Puntos_Ganados"]])
        else:
            st.warning("ID no encontrado")
