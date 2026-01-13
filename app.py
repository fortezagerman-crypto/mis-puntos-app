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

# --- SEGURIDAD Y ESTILO VISUAL ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stButton>button { 
        background-color: #E60002; 
        color: white; 
        border-radius: 5px; 
        width: 100%; 
        font-weight: bold; 
    }
    .stMetric { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #E60002; 
    }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

DB_FILE = "base_datos_puntos.csv"

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'ID_Cliente': str, 'Nro_Factura': str})
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

# --- MENÚ LATERAL ---
st.sidebar.header("MENÚ PRINCIPAL")
opcion = st.sidebar.radio("Seleccione una opción:", 
    ["🔍 Consultar Puntos", "ℹ️ ¿De qué se trata?", "🎁 Ver Beneficios", "🏬 Registro Staff"])

# --- SECCIÓN: CONSULTAR PUNTOS ---
if opcion == "🔍 Consultar Puntos":
    st.subheader("Consulta tus puntos acumulados")
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

# --- SECCIÓN: ¿DE QUÉ SE TRATA? ---
elif opcion == "ℹ️ ¿De qué se trata?":
    st.subheader("Información del Programa")
    st.write("Consulta las bases y condiciones de nuestro programa de fidelidad.")
    url_readme = "https://github.com/wurth-fidelidad-uy/mis-puntos-app/blob/main/README.md"
    st.link_button("📖 LEER REGLAMENTO COMPLETO", url_readme)
    st.markdown("---\n**Resumen rápido:**\n* Acumulas **1 punto por cada $100**.\n* Los puntos se canjean por premios exclusivos.")

# --- SECCIÓN: VER BENEFICIOS ---
elif opcion == "🎁 Ver Beneficios":
    st.subheader("Beneficios y Premios")
    enlace_premios = "https://www.wurth.com.uy/" 
    st.link_button("🚀 VER CATÁLOGO DE PREMIOS", enlace_premios)

# --- SECCIÓN: REGISTRO STAFF ---
elif opcion == "🏬 Registro Staff":
    st.subheader("Panel Administrativo")
    password = st.text_input("Introduce la clave de seguridad", type="password")
    
    if password.strip() == "089020011":
        st.success("Acceso concedido")
        
        # 1. CARGA MANUAL
        st.markdown("### 1. Carga Manual")
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_c = col1.text_input("ID Cliente")
            nom = col1.text_input("Nombre del Cliente")
            fac = col2.text_input("Número de Factura")
            mon = col2.number_input("Monto de Compra ($)", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR PUNTOS"):
                if id_c and nom and fac and mon > 0:
                    if str(fac) in df['Nro_Factura'].astype(str).values:
                        st.error(f"La factura {fac} ya fue registrada anteriormente.")
                    else:
                        puntos = int(mon // 100)
                        nueva_fila = pd.DataFrame([[str(id_c), nom, str(fac), mon, puntos, date.today()]], columns=df.columns)
                        df_final = pd.concat([df, nueva_fila], ignore_index=True)
                        df_final.to_csv(DB_FILE, index=False)
                        st.success("✅ ¡Puntos registrados correctamente!")
                        time.sleep(1)
                        st.rerun()

        st.divider()

        # 2. CARGA MASIVA
        st.markdown("### 2. Carga Masiva desde Excel")
        st.info("Sube un archivo **.xlsx** con las columnas: ID_Cliente, Nombre_Cliente, Nro_Factura, Monto_Compra")
        
        archivo_excel = st.file_uploader("Arrastra aquí tu reporte de BI", type=['xlsx'], key="uploader_masivo")
        
        if archivo_excel is not None:
            try:
                df_nuevo = pd.read_excel(archivo_excel)
                columnas_req = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra"]
                
                if all(col in df_nuevo.columns for col in columnas_req):
                    # Formatear datos nuevos
                    df_nuevo['ID_Cliente'] = df_nuevo['ID_Cliente'].astype(str)
                    df_nuevo['Nro_Factura'] = df_nuevo['Nro_Factura'].astype(str)
                    df_nuevo['Puntos_Ganados'] = (df_nuevo['Monto_Compra'] // 100).astype(int)
                    df_nuevo['Fecha'] = date.today()
                    
                    # FILTRO ANTI-DUPLICADOS
                    facturas_existentes = df['Nro_Factura'].astype(str).values
                    df_filtrado = df_nuevo[~df_nuevo['Nro_Factura'].isin(facturas_existentes)]
                    duplicados_count = len(df_nuevo) - len(df_filtrado)

                    if len(df_filtrado) == 0:
                        st.warning(f"Todas las facturas en este archivo ({duplicados_count}) ya existen en la base de datos.")
                    else:
                        st.write(f"Vista previa: Se cargarán {len(df_filtrado)} facturas nuevas (se omitirán {duplicados_count} duplicadas).")
                        st.dataframe(df_filtrado.head())
                        
                        if st.button("CONFIRMAR IMPORTACIÓN", help="Haz clic una sola vez"):
                            with st.spinner('Procesando y guardando datos...'):
                                df_final = pd.concat([df, df_filtrado[df.columns]], ignore_index=True)
                                df_final.to_csv(DB_FILE, index=False)
                                
                                st.success(f"✅ ¡PROCESO COMPLETADO!")
                                st.write(f"Nuevos registros: {len(df_filtrado)}")
                                if duplicados_count > 0:
                                    st.write(f"Registros omitidos por estar duplicados: {duplicados_count}")
                                
                                st.balloons()
                                time.sleep(3)
                                # Al hacer rerun, el uploader con key="uploader_masivo" se resetea
                                st.rerun()
                else:
                    st.error(f"Faltan columnas requeridas: {columnas_req}")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

        st.divider()
        
        if not df.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Puntos_Wurth')
            
            st.download_button(
                label="📥 DESCARGAR BASE DE DATOS ACTUAL (EXCEL)",
                data=buffer.getvalue(),
                file_name=f"base_puntos_wurth_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
