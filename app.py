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
                    "ahorro": monto_ahorro,
                    "rifa": monto_rifa,
                    "multa_pendiente": multa_aplicada
                }
                
                datos["ahorros"].append(registro)
                guardar_datos(datos)
                
                if multa_aplicada > 0:
                    st.warning(f"⚠️ Pago registrado fuera de fecha límite. Se acumula una multa de ${multa_aplicada:,.0f} para fin de año.")
                else:
                    st.success(f"✅ Transacción registrada con éxito para {socio_info['nombre']}.")

        st.subheader("📊 Historial de Pagos y Ahorros Registrados")
        if datos["ahorros"]:
            df_ahorros = pd.DataFrame(datos["ahorros"])
            st.dataframe(df_ahorros, use_container_width=True)
        else:
            st.write("No hay pagos de ahorros registrados todavía.")

# ----------------------------------------------------
# 3. MÓDULO DE RIFA
# ----------------------------------------------------
elif opcion == "🎲 Rifa (Lotería)":
    st.header("🎲 Sorteos de la Rifa (Lotería de Medellín)")
    st.caption("Fondo de rifa abonado: $10.000 mensuales por socio. 50% al ganador / 50% al fondo común.")
    
    with st.form("form_sorteo_rifa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            mes_sorteo = st.selectbox("Mes del Sorteo", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
            fecha_sorteo = st.date_input("Fecha del Sorteo", value=FECHA_INICIO_NATILLERA)
        with col2:
            numero_ganador = st.number_input("Número Ganador (2 últimos dígitos Lotería de Medellín)", min_value=0, max_value=99, step=1, format="%02d")
        
        btn_registrar_sorteo = st.form_submit_button("Registrar Ganador del Sorteo")
        
        if btn_registrar_sorteo:
            ganador_info = next((s for s in datos["socios"] if s["numero_rifa"] == numero_ganador), None)
            total_recaudado_rifa = sum([a["rifa"] for a in datos["ahorros"]])
            premio_ganador = total_recaudado_rifa * 0.5
            fondo_comun_rifa = total_recaudado_rifa * 0.5
            
            nombre_ganador = ganador_info["nombre"] if ganador_info else "Número no asignado"
            
            sorteo_rec = {
                "mes": mes_sorteo,
                "fecha": str(fecha_sorteo),
                "numero_ganador": f"{numero_ganador:02d}",
                "ganador": nombre_ganador,
                "premio": premio_ganador,
                "aporte_fondo": fondo_comun_rifa
            }
            
            datos["rifas_sorteos"].append(sorteo_rec)
            guardar_datos(datos)
            
            if ganador_info:
                st.balloons()
                st.success(f"🎉 ¡Felicidades a {nombre_ganador}! Número {numero_ganador:02d}. Ganador de ${premio_ganador:,.0f}.")
            else:
                st.info(f"El número {numero_ganador:02d} cayó pero no está asignado a ningún socio. El 100% de la bolsa acumulada pasa al fondo común.")

    st.subheader("📋 Historial de Sorteos Registrados")
    if datos["rifas_sorteos"]:
        st.dataframe(pd.DataFrame(datos["rifas_sorteos"]), use_container_width=True)
    else:
        st.write("Aún no se han registrado sorteos.")

# ----------------------------------------------------
# 4. MÓDULO DE PRÉSTAMOS
# ----------------------------------------------------
elif opcion == "🏦 Préstamos y Cartera":
    st.header("🏦 Préstamos e Intereses (6% Simple)")
    st.caption("Regla de abonos: Primero se descuentan los intereses del mes (6%) y el restante reduce el capital.")
    
    if not datos["socios"]:
        st.warning("⚠️ Registra socios antes de realizar préstamos.")
    else:
        tab1, tab2 = st.tabs(["💰 Nuevo Préstamo", "💵 Registrar Abono"])
        socios_dict = {f"{s['id']} - {s['nombre']}": s for s in datos["socios"]}
        
        with tab1:
            with st.form("form_prestamo", clear_on_submit=True):
                socio_p = st.selectbox("Socio Prestatario", list(socios_dict.keys()))
                socio_info = socios_dict[socio_p]
                
                col1, col2 = st.columns(2)
                with col1:
                    monto_prestamo = st.number_input("Monto Solicitado ($)", min_value=10000, step=50000)
                with col2:
                    fecha_prestamo = st.date_input("Fecha Desembolso", value=FECHA_INICIO_NATILLERA)
                    
                btn_prestamo = st.form_submit_button("Aprobar Préstamo")
                if btn_prestamo:
                    rec_p = {
                        "id": len(datos["prestamos"]) + 1,
                        "socio_id": socio_info["id"],
                        "nombre": socio_info["nombre"],
                        "monto_inicial": monto_prestamo,
                        "saldo_capital": monto_prestamo,
                        "fecha": str(fecha_prestamo)
                    }
                    datos["prestamos"].append(rec_p)
                    guardar_datos(datos)
                    st.success(f"✅ Préstamo de ${monto_prestamo:,.0f} registrado para {socio_info['nombre']}.")

        with tab2:
            prestamos_activos = [p for p in datos["prestamos"] if p["saldo_capital"] > 0]
            if not prestamos_activos:
                st.info("No hay préstamos con saldo pendiente en este momento.")
            else:
                p_options = {f"Préstamo #{p['id']} - {p['nombre']} (Saldo: ${p['saldo_capital']:,.0f})": p for p in prestamos_activos}
                
                with st.form("form_abono", clear_on_submit=True):
                    p_sel_str = st.selectbox("Seleccionar Préstamo Activo", list(p_options.keys()))
                    p_info = p_options[p_sel_str]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        monto_abono = st.number_input("Valor del Abono ($)", min_value=1000, step=5000)
                    with col2:
                        fecha_abono = st.date_input("Fecha de Abono", value=FECHA_INICIO_NATILLERA)
                        
                    btn_abono = st.form_submit_button("Registrar Abono")
                    
                    if btn_abono:
                        interes_mes = p_info["saldo_capital"] * 0.06
                        
                        if monto_abono <= interes_mes:
                            pago_interes = monto_abono
                            abono_capital = 0
                        else:
                            pago_interes = interes_mes
                            abono_capital = monto_abono - interes_mes
                            
                        for p in datos["prestamos"]:
                            if p["id"] == p_info["id"]:
                                p["saldo_capital"] = max(0, p["saldo_capital"] - abono_capital)
                                break
                                
                        rec_abono = {
                            "prestamo_id": p_info["id"],
                            "nombre": p_info["nombre"],
                            "fecha": str(fecha_abono),
                            "monto_total": monto_abono,
                            "pago_interes": pago_interes,
                            "abono_capital": abono_capital,
                            "nuevo_saldo": p_info["saldo_capital"] - abono_capital
                        }
                        
                        datos["abonos_prestamos"].append(rec_abono)
                        guardar_datos(datos)
                        
                        st.success(f"✅ Abono procesado: ${pago_interes:,.0f} a intereses | ${abono_capital:,.0f} a capital. Nuevo saldo: ${max(0, p_info['saldo_capital'] - abono_capital):,.0f}.")

        st.subheader("📋 Resumen de Cartera y Préstamos")
        if datos["prestamos"]:
            st.dataframe(pd.DataFrame(datos["prestamos"]), use_container_width=True)

# ----------------------------------------------------
# 5. RESUMEN Y LIQUIDACIÓN
# ----------------------------------------------------
elif opcion == "📊 Resumen y Liquidación":
    st.header("📊 Resumen General del Fondo y Liquidación 2027")
    
    total_ahorro = sum([a["ahorro"] for a in datos["ahorros"]])
    total_rifa_fondo = sum([r["aporte_fondo"] for r in datos["rifas_sorteos"]])
    total_multas = sum([a["multa_pendiente"] for a in datos["ahorros"]])
    total_intereses = sum([ab["pago_interes"] for ab in datos["abonos_prestamos"]])
    
    fondo_comun_ganancias = total_rifa_fondo + total_multas + total_intereses
    gran_total_caja = total_ahorro + fondo_comun_ganancias
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Ahorros", f"${total_ahorro:,.0f}")
    col2.metric("🎲 Rendimientos Rifas", f"${total_rifa_fondo:,.0f}")
    col3.metric("📈 Intereses Cobrados", f"${total_intereses:,.0f}")
    col4.metric("🚨 Total Multas Mora", f"${total_multas:,.0f}")
    
    st.divider()
    st.subheader(f"🏦 Fondo Total en Caja: ${gran_total_caja:,.0f}")
    
    st.subheader("📋 Proyección de Liquidación por Socio")
    if datos["socios"]:
        liq_list = []
        for s in datos["socios"]:
            ahorro_s = sum([a["ahorro"] for a in datos["ahorros"] if a["socio_id"] == s["id"]])
            multas_s = sum([a["multa_pendiente"] for a in datos["ahorros"] if a["socio_id"] == s["id"]])
            
            prestamos_s = [p for p in datos["prestamos"] if p["socio_id"] == s["id"]]
            deuda_capital_s = sum([p["saldo_capital"] for p in prestamos_s])
            
            neto_a_entregar = ahorro_s - multas_s - deuda_capital_s
            
            liq_list.append({
                "ID": s["id"],
                "Nombre": s["nombre"],
                "Ahorro Bruto": f"${ahorro_s:,.0f}",
                "(-) Multas Morosas": f"${multas_s:,.0f}",
                "(-) Saldo Préstamos": f"${deuda_capital_s:,.0f}",
                "👉 Liquidación Neta": f"${neto_a_entregar:,.0f}"
            })
            
        st.dataframe(pd.DataFrame(liq_list), use_container_width=True)
    else:
        st.write("No hay socios registrados para liquidar.")