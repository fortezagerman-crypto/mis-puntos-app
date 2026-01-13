# --- CARGA MASIVA (Sección que no te aparece) ---
        st.divider()
        st.markdown("### 2. Carga Masiva desde Excel")
        st.info("Sube un archivo **.xlsx** con las columnas: ID_Cliente, Nombre_Cliente, Nro_Factura, Monto_Compra")
        
        archivo_excel = st.file_uploader("Arrastra aquí tu reporte de BI", type=['xlsx'])
        
        if archivo_excel is not None:
            try:
                df_nuevo = pd.read_excel(archivo_excel)
                columnas_necesarias = ["ID_Cliente", "Nombre_Cliente", "Nro_Factura", "Monto_Compra"]
                
                if all(col in df_nuevo.columns for col in columnas_necesarias):
                    df_nuevo['ID_Cliente'] = df_nuevo['ID_Cliente'].astype(str)
                    df_nuevo['Puntos_Ganados'] = (df_nuevo['Monto_Compra'] // 100).astype(int)
                    df_nuevo['Fecha'] = date.today()
                    
                    st.write("Vista previa de la carga:")
                    st.dataframe(df_nuevo.head())
                    
                    if st.button("CONFIRMAR IMPORTACIÓN"):
                        df_final = pd.concat([df, df_nuevo[df.columns]], ignore_index=True)
                        df_final.to_csv(DB_FILE, index=False)
                        st.success(f"✅ Se han cargado {len(df_nuevo)} registros.")
                        st.rerun()
                else:
                    st.error(f"Faltan columnas: {columnas_necesarias}")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
