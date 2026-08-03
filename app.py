import streamlit as st
import math
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="DesignStruct Pro | Concreto & Mampostería", 
    layout="wide", 
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para mejorar las métricas
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0056b3;
    }
    .titulo-modulo {
        color: #0056b3;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BARRA LATERAL (CONFIGURACIÓN GLOBAL)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942933.png", width=80)
    st.title("⚙️ Parámetros Globales")
    
    st.markdown("Selecciona el marco normativo de diseño. Esto ajustará automáticamente los factores de carga y resistencia en todos los módulos.")
    
    reglamento = st.selectbox(
        "Normativa Aplicable:", 
        ["NTC-CDMX (Vigente)", "Reglamento BC (ACI 318)"]
    )
    
    st.divider()
    st.caption("Desarrollado para el curso de Diseño de Estructuras de Concreto y Mampostería.")
    st.caption("📍 Baja California, México")

# ==========================================
# 3. CABECERA PRINCIPAL
# ==========================================
st.title("🏗️ DesignStruct Pro")
st.markdown("Plataforma interactiva para el cálculo y revisión de elementos estructurales.")

# ==========================================
# 4. MOTOR LÓGICO Y PESTAÑAS
# ==========================================
t_flexion, t_cortante, t_columnas, t_mamposteria = st.tabs([
    "📐 Flexión (Vigas)", 
    "✂️ Cortante (Vigas)", 
    "🏛️ Columnas", 
    "🧱 Mampostería"
])

# ------------------------------------------
# MÓDULO A: FLEXIÓN
# ------------------------------------------
with t_flexion:
    st.markdown("<h3 class='titulo-modulo'>Diseño de Acero Longitudinal</h3>", unsafe_allow_html=True)
    
    # Contenedor de Inputs
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            fc_flex = st.number_input("f'c - Resistencia Concreto (kg/cm²)", value=250, step=10, key="fc_f")
            fy_flex = st.number_input("fy - Fluencia Acero (kg/cm²)", value=4200, step=100, key="fy_f")
        with col2:
            b_flex = st.number_input("Base, b (cm)", value=30, step=5, key="b_f")
            h_flex = st.number_input("Peralte Total, h (cm)", value=60, step=5, key="h_f")
            rec_flex = st.number_input("Recubrimiento al centroide (cm)", value=5, step=1, key="rec_f")
        with col3:
            Mu = st.number_input("Momento Último de Diseño, Mu (Ton-m)", value=25.0, step=1.0)

    # Cálculo Interno
    d_flex = h_flex - rec_flex
    
    if reglamento == "NTC-CDMX (Vigente)":
        FR_flex = 0.90 
        fc_calc = 0.85 * (0.80 * fc_flex) # f''c
        beta1 = 0.85 if fc_flex <= 280 else max(0.65, 1.05 - (fc_flex / 1400))
        rho_min = (0.7 * math.sqrt(fc_flex)) / fy_flex 
    else: # ACI 318
        FR_flex = 0.90 
        fc_calc = 0.85 * fc_flex 
        beta1 = 0.85 if fc_flex <= 280 else max(0.65, 0.85 - (0.05 * (fc_flex - 280) / 70))
        rho_min = max((0.8 * math.sqrt(fc_flex)) / fy_flex, 14 / fy_flex) 

    rho_b = (fc_calc / fy_flex) * ((6000 * beta1) / (6000 + fy_flex))
    rho_max = 0.75 * rho_b 
    coeficiente = (Mu * 100000) / (FR_flex * b_flex * (d_flex**2) * fc_calc)

    st.subheader("Resultados Analíticos")
    try:
        q = 1 - math.sqrt(1 - (2 * coeficiente))
        rho_req = q * (fc_calc / fy_flex)
        As_req = rho_req * b_flex * d_flex
        As_min_cm2 = rho_min * b_flex * d_flex
        As_max_cm2 = rho_max * b_flex * d_flex
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Acero Mínimo", f"{As_min_cm2:.2f} cm²", f"ρ = {rho_min:.4f}")
        c2.metric("Acero Requerido (As)", f"{As_req:.2f} cm²", f"ρ = {rho_req:.4f}", delta_color="off")
        c3.metric("Acero Máximo (Límite dúctil)", f"{As_max_cm2:.2f} cm²", f"ρ = {rho_max:.4f}")
        
        if rho_req < rho_min:
            st.info(f"El cálculo demanda poco acero. Por seguridad normativa, rige la cuantía mínima: colocar **{As_min_cm2:.2f} cm²**.")
        elif rho_req > rho_max:
            st.error("⚠️ La sección está sobre-reforzada. El concreto fallará por aplastamiento antes de que el acero fluya. Aumenta la sección (b, h) o diseña con acero en compresión.")
        else:
            st.success("Condición ideal. La viga es simplemente reforzada y garantiza una falla dúctil.")
            
    except ValueError:
        st.error("⚠️ El Momento Flector supera la capacidad máxima absoluta de esta geometría. Se requiere aumentar el peralte o la base de la viga.")

# ------------------------------------------
# MÓDULO B: CORTANTE
# ------------------------------------------
with t_cortante:
    st.markdown("<h3 class='titulo-modulo'>Diseño de Estribos (Separación)</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col1_v, col2_v, col3_v = st.columns(3)
        with col1_v:
            fc_v = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_v")
            fy_v = st.number_input("fy de estribos (kg/cm²)", value=4200, step=100, key="fy_v")
        with col2_v:
            b_v = st.number_input("Base, b (cm)", value=30, step=5, key="b_v")
            d_v = st.number_input("Peralte Efectivo, d (cm)", value=55, step=5, key="d_v")
        with col3_v:
            Vu = st.number_input("Cortante Último, Vu (Ton)", value=15.0, step=1.0)
            Av = st.number_input("Área del estribo, Av (cm²)", value=1.42, help="Estribo #3 a dos ramas = 1.42 cm²")

    FR_v = 0.75 
    
    if reglamento == "NTC-CDMX (Vigente)":
        Vcr_kg = FR_v * 0.5 * math.sqrt(0.80 * fc_v) * b_v * d_v
    else: # ACI
        Vcr_kg = FR_v * 0.53 * math.sqrt(fc_v) * b_v * d_v
        
    Vcr_ton = Vcr_kg / 1000

    st.subheader("Evaluación de Cortante")
    st.write(f"Capacidad del concreto ($V_c$): **{Vcr_ton:.2f} Ton**")

    if Vu <= Vcr_ton:
        st.success("El concreto absorbe la totalidad de la fuerza cortante. Colocar estribos a la separación máxima reglamentaria.")
        st.info(f"Separación máxima recomendada: **{d_v / 2:.1f} cm**.")
    else:
        Vsr_ton = Vu - Vcr_ton
        st.warning(f"El concreto es insuficiente. El refuerzo transversal (estribos) debe resistir el remanente: **{Vsr_ton:.2f} Ton**")
        
        Vsr_kg = Vsr_ton * 1000
        separacion = (FR_v * Av * fy_v * d_v) / Vsr_kg
        s_max = d_v / 2
        sep_final = min(separacion, s_max)
        
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Separación Calculada", f"{separacion:.1f} cm")
        col_s2.metric("Separación Máxima (Reglamento)", f"{s_max:.1f} cm")
        
        if sep_final < 6.0:
            st.error("La separación resultante es muy estrecha (< 6 cm), lo que dificulta el colado. Cambia a estribos de mayor diámetro (ej. #4).")
        else:
            st.info(f"👉 **Instrucción de obra:** Armar con estribos separados a **{math.floor(sep_final)} cm**.")

# ------------------------------------------
# MÓDULO C: COLUMNAS
# ------------------------------------------
with t_columnas:
    st.markdown("<h3 class='titulo-modulo'>Revisión por Flexocompresión</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col1_c, col2_c, col3_c = st.columns(3)
        with col1_c:
            fc_c = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_c")
            fy_c = st.number_input("fy (kg/cm²)", value=4200, step=100, key="fy_c")
            b_c = st.number_input("Base (cm)", value=40, step=5, key="b_c")
            h_c = st.number_input("Peralte (cm)", value=40, step=5, key="h_c")
        with col2_c:
            num_var = st.number_input("Número de varillas", value=8, step=2, min_value=4)
            a_var = st.number_input("Área por varilla (cm²)", value=2.85)
            rec_c = st.number_input("Recubrimiento (cm)", value=5, step=1, key="rec_c")
        with col3_c:
            Pu = st.number_input("Carga Axial Actuante, Pu (Ton)", value=100.0, step=10.0)
            Mu_c = st.number_input("Momento Actuante, Mu (Ton-m)", value=15.0, step=1.0)

    Ag = b_c * h_c  
    Ast = num_var * a_var  
    rho_col = Ast / Ag

    # Factores según norma para columnas con estribos
    FR_c = 0.70 if reglamento == "NTC-CDMX (Vigente)" else 0.65
    fc_calc_c = (0.85 * 0.80 * fc_c) if reglamento == "NTC-CDMX (Vigente)" else (0.85 * fc_c)

    st.subheader("Estado de la Columna")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Cuantía de Acero (ρ)", f"{rho_col*100:.2f} %", f"Área: {Ast:.2f} cm²")
        if rho_col < 0.01 or rho_col > 0.06:
            st.error("Cuantía fuera del límite normativo (1% - 6%).")
        else:
            st.success("Cuantía dentro de norma.")

    # Diagrama Simplificado
    Po_kg = FR_c * ((fc_calc_c * (Ag - Ast)) + (fy_c * Ast))
    Po_ton = Po_kg / 1000
    d_c = h_c - rec_c
    As_tension = Ast / 2
    a_flex = (As_tension * fy_c) / (fc_calc_c * b_c)
    Mo_kgcm = FR_c * As_tension * fy_c * (d_c - (a_flex / 2))
    Mo_tonm = Mo_kgcm / 100000

    Pb_ton = Po_ton * 0.4  
    Mb_tonm = Mo_tonm * 1.5 
    
    datos_curva = pd.DataFrame({
        "Momento (Ton-m)": [0, Mb_tonm, Mo_tonm],
        "Carga Axial (Ton)": [Po_ton, Pb_ton, 0]
    })
    
    with c2:
        st.caption("Diagrama de Interacción Simplificado (Frontera de Seguridad)")
        st.line_chart(datos_curva, x="Momento (Ton-m)", y="Carga Axial (Ton)", height=250)
        if Pu > Po_ton:
            st.error("Falla Inminente: La carga axial supera la resistencia máxima a compresión pura.")
        else:
            st.info("Verifica visualmente que tu par de carga (Mu, Pu) quede debajo de la curva generada.")

# ------------------------------------------
# MÓDULO D: MAMPOSTERÍA
# ------------------------------------------
with t_mamposteria:
    st.markdown("<h3 class='titulo-modulo'>Diseño de Muros Confinados</h3>", unsafe_allow_html=True)
    st.caption("Nota: Los criterios de mampostería se rigen universalmente por la mecánica clásica expuesta en las NTC.")
    
    with st.container(border=True):
        col1_m, col2_m, col3_m = st.columns(3)
        with col1_m:
            L = st.number_input("Longitud del muro, L (m)", value=3.0, step=0.1)
            H = st.number_input("Altura libre, H (m)", value=2.5, step=0.1)
            t = st.number_input("Espesor del muro, t (cm)", value=15.0, step=1.0)
        with col2_m:
            fm = st.number_input("Compresión mampostería, f*m (kg/cm²)", value=15.0, step=1.0)
            vm = st.number_input("Cortante mampostería, v*m (kg/cm²)", value=3.0, step=0.5)
        with col3_m:
            Pu_muro = st.number_input("Carga Vertical (Gravedad), Pu (Ton)", value=10.0, step=1.0)
            Vu_muro = st.number_input("Cortante en el plano (Sismo), Vu (Ton)", value=4.0, step=1.0)

    AT_cm2 = (L * (t / 100)) * 10000 
    
    # Resistencias
    PR_ton = (0.60 * 0.70 * fm * AT_cm2) / 1000  # FR * Factor de Esbeltez * f*m * Area
    aporte_friccion = 0.3 * (Pu_muro * 1000) 
    VR_ton = (0.70 * ((0.5 * vm * AT_cm2) + aporte_friccion)) / 1000

    st.subheader("Dictamen Estructural del Muro")
    rm1, rm2 = st.columns(2)
    
    with rm1:
        with st.container(border=True):
            st.markdown("#### 📉 Revisión Gravitacional")
            st.metric("Capacidad a Compresión (PR)", f"{PR_ton:.2f} Ton", f"Demanda: {Pu_muro:.2f} Ton", delta_color="inverse")
            if PR_ton >= Pu_muro:
                st.success("Muro estable bajo cargas verticales.")
            else:
                st.error("Riesgo de aplastamiento. Aumentar espesor o longitud.")

    with rm2:
        with st.container(border=True):
            st.markdown("#### 🌪️ Revisión Sísmica")
            st.metric("Capacidad a Cortante (VR)", f"{VR_ton:.2f} Ton", f"Demanda: {Vu_muro:.2f} Ton", delta_color="inverse")
            if VR_ton >= Vu_muro:
                st.success("El muro es capaz de disipar la energía sísmica sin refuerzo interior.")
            else:
                st.error("Falla por cortante inminente. Se requiere refuerzo horizontal o mampostería reforzada interiormente.")
