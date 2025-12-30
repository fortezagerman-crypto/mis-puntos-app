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
        # Leemos el ID como texto para preservar ceros iniciales
        return pd.read_csv('base_datos_puntos.csv', dtype={'ID_Cliente': str})
    return pd.DataFrame(columns=["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra", "Puntos_Ganados", "Fecha"])

df = cargar_datos()

st.title("Sistema de Fidelidad")
opcion = st.sidebar.radio("MENÚ", ["🔍 Consultar Puntos", "🏬 Registro Staff"])

if opcion == "🏬 Registro Staff":
    st.subheader("Panel Administrativo")
    # Clave de acceso: 089020011
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

        with col_desc:
            if not df.empty:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Puntos_Wurth')
                
                st.download_button(
                    label="📥 DESCARGAR EXCEL",
                    data=buffer.getvalue(),
                    file_name=f"Base_Puntos_Wurth_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with col_del:
            if not df.empty:
                if st.button("🗑️ ELIMINAR ÚLTIMO REGISTRO"):
                    df_reducido = df.drop(df.index[-1])
                    df_reducido.to_csv("base_datos_puntos.csv", index=False)
                    st.warning("Último registro eliminado.")
                    st.rerun()

        st.write("### Vista previa de registros")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

    elif st.session_state.get('password'):
        st.error("Clave incorrecta")

else:
    # --- SECCIÓN DE CONSULTA PARA CLIENTES (CORREGIDA) ---
    st.subheader("Consulta tus puntos acumulados")
    st.write("Ingresa tu número de cliente para conocer tu saldo y beneficios.")
    
    # Recuperamos el campo de ID que faltaba
    busqueda = st.text_input("Número de ID de Cliente", placeholder="Ej: 12345678")
    
    if busqueda:
        # Buscamos en la base de datos comparando como texto
        datos_cliente = df[df["ID_Cliente"].astype(str) == str(busqueda).strip()]
        
        if not datos_cliente.empty:
            # Obtenemos el nombre (del primer registro que encontremos para ese ID)
            nombre_cliente = datos_cliente["Nombre_Cliente"].iloc[0]
            total_puntos = int(datos_cliente["Puntos_Ganados"].sum())
            
            # Saludo personalizado y visualización de puntos
            st.markdown(f"## ¡Hola, **{nombre_cliente}**!")
            st.metric("Tu saldo actual es de:", f"{total_puntos} Puntos")
            
            with st.expander("Ver detalle de mis compras"):
                # Ordenamos para mostrar lo más reciente primero
                tabla_usuario = datos_cliente[["Fecha", "Nro_Factura", "Puntos_Ganados"]].sort_values(by="Fecha", ascending=False)
                st.table(tabla_usuario)
            
            st.balloons()
        else:
            st.warning("No encontramos el ID ingresado. Por favor, verifica el número con tu vendedor.")
