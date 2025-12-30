import streamlit as st
import pandas as pd
from datetime import date
import os
import io

# 1. CONFIGURACIÓN DE PÁGINA (Pestaña del navegador)
st.set_page_config(
    page_title="Puntos Würth",
    page_icon="logo_UY.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. METADATOS "LIMPIOS" PARA ELIMINAR LA PUBLICIDAD
# Usamos un bloque HTML oculto pero legible por WhatsApp
st.markdown(
    """
    <head>
        <title>Sistema de Fidelidad Würth Uruguay</title>
        <meta name="title" content="Sistema de Fidelidad Würth Uruguay">
        
        <meta name="description" content="Portal oficial para clientes Würth Uruguay. Consulta tu saldo de puntos y beneficios aquí.">
        
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://puntos-wurth-uy.streamlit.app/">
        <meta property="og:title" content="Puntos Würth Uruguay">
        <meta property="og:description" content="Accede para ver tu historial de puntos acumulados.">
        <meta property="og:image" content="https://raw.githubusercontent.com/fortezagerman-crypto/mis-puntos-app/main/logo_UY.png">

        <meta property="twitter:card" content="summary_large_image">
        <meta property="twitter:title" content="Puntos Würth Uruguay">
        <meta property="twitter:description" content="Portal oficial para clientes Würth Uruguay.">
    </head>
    """,
    unsafe_allow_html=True
)

# --- ESTILOS Y RESTO DEL CÓDIGO ---
# (El resto de tu código de gestión de base de datos sigue aquí abajo)
