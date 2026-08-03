import streamlit as st
import math
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA (Dashboard)
# ==========================================
st.set_page_config(
    page_title="DesignStruct Pro", 
    layout="wide", 
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. BARRA LATERAL (CONFIGURACIÓN)
# ==========================================
with st.sidebar:
    st.title("⚙️ Parámetros")
    st.markdown("Marco normativo de diseño:")
    
    reglamento = st.selectbox(
        "Normativa Aplicable:", 
        ["NTC-CDMX (Vigente)", "Reglamento BC (ACI 318)"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.caption("Desarrollado para cálculo de elementos de Concreto y Mampostería.")
    st.caption("📍 Baja California, México")

# ==========================================
# 3. CABECERA PRINCIPAL
# ==========================================
st.title("🏗️ DesignStruct Pro")
st.markdown("Plataforma de análisis y diseño de elementos estructurales.")
st.divider()

# ==========================================
# 4. PESTAÑAS DE MÓDULOS
# ==========================================
t_flexion, t_cortante, t_columnas, t_mamposteria = st.tabs([
    "📐 Flexión (Vigas)", 
    "✂️ Cortante (Vigas)", 
    "🏛️ Flexocompresión (Columnas)", 
    "🧱 Muros (Mampostería)"
])

# ------------------------------------------
# MÓDULO A: FLEXIÓN
# ------------------------------------------
with t_flexion:
    st.subheader("Diseño de Acero Longitudinal")
    
    col_input, col_output = st.columns([1.2, 1])
    
    with col_input:
        with st.container(border=True):
            st.markdown("#### 📥 Datos de Entrada")
            c1, c2 = st.columns(2)
            with c1:
                fc_flex = st.number_input("f'c - Resistencia Concreto (kg/cm²)", value=250, step=10, key="fc_f")
                fy_flex = st.number_input("fy - Fluencia Acero (kg/cm²)", value=4200, step=100, key="fy_f")
                Mu = st.number_input("Momento de Diseño, Mu (Ton-m)", value=25.0, step=1.0)
            with c2:
                b_flex = st.number_input("Base, b (cm)", value=30, step=5, key="b_f")
                h_flex = st.number_input("Peralte Total, h (cm)", value=60, step=5, key="h_f")
                rec_flex = st.number_input("Recubrimiento (cm)", value=5, step=1, key="rec_f")

    with col_output:
        with st.container(border=True):
            st.markdown("#### 📊 Resultados Analíticos")
            
            d_flex = h_flex - rec_flex
            
            if reglamento == "NTC-CDMX (Vigente)":
                FR_flex = 0.90 
                fc_calc = 0.85 * (0.80 * fc_flex) 
                beta1 = 0.85 if fc_flex <= 280 else max(0.65, 1.05 - (fc_flex / 1400))
                rho_min = (0.7 * math.sqrt(fc_flex)) / fy_flex 
            else: 
                FR_flex = 0.90 
                fc_calc = 0.85 * fc_flex 
                beta1 = 0.85 if fc_flex <= 280 else max(0.65, 0.85 - (0.05 * (fc_flex - 280) / 70))
                rho_min = max((0.8 * math.sqrt(fc_flex)) / fy_flex, 14 / fy_flex) 

            rho_b = (fc_calc / fy_flex) * ((6000 * beta1) / (6000 + fy_flex))
            rho_max = 0.75 * rho_b 
            coeficiente = (Mu * 100000) / (FR_flex * b_flex * (d_flex**2) * fc_calc)

            try:
                q = 1 - math.sqrt(1 - (2 * coeficiente))
                rho_req = q * (fc_calc / fy_flex)
                As_req = rho_req * b_flex * d_flex
                As_min_cm2 = rho_min * b_flex * d_flex
                As_max_cm2 = rho_max * b_flex * d_flex
                
                rm1, rm2 = st.columns(2)
                rm1.metric("Acero Requerido (As)", f"{As_req:.2f} cm²", f"Mínimo: {As_min_cm2:.2f} cm²")
                rm2.metric("Límite Máximo Dúctil", f"{As_max_cm2:.2f} cm²")
                
                if rho_req < rho_min:
                    st.info(f"Rige cuantía mínima. Usar: **{As_min_cm2:.2f} cm²**")
                elif rho_req > rho_max:
                    st.error("Falla frágil por compresión. Aumentar sección.")
                else:
                    st.success("Sección óptima y dúctil.")
                    
            except ValueError:
                st.error("Momento excesivo para la sección. Aumentar b o h.")

# ------------------------------------------
# MÓDULO B: CORTANTE
# ------------------------------------------
with t_cortante:
    st.subheader("Diseño de Refuerzo Transversal (Estribos)")
    
    col_v_in, col_v_out = st.columns([1.2, 1])
    
    with col_v_in:
        with st.container(border=True):
            st.markdown("#### 📥 Parámetros de Sección")
            cv1, cv2 = st.columns(2)
            with cv1:
                fc_v = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_v")
                fy_v = st.number_input("fy estribos (kg/cm²)", value=4200, step=100, key="fy_v")
                Av = st.number_input("Área estribo (cm²)", value=1.42, help="Estribo #3 a 2 ramas = 1.42")
            with cv2:
                b_v = st.number_input("Base, b (cm)", value=30, step=5, key="b_v")
                d_v = st.number_input("Peralte Efectivo, d (cm)", value=55, step=5, key="d_v")
                Vu = st.number_input("Cortante, Vu (Ton)", value=15.0, step=1.0)

    with col_v_out:
        with st.container(border=True):
            st.markdown("#### 📊 Disposición de Estribos")
            FR_v = 0.75 
            
            if reglamento == "NTC-CDMX (Vigente)":
                Vcr_kg = FR_v * 0.5 * math.sqrt(0.80 * fc_v) * b_v * d_v
            else: 
                Vcr_kg = FR_v * 0.53 * math.sqrt(fc_v) * b_v * d_v
                
            Vcr_ton = Vcr_kg / 1000
            st.write(f"Resistencia del concreto (Vc): **{Vcr_ton:.2f} Ton**")

            if Vu <= Vcr_ton:
                st.success(f"Estribos por especificación mínima a cada **{d_v / 2:.1f} cm**.")
            else:
                Vsr_ton = Vu - Vcr_ton
                st.warning(f"Acero requerido para: **{Vsr_ton:.2f} Ton**")
                
                Vsr_kg = Vsr_ton * 1000
                separacion = (FR_v * Av * fy_v * d_v) / Vsr_kg
                s_max = d_v / 2
                sep_final = min(separacion, s_max)
                
                st.metric("Separación Calculada (s)", f"{sep_final:.1f} cm", f"Máxima: {s_max:.1f} cm")
                
                if sep_final < 6.0:
                    st.error("Separación muy estrecha. Usar estribos más gruesos.")
                else:
                    st.success(f"Armar con estribos a cada **{math.floor(sep_final)} cm**.")

# ------------------------------------------
# MÓDULO C: COLUMNAS
# ------------------------------------------
with t_columnas:
    st.subheader("Revisión por Flexocompresión")
    
    col_c_in, col_c_out = st.columns([1, 1])
    
    with col_c_in:
        with st.container(border=True):
            st.markdown("#### 📥 Propiedades de la Columna")
            cc1, cc2 = st.columns(2)
            with cc1:
                b_c = st.number_input("Base (cm)", value=40, step=5, key="b_c")
                h_c = st.number_input("Peralte (cm)", value=40, step=5, key="h_c")
                fc_c = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_c")
                fy_c = st.number_input("fy (kg/cm²)", value=4200, step=100, key="fy_c")
            with cc2:
                num_var = st.number_input("Cant. varillas", value=8, step=2, min_value=4)
                a_var = st.number_input("Área varilla (cm²)", value=2.85)
                Pu = st.number_input("Carga Axial, Pu (Ton)", value=100.0, step=10.0)
                Mu_c = st.number_input("Momento, Mu (Ton-m)", value=15.0, step=1.0)

    with col_c_out:
        with st.container(border=True):
            st.markdown("#### 📊 Diagrama de Interacción")
            Ag = b_c * h_c  
            Ast = num_var * a_var  
            rho_col = Ast / Ag

            FR_c = 0.70 if reglamento == "NTC-CDMX (Vigente)" else 0.65
            fc_calc_c = (0.85 * 0.80 * fc_c) if reglamento == "NTC-CDMX (Vigente)" else (0.85 * fc_c)
            
            if rho_col < 0.01 or rho_col > 0.06:
                st.error(f"Cuantía {rho_col*100:.2f}% fuera de norma (1-6%)")
            else:
                st.success(f"Cuantía de acero: {rho_col*100:.2f}% (Válida)")

            Po_kg = FR_c * ((fc_calc_c * (Ag - Ast)) + (fy_c * Ast))
            Po_ton = Po_kg / 1000
            As_tension = Ast / 2
            a_flex = (As_tension * fy_c) / (fc_calc_c * b_c)
            Mo_kgcm = FR_c * As_tension * fy_c * ((h_c - 5) - (a_flex / 2))
            Mo_tonm = Mo_kgcm / 100000

            datos_curva = pd.DataFrame({
                "Momento (Ton-m)": [0, Mo_tonm * 1.5, Mo_tonm],
                "Carga Axial (Ton)": [Po_ton, Po_ton * 0.4, 0]
            })
            
            st.line_chart(datos_curva, x="Momento (Ton-m)", y="Carga Axial (Ton)", height=200)

# ------------------------------------------
# MÓDULO D: MAMPOSTERÍA
# ------------------------------------------
with t_mamposteria:
    st.subheader("Dictamen de Muros Confinados")
    
    col_m_in, col_m_out = st.columns([1.2, 1])
    
    with col_m_in:
        with st.container(border=True):
            st.markdown("#### 📥 Dimensiones y Cargas")
            cm1, cm2 = st.columns(2)
            with cm1:
                L = st.number_input("Longitud, L (m)", value=3.0, step=0.1)
                H = st.number_input("Altura, H (m)", value=2.5, step=0.1)
                t = st.number_input("Espesor, t (cm)", value=15.0, step=1.0)
            with cm2:
                fm = st.number_input("f*m compresión (kg/cm²)", value=15.0, step=1.0)
                vm = st.number_input("v*m cortante (kg/cm²)", value=3.0, step=0.5)
                Pu_muro = st.number_input("Carga Vertical (Ton)", value=10.0, step=1.0)
                Vu_muro = st.number_input("Fuerza Sísmica (Ton)", value=4.0, step=1.0)

    with col_m_out:
        with st.container(border=True):
            st.markdown("#### 📊 Revisión Estructural")
            AT_cm2 = (L * (t / 100)) * 10000 
            
            PR_ton = (0.60 * 0.70 * fm * AT_cm2) / 1000  
            aporte_friccion = 0.3 * (Pu_muro * 1000) 
            VR_ton = (0.70 * ((0.5 * vm * AT_cm2) + aporte_friccion)) / 1000

            st.metric("Resistencia a Compresión (PR)", f"{PR_ton:.2f} Ton", f"Demanda: {Pu_muro:.2f} Ton", delta_color="inverse")
            if PR_ton >= Pu_muro:
                st.success("✅ Muro estable bajo cargas gravitacionales.")
            else:
                st.error("❌ Falla por aplastamiento. Aumentar espesor.")
                
            st.divider()

            st.metric("Resistencia a Cortante (VR)", f"{VR_ton:.2f} Ton", f"Demanda: {Vu_muro:.2f} Ton", delta_color="inverse")
            if VR_ton >= Vu_muro:
                st.success("✅ Soporta la fuerza cortante sísmica.")
            else:
                st.error("❌ Falla diagonal inminente. Reforzar o alargar muro.")
