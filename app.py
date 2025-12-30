import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os

# 1. CONFIGURACIÓN VISUAL E ICONO
st.set_page_config(
    page_title="Puntos Würth", 
    page_icon="logo_UY.png", 
    layout="centered"
)

# Estilo Rojo Würth corporativo
st.markdown("""
    <style>
    .stButton>button { background-color: #E60002; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #E60002; }
    div[data-baseweb="input"] { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Mostrar Logo si existe
if os.path.exists('logo_UY.png'):
    st.image('logo_UY.png', width=180)

# 2. CONEXIÓN A GOOGLE SHEETS
# Se conecta usando la URL guardada en "Secrets"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 obliga a la app a leer datos nuevos de Google Sheets cada vez
    return conn.read(ttl=0)

# Intentar cargar datos, si falla mostrar error descriptivo
try:
    df = cargar_datos()
except Exception as e:
    st.error("Error al conectar con Google Sheets. Verifica los permisos de 'Editor' y el link en Secrets.")
    st.stop()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["🔍 Consultar mis Puntos", "🏬 Registro Staff (Interno)"])

# --- SECCIÓN DE REGISTRO (VENDEDOR) ---
if opcion == "🏬 Registro Staff (Interno)":
    st.subheader("Acceso Restringido")
    
    # CLAVE CONFIGURADA (Mantenla como texto entre comillas)
    CLAVE_CORRECTA = "089020011" 
    
    # Campo de contraseña
    password = st.text_input("Introduce la clave de vendedor", type="password", help="Código de producto universal")
    
    # Validación: .strip() elimina espacios accidentales al inicio o final
    if password.strip() == CLAVE_CORRECTA:
        st.success("🔓 Acceso concedido")
        st.divider()
        st.subheader("Formulario de Carga")
        
        with st.form("registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                id_c = st.text_input("ID o DNI Cliente")
                nom = st.text_input("Nombre Completo")
            with col2:
                fac = st.text_input("Número de Factura")
                mon = st.number_input("Monto de Compra ($)", min_value=0.0, step=100.0)
            
            btn_enviar = st.form_submit_button("REGISTRAR PUNTOS")
            
            if btn_enviar:
                if id_c and nom and fac and mon > 0:
                    puntos = int(mon // 100) # Cálculo de 1 punto cada $100
                    
                    # Preparar los datos nuevos con los nombres de columna exactos de Google Sheets
                    nueva_fila = pd.DataFrame([{
                        "ID_Cliente": str(id_c).strip(),
                        "Nombre_Cliente": nom.strip(),
                        "Nro_Factura": str(fac).strip(),
                        "Monto_Compra": float(mon),
                        "Puntos_Ganados": int(puntos),
                        "Fecha": str(datetime.date.today())
                    }])
                    
                    # Unir datos viejos con el nuevo registro
                    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    # Actualizar Google Sheets
                    conn.update(data=df_actualizado)
                    
                    st.success(f"✅ ¡Puntos cargados con éxito! {nom} sumó {puntos} pts.")
                    st.balloons()
                else:
                    st.error("⚠️ Por favor completa todos los campos con valores válidos.")
    
    elif password != "":
        st.error("❌ Clave incorrecta. Inténtalo de nuevo.")

# --- SECCIÓN DE CONSULTA (CLIENTE) ---
else:
    st.subheader("¡Bienvenido a tu cuenta de puntos!")
    busqueda = st.text_input("Ingresa tu ID de Cliente para consultar")
    
    if busqueda:
        # Aseguramos que la búsqueda compare textos
        datos = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        
        if not datos.empty:
            nombre_cliente = datos["Nombre_Cliente"].iloc[0]
            total_puntos = int(datos["Puntos_Ganados"].sum())
            
            st.markdown(f"### Hola, **{nombre_cliente}**")
            st.metric("Tu saldo actual es de:", f"{total_puntos} Puntos")
            
            with st.expander("Ver detalle de mis facturas"):
                # Mostrar tabla con las columnas relevantes
                columnas_ver = ["Fecha", "Nro_Factura", "Puntos_Ganados"]
                st.table(datos[columnas_ver].sort_values(by="Fecha", ascending=False))
        else:
            st.warning("No encontramos ese ID. Por favor, verifica el número o consulta en el mostrador.")
