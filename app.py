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

# --- 2. CARGA DE CSS EXTERNO ---
def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# --- 3. DICCIONARIO DE FONDOS ---
fondos = {
    "🔍 Consultar Puntos": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?q=80&w=2070",
    "ℹ️ ¿De qué se trata?": "https://eur05.safelinks.protection.outlook.com/?url=https%3A%2F%2Fviewer.ipaper.io%2Fwurth-uruguay%2Fcupones%2Fplataforma-de-puntos%2F&data=05%7C02%7CGerman.Forteza%40wurth.com.uy%7C1bc915be0fb04928d6b808de54fabc00%7C45de56eae50543a5bd604957c8afc438%7C0%7C0%7C639041633325855187%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=63N7zUxa09AL8YTHk1JhHHV44WwEtZIh4eEyIzwlriw%3D&reserved=0",
    "🎁 Ver Beneficios": "https://images.unsplash.com/photo-1530124560677-bbfda2f97a1d?q=80&w=2070",
    "Staff": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070"
}

# --- 4. CARGA DE LOGO Y DATOS ---
if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

DB_FILE = "base_datos_puntos.csv"
COLUMNAS_ESTANDAR = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str)
    return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

df = cargar_datos()

# --- 5. MENÚ ---
st.sidebar.markdown("# 🏆 CLIENTES")
opcion_cliente = st.sidebar.radio("Menú de Usuario:", ["🔍 Consultar Puntos", "ℹ️ ¿De qué se trata?", "🎁 Ver Beneficios"])
st.sidebar.markdown("---") 
st.sidebar.markdown("# ⚙️ ADMINISTRACIÓN")
opcion_staff = st.sidebar.checkbox("Acceder como Staff")

# --- APLICAR FONDO DINÁMICO ---
opcion_actual = "Staff" if opcion_staff else opcion_cliente
url_f = fondos.get(opcion_actual, fondos["🔍 Consultar Puntos"])

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{url_f}") !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
        background-blend-mode: overlay !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. LÓGICA CLIENTE ---
if not opcion_staff:
    if opcion_cliente == "🔍 Consultar Puntos":
        st.subheader("Consulta tus puntos acumulados")
        id_busqueda = st.text_input("Ingresa tu número de cliente").strip()
        if id_busqueda:
            datos_cliente = df[df["ID_Cliente"] == id_busqueda]
            if not datos_cliente.empty:
                nombre = datos_cliente["Nombre_Cliente"].iloc[0]
                total = int(pd.to_numeric(datos_cliente["Puntos_Ganados"], errors='coerce').fillna(0).sum())
                st.markdown(f"## ¡Hola, **{nombre}**!")
                st.metric("Tu saldo actual es de:", f"{total} Puntos")
                with st.expander("Ver historial de facturas"):
                    st.table(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
            else:
                st.warning("No se encontró el ID.")

    elif opcion_cliente == "ℹ️ ¿De qué se trata?":
        st.subheader("Información del Programa")
        st.write("Bienvenido al sistema de beneficios de Würth Uruguay.")
        # BOTÓN A REGLAMENTO EXTERNO
        URL_REGLAMENTO = "https://www.wurth.com.uy/reglamento_puntos.pdf" 
        st.link_button("📖 LEER REGLAMENTO Y CONDICIONES", URL_REGLAMENTO)

    elif opcion_cliente == "🎁 Ver Beneficios":
        st.subheader("Beneficios y Premios")
        # BOTÓN A CATÁLOGO EXTERNO
        URL_CATALOGO = "https://www.wurth.com.uy/catalogo_premios.pdf" 
        st.link_button("🚀 ABRIR CATÁLOGO DE PREMIOS (PDF)", URL_CATALOGO)

# --- 7. LÓGICA STAFF ---
else:
    st.subheader("🔐 Panel Administrativo")
    password = st.text_input("Clave", type="password")
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        t1, t2, t3 = st.tabs(["📊 Carga Masiva", "➕ Manual", "🗑️ Gestión"])
        
        with t1:
            archivo = st.file_uploader("Subir .xlsx", type=['xlsx'], key="up")
            if archivo:
                try:
                    df_n = pd.read_excel(archivo, dtype=str)
                    if all(col in df_n.columns for col in ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra"]):
                        df_n = df_n.drop_duplicates(subset=['Nro_Factura'])
                        df_n['Puntos_Ganados'] = (pd.to_numeric(df_n['Monto_Compra'], errors='coerce').fillna(0) // 100).astype(int).astype(str)
                        df_n['Fecha'] = str(date.today())
                        df_f = df_n[~df_n['Nro_Factura'].isin(df['Nro_Factura'].values)]
                        if not df_f.empty:
                            st.dataframe(df_f[COLUMNAS_ESTANDAR].head())
                            if st.button("CONFIRMAR"):
                                pd.concat([df, df_f[COLUMNAS_ESTANDAR]], ignore_index=True).to_csv(DB_FILE, index=False)
                                st.success("Carga exitosa.")
                                time.sleep(1)
                                st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        with t2:
            with st.form("manual", clear_on_submit=True):
                c1, c2 = st.columns(2)
                id_i = c1.text_input("ID Cliente")
                nom_i = c1.text_input("Nombre")
                fac_i = c2.text_input("Factura")
                mon_i = c2.number_input("Monto", min_value=0.0)
                if st.form_submit_button("REGISTRAR"):
                    p = str(int(mon_i // 100))
                    nueva = pd.DataFrame([[id_i, nom_i, fac_i, str(mon_i), p, str(date.today())]], columns=COLUMNAS_ESTANDAR)
                    pd.concat([df, nueva], ignore_index=True).to_csv(DB_FILE, index=False)
                    st.rerun()

        with t3:
            if not df.empty:
                st.dataframe(df)
                idx = st.number_input("Índice a borrar", min_value=0, max_value=len(df)-1, step=1)
                if st.button("ELIMINAR"):
                    df.drop(df.index[idx]).to_csv(DB_FILE, index=False)
                    st.rerun()

        st.divider()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 DESCARGAR BASE", buffer.getvalue(), "base_puntos.xlsx")
