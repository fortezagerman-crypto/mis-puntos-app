import streamlit as st
import pandas as pd
from datetime import date
import os
import io

# 1. CONFIGURACIÓN DE PÁGINA Y METADATOS (Para vista previa en WhatsApp)
st.set_page_config(
    page_title="Puntos Würth",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo visual Rojo Würth
st.markdown("""
    <style>
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    </style>
    """, unsafe_allow_html=True)

# Mostrar Logo
if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. GESTIÓN DE BASE DE DATOS
DB_FILE = "base_datos_puntos.csv"

def cargar_datos():
    if os.path.exists(DB_FILE):
        # Mantenemos ID como texto para no perder ceros iniciales
        return pd.read_csv(DB_FILE, dtype={'ID_Cliente': str})
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

# --- SECCIÓN: REGISTRO STAFF ---
if opcion == "🏬 Registro Staff":
    st.subheader("Panel Administrativo")
    # Clave de acceso configurada
    password = st.text_input("Introduce la clave", type="password")
    
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_c = col1.text_input("ID Cliente")
            nom = col1.text_input("Nombre del Cliente")
            fac = col2.text_input("Número de Factura")
            mon = col2.number_input("Monto de Compra ($)", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR PUNTOS"):
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    nueva_fila = pd.DataFrame([[str(id_c), nom, fac, mon, puntos, date.today()]], columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    df_final.to_csv(DB_FILE, index=False)
                    st.success("✅ ¡Registro exitoso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Por favor, completa todos los campos.")
        
        st.divider()
        st.subheader("Gestión de Base de Datos")
        
        if not df.empty:
            # Botón de Descarga Excel Legible
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Puntos_Wurth')
            
            st.download_button(
                label="📥 DESCARGAR EXCEL DE PUNTOS",
                data=buffer.getvalue(),
                file_name=f"puntos_wurth_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Botón para eliminar error
            if st.button("🗑️ ELIMINAR ÚLTIMO REGISTRO (Corrección)"):
                df_nueva = df.drop(df.index[-1])
                df_nueva.to_csv(DB_FILE, index=False)
                st.warning("Último registro borrado.")
                st.rerun()

            st.write("### Vista previa de registros")
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            
    elif password != "":
        st.error("Clave incorrecta")

# --- SECCIÓN: CONSULTA CLIENTE ---
else:
    st.subheader("Consulta tus puntos")
    id_busqueda = st.text_input("Ingresa tu número de cliente", placeholder="Ej: 12345678")
    
    if id_busqueda:
        datos_cliente = df[df["ID_Cliente"].astype(str) == str(id_busqueda).strip()]
        
        if not datos_cliente.empty:
            nombre = datos_cliente["Nombre_Cliente"].iloc[0]
            total = int(datos_cliente["Puntos_Ganados"].sum())
            
            st.markdown(f"## ¡Hola, **{nombre}**!")
            st.metric("Tu saldo actual es de:", f"{total} Puntos")
            
            with st.expander("Ver historial de facturas"):
                st.table(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
            
            st.balloons()
        else:
            st.warning("No se encontró el ID. Consulta con tu vendedor.")
