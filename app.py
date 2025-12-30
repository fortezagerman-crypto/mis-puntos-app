import streamlit as st
import pandas as pd
from datetime import date
import os
import io

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Puntos Würth", page_icon="logo_UY.png")

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CARGA DE DATOS
def cargar_datos():
    if os.path.exists('base_datos_puntos.csv'):
        # Forzamos que el ID se lea como texto para no perder los ceros a la izquierda
        return pd.read_csv('base_datos_puntos.csv', dtype={'ID_Cliente': str})
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Panel Administrativo")
    if st.text_input("Introduce la clave", type="password") == "089020011":
        st.success("Acceso concedido")
        
        # --- FORMULARIO DE REGISTRO ---
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_c = col1.text_input("ID Cliente")
            nom = col1.text_input("Nombre del Cliente")
            fac = col2.text_input("Número de Factura")
            mon = col2.number_input("Monto de Compra ($)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("REGISTRAR PUNTOS"):
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100)
                    nueva_fila = pd.DataFrame([[str(id_c), nom, fac, mon, puntos, date.today()]], columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    df_final.to_csv("base_datos_puntos.csv", index=False)
                    st.success(f"✅ ¡Puntos cargados con éxito!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Por favor, completa todos los campos.")

        # --- GESTIÓN DE DATOS ---
        st.divider()
        st.subheader("Gestión de Base de Datos")
        
        col_desc, col_del = st.columns(2)

        # 1. Botón de Descarga Excel Legible
        with col_desc:
            if not df.empty:
                buffer = io.BytesIO()
                # Usamos xlsxwriter para formato Excel genuino
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Puntos_Wurth')
                
                st.download_button(
                    label="📥 DESCARGAR EXCEL",
                    data=buffer.getvalue(),
                    file_name=f"Base_Puntos_Wurth_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No hay datos para descargar.")

        # 2. Botón para eliminar error
        with col_del:
            if not df.empty:
                if st.button("🗑️ ELIMINAR ÚLTIMO REGISTRO"):
                    df_reducido = df
