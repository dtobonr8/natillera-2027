import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Natillera 2027",
    page_icon="💰",
    layout="wide"
)

FECHA_INICIO_NATILLERA = date(2027, 1, 15)
DATA_FILE = "natillera_data.json"

# Cargar y Guardar Datos
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "socios": [],
        "ahorros": [],
        "rifas_sorteos": [],
        "prestamos": [],
        "abonos_prestamos": []
    }

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f, indent=4)

datos = cargar_datos()

st.title("💰 Sistema de Gestión de Natillera 2027")
st.caption("Inicio de vigencia: 15 de Enero de 2027 | Control de ahorros, rifas, préstamos y liquidación.")

# Navegación
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
    st.info("Límite: 30 cupos. Cada socio tiene un número fijo de 2 dígitos (00 - 99) para el ciclo 2027.")
    
    with st.form("form_registro_socio", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo del Socio")
            telefono = st.text_input("Teléfono / WhatsApp")
        with col2:
            numero_rifa = st.number_input("Número Fijo de Rifa (00 - 99)", min_value=0, max_value=99, step=1, format="%02d")
            frecuencia = st.selectbox("Frecuencia de Ahorro", ["Quincenal", "Mensual"])
            
        btn_registrar = st.form_submit_button("Registrar Socio")
        
        if btn_registrar:
            if len(datos["socios"]) >= 30:
                st.error("❌ Se ha alcanzado el límite máximo de 30 cupos.")
            elif not nombre.strip():
                st.warning("⚠️ Por favor ingresa el nombre del socio.")
            else:
                numeros_ocupados = [s["numero_rifa"] for s in datos["socios"]]
                if numero_rifa in numeros_ocupados:
                    st.error(f"❌ El número {numero_rifa:02d} ya está asignado a otro socio.")
                else:
                    nuevo_socio = {
                        "id": len(datos["socios"]) + 1,
                        "nombre": nombre.strip(),
                        "telefono": telefono.strip(),
                        "numero_rifa": numero_rifa,
                        "frecuencia": frecuencia
                    }
                    datos["socios"].append(nuevo_socio)
                    guardar_datos(datos)
                    st.success(f"✅ Socio {nombre} registrado correctamente con el número {numero_rifa:02d}.")

    st.subheader("📋 Listado de Socios Registrados")
    if datos["socios"]:
        df_socios = pd.DataFrame(datos["socios"])
        df_socios["numero_rifa"] = df_socios["numero_rifa"].apply(lambda x: f"{x:02d}")
        df_socios.columns = ["ID", "Nombre", "Teléfono", "N° Rifa", "Frecuencia"]
        st.dataframe(df_socios, use_container_width=True)
        st.caption(f"Total inscritos: {len(datos['socios'])} / 30 cupos.")
    else:
        st.write("Aún no hay socios registrados.")

# ----------------------------------------------------
# 2. MÓDULO DE AHORROS Y MULTAS
# ----------------------------------------------------
elif opcion == "💵 Ahorros y Multas":
    st.header("💵 Control de Ahorros y Penalizaciones")
    st.caption("Fechas límite: días 2 y 16. Multas por mora: $4.000 (quincenal) / $8.000 (mensual). Acumulables para el cierre de año.")
    
    if not datos["socios"]:
        st.warning("⚠️ Primero debes registrar socios en el módulo de Socios.")
    else:
        socios_opciones = {f"{s['id']} - {s['nombre']} ({s['frecuencia']})": s for s in datos["socios"]}
        
        with st.form("form_registrar_ahorro", clear_on_submit=True):
            socio_seleccionado_str = st.selectbox("Seleccionar Socio", list(socios_opciones.keys()))
            socio_info = socios_opciones[socio_seleccionado_str]
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_pago = st.date_input("Fecha del Pago", value=FECHA_INICIO_NATILLERA)
                monto_ahorro = st.number_input("Valor Cuota de Ahorro ($)", min_value=0, step=5000)
            with col2:
                incluir_rifa = st.checkbox("¿Pagar cuota de rifa del mes ($10.000)?", value=True)
                
            btn_guardar_pago = st.form_submit_button("Registrar Transacción")
            
            if btn_guardar_pago:
                dia = fecha_pago.day
                multa_aplicada = 0
                
                if socio_info["frecuencia"] == "Quincenal":
                    if (dia > 2 and dia < 16) or (dia > 16):
                        multa_aplicada = 4000
                else:
                    if dia > 2:
                        multa_aplicada = 8000
                
                monto_rifa = 10000 if incluir_rifa else 0
                
                registro = {
                    "socio_id": socio_info["id"],
                    "nombre": socio_info["nombre"],
                    "fecha": str(fecha_pago),
                    "