import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Mi HRMS", layout="wide")

# --- LÓGICA DE LOGIN ---
if 'logeado' not in st.session_state: st.session_state['logeado'] = False

def pagina_login():
    st.title("🔐 Acceso al Sistema HRMS")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == "admin" and password == "1234":
            st.session_state['logeado'] = True
            st.rerun()
        else: st.error("Usuario o contraseña incorrectos")

if not st.session_state['logeado']:
    pagina_login()
else:
    # --- PANEL DESBLOQUEADO ---
    st.sidebar.title("⚙️ Navegación")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['logeado'] = False
        st.rerun()
        
    menu = st.sidebar.radio("Módulos:", ["👥 Maestro de Personal", "📍 Monitor de Asistencia", "📊 Dashboard"])

    # --- MÓDULO 1: MAESTRO ---
    if menu == "👥 Maestro de Personal":
        st.title("👥 Maestro de Personal")
        with st.form("form_reg", clear_on_submit=True):
            id_emp = st.text_input("ID de Empleado")
            dni_emp = st.text_input("DNI")
            nombres_emp = st.text_input("Nombres")
            cargo_emp = st.text_input("Cargo")
            area_emp = st.text_input("Área")
            if st.form_submit_button("Guardar"):
                conexion = sqlite3.connect("hrms.db")
                cursor = conexion.cursor()
                cursor.execute("INSERT OR IGNORE INTO maestro_personal VALUES (?,?,?,?,?,?,?)", (id_emp, dni_emp, nombres_emp, cargo_emp, area_emp, "2026-01-01", "Activo"))
                conexion.commit()
                conexion.close()
                st.success("Guardado con éxito")
        
        conexion = sqlite3.connect("hrms.db")
        df = pd.read_sql_query("SELECT * FROM maestro_personal", conexion)
        conexion.close()
        st.dataframe(df, use_container_width=True)

    # --- MÓDULO 2: MONITOR ---
    elif menu == "📍 Monitor de Asistencia":
        st.title("📍 Monitor de Asistencia")
        conexion = sqlite3.connect("hrms.db")
        df = pd.read_sql_query("""
            SELECT a.id_marcaje, m.nombres_completos, a.fecha_hora, a.tipo_marcaje, a.latitud, a.longitud 
            FROM registro_asistencia a
            LEFT JOIN maestro_personal m ON a.id_empleado = m.id_empleado
        """, conexion)
        conexion.close()
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte en Excel (CSV)", data=csv, file_name='asistencia.csv', mime='text/csv')

    # --- MÓDULO 3: DASHBOARD REAL ---
    elif menu == "📊 Dashboard":
        st.title("📊 Indicadores y Alertas")
        conexion = sqlite3.connect("hrms.db")
        
        # 1. Cargamos datos
        df_asistencia = pd.read_sql_query("SELECT * FROM registro_asistencia", conexion)
        df_empleados = pd.read_sql_query("SELECT * FROM maestro_personal", conexion)
        conexion.close()

        if not df_asistencia.empty:
            # Cálculos de Indicadores
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Marcajes", len(df_asistencia))
            col2.metric("Entradas", len(df_asistencia[df_asistencia['tipo_marcaje'] == 'Entrada']))
            col3.metric("Salidas", len(df_asistencia[df_asistencia['tipo_marcaje'] == 'Salida']))

            st.markdown("---")
            
            # ==========================================
            # NUEVO: LÓGICA DE ALERTAS
            # ==========================================
            st.subheader("⚠️ Alertas de Cumplimiento")
            
            # Obtenemos los IDs que sí marcaron hoy
            ids_marcados = df_asistencia['id_empleado'].unique()
            
            # Filtramos quiénes del Maestro NO están en la lista de marcados
            pendientes = df_empleados[~df_empleados['id_empleado'].isin(ids_marcados)]
            
            if not pendientes.empty:
                st.warning(f"¡Atención! {len(pendientes)} trabajadores aún no marcan asistencia hoy:")
                st.table(pendientes[['id_empleado', 'nombres_completos', 'cargo']])
            else:
                st.success("✅ Todo el personal ha marcado asistencia hoy.")

            st.markdown("---")
            st.subheader("Distribución por tipo")
            st.bar_chart(df_asistencia['tipo_marcaje'].value_counts())
        else:
            st.info("Aún no hay datos suficientes para generar el dashboard.")