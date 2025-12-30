import streamlit as st
import pandas as pd
from datetime import date
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Puntos Würth", page_icon="logo_UY.png")

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CARGA DE DATOS
def cargar_datos():
    if os.path.exists('base_datos_puntos.csv'):
        return pd.read_csv('base_datos_puntos.csv')
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Acceso Restringido")
    # Tu clave: 089020011
    password = st.text_input("Introduce la clave", type="password")
    
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        
        # --- SECCIÓN DE CARGA ---
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
                    df_final.to_csv("base_datos_puntos.csv", index=False)
                    st.success(f"✅ ¡Puntos cargados!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Completa todos los campos")
        
        # --- SECCIÓN DE DESCARGA (EXCEL) ---
        st.divider()
        st.subheader("Administración de Datos")
        st.info("Desde aquí puedes descargar la base de datos completa en formato Excel.")
        
        # Convertimos el CSV a Excel en memoria para la descarga
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Puntos_Acumulados')
        
        st.download_button(
            label="📥 DESCARGAR EXCEL DE PUNTOS",
            data=buffer.getvalue(),
            file_name=f"puntos_wurth_{date.today()}.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        # Vista previa para el staff
        with st.expander("Ver tabla completa de registros"):
            st.dataframe(df.sort_values(by="Fecha", ascending=False))

    elif password != "":
        st.error("Clave incorrecta")

else:
    # (El código de consulta de clientes sigue igual...)
    st.subheader("Consulta tus puntos")
    busqueda = st.text_input("Ingresa tu ID de Cliente")
    if busqueda:
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        if not datos.empty:
            total = datos["Puntos_Ganados"].sum()
            st.metric(f"Hola {datos['Nombre_Cliente'].iloc[0]}", f"{total} Puntos")
        else:
            st.warning("ID no encontrado")
