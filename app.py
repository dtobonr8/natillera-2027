import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Natillera",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Sistema de Gestión de Natillera")
st.write("Control integral de ahorros, rifas, préstamos y penalizaciones.")

# Menú lateral para navegar entre módulos
opcion = st.sidebar.radio(
    "Navegación",
    [
        "👥 Socios", 
        "💵 Ahorros y Multas", 
        "🎲 Rifa (Lotería)", 
        "🏦 Préstamos y Cartera", 
        "📊 Resumen y Liquidación"
    ]
)

# ----------------------------------------------------
# 1. MÓDULO DE SOCIOS
# ----------------------------------------------------
if opcion == "👥 Socios":
    st.header("👥 Gestión de Socios y Números de Rifa")
    st.info("Límite de 30 cupos. Cada socio tiene un número fijo de 2 dígitos asignado para todo el año.")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo del Socio")
        telefono = st.text_input("Teléfono / WhatsApp")
    with col2:
        numero_rifa = st.number_input("Número Fijo de Rifa (00 - 99)", min_value=0, max_value=99, step=1, format="%02d")
        frecuencia = st.selectbox("Frecuencia de Ahorro", ["Quincenal", "Mensual"])
        
    if st.button("Registrar Socio"):
        st.success(f"Socio {nombre} registrado correctamente con el número {numero_rifa:02d}.")

# ----------------------------------------------------
# 2. MÓDULO DE AHORROS Y MULTAS
# ----------------------------------------------------
elif opcion == "💵 Ahorros y Multas":
    st.header("💵 Control de Ahorros y Penalizaciones")
    st.caption("Fechas límite: días 2 y 16. Multas: $4.000 (quincenal) / $8.000 (mensual). Se acumulan para el cierre de año.")
    
    # Registro de cuotas
    st.subheader("Registrar Cuota de Ahorro")
    # Lógica para seleccionar socio y registrar aporte
    
# ----------------------------------------------------
# 3. MÓDULO DE RIFA
# ----------------------------------------------------
elif opcion == "🎲 Rifa (Lotería)":
    st.header("🎲 Rifa Mensual (Lotería de Medellín)")
    st.caption("Aporte mensual: $10.000 por socio. 50% para el ganador y 50% para el fondo común.")
    
# ----------------------------------------------------
# 4. MÓDULO DE PRÉSTAMOS
# ----------------------------------------------------
elif opcion == "🏦 Préstamos y Cartera":
    st.header("🏦 Préstamos e Intereses (6% Simple)")
    st.caption("Los abonos cubren primero los intereses del mes y el excedente reduce el capital.")

# ----------------------------------------------------
# 5. RESUMEN Y LIQUIDACIÓN
# ----------------------------------------------------
elif opcion == "📊 Resumen y Liquidación":
    st.header("📊 Estado General y Cierre de Vigencia")
    st.caption("Fondo común total y cruce automático de deudas de fin de año.")