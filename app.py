import streamlit st
import pandas as pd
from datetime import date
import os
import io
import time

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(
    page_title="Puntos Würth",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- LÓGICA DE FONDOS DINÁMICOS Y DISEÑO ---
# Definimos las imágenes para cada sección
fondos = {
    "🔍 Consultar Puntos": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?q=80&w=2070",
    "ℹ️ ¿De qué se trata?": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=2070",
    "🎁 Ver Beneficios": "https://images.unsplash.com/photo-1530124560677-bbfda2f97a1d?q=80&w=2070",
    "Staff": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070"
}

# --- ESTILO VISUAL CSS (Incluye opacidad y bloqueo de menús) ---
def aplicar_estilos(url_imagen):
    st.markdown(f"""
        <style>
        /* Ocultar menús de sistema para seguridad */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        
        /* Fondo con imagen y opacidad mediante overlay */
        .stApp {{
            background: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), 
                        url("{url_imagen}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* Contenedores con efecto cristal para legibilidad */
        [data-testid="stVerticalBlock"] > div > div {{
            background-color: rgba(255, 255, 255, 0.6);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(5px);
        }}

        /* Tipografía y botones */
        [data-testid="stSidebarNav"] span {{ font-size: 18px !important; font-weight: 500; }}
        
        .stButton>button {{ 
            background-color: #E60002; 
            color: white; 
            border-radius: 5px; 
            width: 100%; 
            font-weight: bold; 
            border: none;
        }}

        .stMetric {{ 
            background-color: rgba(240, 242, 246, 0.9); 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 5px solid #E60002; 
        }}
        </style>
        """, unsafe_allow_html=True)

# --- BASE DE DATOS Y LOGO ---
if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

DB_FILE = "base_datos_puntos.csv"
COLUMNAS_ESTANDAR = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str)
    return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

df = cargar_datos()

# --- MENÚ LATERAL ---
st.sidebar.markdown("# 🏆 CLIENTES")
opcion_cliente = st.sidebar.radio("Menú de Usuario:", 
    ["🔍 Consultar Puntos", "ℹ️ ¿De qué se trata?", "🎁 Ver Beneficios"])

st.sidebar.markdown("---") 

st.sidebar.markdown("# ⚙️ ADMINISTRACIÓN")
opcion_staff = st.sidebar.checkbox("Acceder como Staff")

# Aplicar el fondo dinámico basado en la selección
url_actual = fondos["Staff"] if opcion_staff else fondos.get(opcion_cliente)
aplicar_estilos(url_actual)

# --- LÓGICA DE NAVEGACIÓN ---

if not opcion_staff:
    if opcion_cliente == "🔍 Consultar Puntos":
        st.subheader("Consulta tus puntos acumulados")
        id_busqueda = st.text_input("Ingresa tu número de cliente").strip()
        
        if id_busqueda:
            datos_cliente = df[df["ID_Cliente"] == id_busqueda]
            if not datos_cliente.empty:
                nombre = datos_cliente["Nombre_Cliente"].iloc[0]
                puntos_num = pd.to_numeric(datos_cliente["Puntos_Ganados"], errors='coerce').fillna(0)
                total = int(puntos_num.sum())
                st.markdown(f"## ¡Hola, **{nombre}**!")
                st.metric("Tu saldo actual es de:", f"{total} Puntos")
                with st.expander("Ver historial de facturas"):
                    st.table(datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False))
                st.balloons()
            else:
                st.warning("No se encontró el ID. Por favor, verifica el número.")

    elif opcion_cliente == "ℹ️ ¿De qué se trata?":
        st.subheader("Información del Programa")
        st.write("Bienvenido al programa de fidelidad de Würth Uruguay.")
        st.markdown("""
        * Por cada **$100** en compras, sumas **1 punto**.
        * Los puntos tienen vigencia de 1 año.
        * Canjea tus puntos por herramientas y premios exclusivos.
        """)
        st.link_button("📖 LEER REGLAMENTO COMPLETO", "https://github.com/wurth-fidelidad-uy/mis-puntos-app/blob/main/README.md")

    elif opcion_cliente == "🎁 Ver Beneficios":
        st.subheader("Beneficios y Premios")
        st.write("Descubre todo lo que puedes canjear con tus puntos acumulados.")
        # ESTE BOTÓN ABRE EL PDF EN PESTAÑA NUEVA
        URL_PDF_CATALOGO = "https://www.wurth.com.uy/catalogo_premios.pdf" # Reemplazar por tu link real
        st.link_button("🚀 ABRIR CATÁLOGO DE BENEFICIOS (PDF)", URL_PDF_CATALOGO)

else:
    st.subheader("🔐 Panel Administrativo - Staff")
    password = st.text_input("Introduce la clave de seguridad", type="password")
    
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        tab1, tab2, tab3 = st.tabs(["📊 Carga Masiva", "➕ Carga Manual", "🗑️ Gestionar Base"])
        
        with tab1:
            st.info("Sube el reporte de BI en formato .xlsx")
            archivo_excel = st.file_uploader("Seleccionar archivo", type=['xlsx'], key="bi_uploader")
            if archivo_excel:
                try:
                    df_nuevo = pd.read_excel(archivo_excel, dtype=str)
                    columnas_req = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra"]
                    if all(col in df_nuevo.columns for col in columnas_req):
                        df_nuevo = df_nuevo.drop_duplicates(subset=['Nro_Factura'])
                        df_nuevo['Monto_Compra_Num'] = pd.to_numeric(df_nuevo['Monto_Compra'], errors='coerce').fillna(0)
                        df_nuevo['Puntos_Ganados'] = (df_nuevo['Monto_Compra_Num'] // 100).astype(int).astype(str)
                        df_nuevo['Monto_Compra'] = df_nuevo['Monto_Compra_Num'].astype(str)
                        df_nuevo['Fecha'] = str(date.today())
                        
                        facturas_en_base = df['Nro_Factura'].values
                        df_filtrado = df_nuevo[~df_nuevo['Nro_Factura'].isin(facturas_en_base)]
                        
                        if not df_filtrado.empty:
                            st.dataframe(df_filtrado[COLUMNAS_ESTANDAR].head())
                            if st.button("CONFIRMAR CARGA"):
                                df_final = pd.concat([df, df_filtrado[COLUMNAS_ESTANDAR]], ignore_index=True)
                                df_final.to_csv(DB_FILE, index=False)
                                st.success("✅ Carga masiva exitosa.")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.warning("No hay datos nuevos.")
                except Exception as e:
                    st.error(f"Error: {e}")

        with tab2:
            with st.form("registro_man", clear_on_submit=True):
                col1, col2 = st.columns(2)
                id_c = col1.text_input("ID Cliente")
                nom = col1.text_input("Nombre")
                fac = col2.text_input("Nro Factura")
                mon = col2.number_input("Monto ($)", min_value=0.0)
                if st.form_submit_button("REGISTRAR"):
                    if id_c and nom and fac and mon > 0:
                        if fac in df['Nro_Factura'].values:
                            st.error("Factura ya existe.")
                        else:
                            puntos = str(int(mon // 100))
                            nueva_fila = pd.DataFrame([[id_c, nom, fac, str(mon), puntos, str(date.today())]], columns=COLUMNAS_ESTANDAR)
                            pd.concat([df, nueva_fila], ignore_index=True).to_csv(DB_FILE, index=False)
                            st.success("Registrado.")
                            time.sleep(1)
                            st.rerun()

        with tab3:
            if not df.empty:
                st.dataframe(df)
                idx = st.number_input("Índice a borrar", min_value=0, max_value=len(df)-1, step=1)
                if st.button("ELIMINAR"):
                    df.drop(df.index[idx]).to_csv(DB_FILE, index=False)
                    st.rerun()
            else:
                st.info("Base vacía.")

        st.divider()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 DESCARGAR EXCEL COMPLETO", buffer.getvalue(), f"base_puntos.xlsx")
