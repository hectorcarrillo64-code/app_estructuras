import streamlit as st
import math

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="App Diseño Estructural", layout="wide", page_icon="🏗️")

st.title("🏗️ Diseño de Estructuras: Concreto y Mampostería")
st.markdown("---")

# CREACIÓN DE PESTAÑAS (TABS)
tab_flexion, tab_cortante, tab_columnas, tab_mamposteria = st.tabs(["1️⃣ Flexión", "2️⃣ Cortante", "3️⃣ Columnas", "4️⃣ Mampostería"])
# ==========================================
# MÓDULO 1: FLEXIÓN
# ==========================================
with tab_flexion:
    st.header("Diseño de Vigas por Flexión (NTC-CDMX)")
    st.caption("Cálculo de Área de Acero Longitudinal con el Bloque de Whitney")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Materiales")
        fc_flex = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_flex")
        fy_flex = st.number_input("fy (kg/cm²)", value=4200, step=100, key="fy_flex")
    with col2:
        st.subheader("Geometría")
        b_flex = st.number_input("Base, b (cm)", value=30, step=5, key="b_flex")
        h_flex = st.number_input("Peralte Total, h (cm)", value=60, step=5, key="h_flex")
        rec_flex = st.number_input("Recubrimiento, r (cm)", value=5, step=1, key="rec_flex")
    with col3:
        st.subheader("Fuerzas")
        Mu = st.number_input("Momento Último, Mu (Ton-m)", value=25.0, step=1.0)
        
    d_flex = h_flex - rec_flex
    FR_flex = 0.90 
    fc_star_flex = 0.80 * fc_flex 
    fc_biprima = 0.85 * fc_star_flex 

    beta1 = 0.85 if fc_flex <= 280 else max(0.65, 1.05 - (fc_flex / 1400))
    rho_min = (0.7 * math.sqrt(fc_flex)) / fy_flex 
    rho_b = (fc_biprima / fy_flex) * ((6000 * beta1) / (6000 + fy_flex))
    rho_max = 0.75 * rho_b 

    Mu_kgcm = Mu * 100000 
    coeficiente = Mu_kgcm / (FR_flex * b_flex * (d_flex**2) * fc_biprima)

    try:
        q = 1 - math.sqrt(1 - (2 * coeficiente))
        rho_req = q * (fc_biprima / fy_flex)
        As_req = rho_req * b_flex * d_flex
        As_min_cm2 = rho_min * b_flex * d_flex
        As_max_cm2 = rho_max * b_flex * d_flex
        
        st.markdown("---")
        st.subheader("Resultados de Flexión")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Acero Mínimo", f"{As_min_cm2:.2f} cm²", f"ρ = {rho_min:.4f}")
        res_col2.metric("Acero Requerido (As)", f"{As_req:.2f} cm²", f"ρ = {rho_req:.4f}")
        res_col3.metric("Acero Máximo", f"{As_max_cm2:.2f} cm²", f"ρ = {rho_max:.4f}")
        
        if rho_req < rho_min:
            st.warning(f"⚠️ Usa el acero mínimo normativo: **{As_min_cm2:.2f} cm²**.")
        elif rho_req > rho_max:
            st.error("❌ Falla por compresión (frágil). Aumenta la sección (b, h).")
        else:
            st.success("✅ Diseño Satisfactorio y dúctil.")
    except ValueError:
        st.error("❌ El Momento es demasiado grande para esta sección. Aumenta b o h.")


# ==========================================
# MÓDULO 2: CORTANTE
# ==========================================
with tab_cortante:
    st.header("Diseño de Vigas por Cortante (NTC-CDMX)")
    st.caption("Cálculo de separación de estribos")

    col1_v, col2_v, col3_v = st.columns(3)
    with col1_v:
        st.subheader("Materiales")
        fc_v = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_v")
        fy_v = st.number_input("fy estribos (kg/cm²)", value=4200, step=100, key="fy_v")
    with col2_v:
        st.subheader("Geometría")
        b_v = st.number_input("Base, b (cm)", value=30, step=5, key="b_v")
        h_v = st.number_input("Peralte Total, h (cm)", value=60, step=5, key="h_v")
        rec_v = st.number_input("Recubrimiento, r (cm)", value=5, step=1, key="rec_v")
    with col3_v:
        st.subheader("Fuerzas y Acero")
        Vu = st.number_input("Cortante Último, Vu (Ton)", value=15.0, step=1.0)
        # Un estribo del #3 (3/8") tiene 2 ramas, su área es 2 * 0.71 = 1.42 cm2
        Av = st.number_input("Área del estribo, Av (cm²)", value=1.42, help="Para estribo #3 con 2 ramas usa 1.42")

    d_v = h_v - rec_v
    FR_v = 0.75 # Factor de resistencia para cortante
    fc_star_v = 0.80 * fc_v

    # Resistencia del concreto al cortante (Vcr) simplificada
    Vcr_kg = FR_v * 0.5 * math.sqrt(fc_star_v) * b_v * d_v
    Vcr_ton = Vcr_kg / 1000

    st.markdown("---")
    st.subheader("Resultados de Cortante")
    st.write(f"Resistencia del concreto solo ($V_{{cR}}$): **{Vcr_ton:.2f} Ton**")

    if Vu <= Vcr_ton:
        st.success("✅ El concreto resiste todo el cortante. Solo requieres estribos por especificación mínima.")
        s_max = d_v / 2
        st.info(f"Coloca estribos a una separación máxima de **{s_max:.2f} cm**.")
    else:
        # El acero debe resistir lo que le falta al concreto
        Vsr_ton = Vu - Vcr_ton
        st.warning(f"⚠️ El concreto NO resiste solo. Los estribos deben resistir: **{Vsr_ton:.2f} Ton**")
        
        # Fórmula: Vsr = (FR * Av * fy * d) / s  --> Despejamos 's' (separación)
        Vsr_kg = Vsr_ton * 1000
        separacion = (FR_v * Av * fy_v * d_v) / Vsr_kg
        s_max = d_v / 2
        
        sep_final = min(separacion, s_max)
        
        st.metric("Separación de estribos calculada (s)", f"{sep_final:.1f} cm")
        
        if sep_final < 6.0:
            st.error("❌ La separación es menor a 6 cm (muy juntos para colar). Usa estribos más gruesos (ej. #4) o aumenta la sección.")
        else:
            st.success(f"👷‍♂️ **Recomendación en obra:** Usa estribos del #3 separados a **{math.floor(sep_final)} cm**.")

# ==========================================
# MÓDULO 3: COLUMNAS (Flexocompresión)
# ==========================================
with tab_columnas:
    st.header("Diseño de Columnas (NTC-CDMX)")
    st.caption("Revisión por Flexocompresión y Diagrama de Interacción Simplificado")

    col1_c, col2_c, col3_c = st.columns(3)
    
    with col1_c:
        st.subheader("Materiales y Geometría")
        fc_c = st.number_input("f'c (kg/cm²)", value=250, step=10, key="fc_c")
        fy_c = st.number_input("fy (kg/cm²)", value=4200, step=100, key="fy_c")
        b_c = st.number_input("Base, b (cm)", value=40, step=5, key="b_c")
        h_c = st.number_input("Peralte, h (cm)", value=40, step=5, key="h_c")
        
    with col2_c:
        st.subheader("Acero de Refuerzo")
        num_varillas = st.number_input("Cantidad total de varillas", value=8, step=2, min_value=4)
        area_varilla = st.number_input("Área por varilla (cm²)", value=2.85, help="Ej. Varilla #6 = 2.85 cm²")
        rec_c = st.number_input("Recubrimiento (cm)", value=5, step=1, key="rec_c")

    with col3_c:
        st.subheader("Cargas Actuantes")
        Pu = st.number_input("Carga Axial Última, Pu (Ton)", value=100.0, step=10.0)
        Mu_c = st.number_input("Momento Último, Mu (Ton-m)", value=15.0, step=1.0)

    # 1. Cálculos Preliminares
    Ag = b_c * h_c  # Área bruta de concreto
    Ast = num_varillas * area_varilla  # Área total de acero
    rho_col = Ast / Ag

    FR_c = 0.70  # Factor de resistencia para columnas con estribos (NTC)
    fc_star_c = 0.80 * fc_c
    fc_biprima_c = 0.85 * fc_star_c

    # 2. Validaciones Normativas de Cuantía
    st.markdown("---")
    st.subheader("1. Revisión de Cuantía de Acero")
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Área de Acero Colocada (Ast)", f"{Ast:.2f} cm²", f"ρ = {rho_col:.4f}")
    
    if rho_col < 0.01:
        col_res2.error("❌ Cuantía menor al 1% mínimo (NTC). Aumenta el número o grosor de varillas.")
    elif rho_col > 0.06:
        col_res2.error("❌ Cuantía mayor al 6% máximo (NTC). Mucho acero, la columna estará muy congestionada.")
    else:
        col_res2.success("✅ Cuantía de acero dentro de los límites normativos (1% - 6%).")

    # 3. Puntos Clave del Diagrama de Interacción (Simplificado)
    # Punto 1: Compresión Pura (Po)
    Po_kg = FR_c * ((fc_biprima_c * (Ag - Ast)) + (fy_c * Ast))
    Po_ton = Po_kg / 1000

    # Punto 2: Flexión Pura aproximada (M0) - Asumiendo mitad del acero en tensión
    d_c = h_c - rec_c
    As_tension = Ast / 2
    a_flex = (As_tension * fy_c) / (0.85 * fc_biprima_c * b_c)
    Mo_kgcm = FR_c * As_tension * fy_c * (d_c - (a_flex / 2))
    Mo_tonm = Mo_kgcm / 100000

    # Punto 3: Punto Balanceado (Aproximación educada para el gráfico)
    Pb_ton = Po_ton * 0.4  # Típicamente el punto balanceado ocurre al ~40% de Po
    Mb_tonm = Mo_tonm * 1.5 # El momento balanceado es mayor que el de flexión pura

    # 4. Generación del Gráfico (Diagrama de Interacción)
    st.markdown("---")
    st.subheader("2. Diagrama de Interacción (Aproximado)")
    
    # Creamos los datos para la "Cebolla" del diagrama
    datos_curva = [
        {"Momento (Ton-m)": 0, "Carga Axial (Ton)": Po_ton},          # Compresión Pura
        {"Momento (Ton-m)": Mb_tonm, "Carga Axial (Ton)": Pb_ton},    # Punto Balanceado
        {"Momento (Ton-m)": Mo_tonm, "Carga Axial (Ton)": 0},         # Flexión Pura
    ]
    
    # Mostrar si la carga actual está dentro del límite seguro (simplificado)
    st.write(f"Carga actuante: **Pu = {Pu} Ton** | **Mu = {Mu_c} Ton-m**")
    
    if Pu > Po_ton:
        st.error(f"❌ La columna falla por aplastamiento puro. La resistencia máxima es {Po_ton:.2f} Ton.")
    else:
        st.info("💡 Gráfico de Referencia: Si tu punto (Mu, Pu) queda 'debajo' de la curva imaginaria entre los puntos máximos, la columna es segura.")
        st.line_chart(datos_curva, x="Momento (Ton-m)", y="Carga Axial (Ton)")

# ==========================================
# MÓDULO 4: MAMPOSTERÍA
# ==========================================
with tab_mamposteria:
    st.header("Diseño de Muros de Mampostería (NTC-CDMX)")
    st.caption("Revisión por Carga Vertical (Gravedad) y Cortante en el Plano (Sismo)")

    col1_m, col2_m, col3_m = st.columns(3)

    with col1_m:
        st.subheader("Geometría del Muro")
        L = st.number_input("Longitud del muro, L (m)", value=3.0, step=0.1)
        H = st.number_input("Altura libre, H (m)", value=2.5, step=0.1)
        t = st.number_input("Espesor del muro, t (cm)", value=15.0, step=1.0)

    with col2_m:
        st.subheader("Resistencias de Diseño")
        fm = st.number_input("Compresión mampostería, f*m (kg/cm²)", value=15.0, step=1.0, help="Bloque de concreto hueco: ~15. Ladrillo macizo: ~40.")
        vm = st.number_input("Cortante mampostería, v*m (kg/cm²)", value=3.0, step=0.5, help="Suele variar entre 2.0 y 3.5 dependiendo del mortero y la pieza.")

    with col3_m:
        st.subheader("Fuerzas Actuantes")
        Pu_muro = st.number_input("Carga Vertical Última, Pu (Ton)", value=10.0, step=1.0)
        Vu_muro = st.number_input("Fuerza Cortante Última (Sismo), Vu (Ton)", value=4.0, step=1.0)

    # 1. Propiedades Geométricas
    t_m = t / 100  # Espesor en metros
    AT_m2 = L * t_m  # Área transversal en m²
    AT_cm2 = AT_m2 * 10000  # Área transversal en cm²

    # 2. Revisión por Carga Vertical (Compresión)
    FR_comp = 0.60
    # Factor de reducción por esbeltez y excentricidad (Valor simplificado para muros típicos de vivienda)
    FE = 0.70 
    
    # Ecuación de resistencia a compresión pura: PR = FR * FE * f*m * AT
    PR_kg = FR_comp * FE * fm * AT_cm2
    PR_ton = PR_kg / 1000

    st.markdown("---")
    st.subheader("Resultados de Diseño Estructural")
    
    res_m1, res_m2 = st.columns(2)
    
    with res_m1:
        st.markdown("### 🧱 Revisión por Compresión")
        st.metric("Resistencia Vertical Máxima (PR)", f"{PR_ton:.2f} Ton", f"Carga Actuante: {Pu_muro:.2f} Ton", delta_color="off")
        
        if PR_ton >= Pu_muro:
            st.success("✅ ¡Pasa! El muro es lo suficientemente robusto para soportar el peso de los pisos superiores sin aplastarse.")
        else:
            st.error("❌ El muro falla por compresión. Soluciones: Aumenta la longitud, hazlo más grueso, o cambia a una pieza más resistente (ej. ladrillo macizo).")

    # 3. Revisión por Fuerza Cortante (Sismo)
    FR_cort = 0.70
    
    # Ecuación de resistencia al cortante: VR = FR * (0.5 * v*m * AT + 0.3 * P)
    # Nota: El 0.3 * P representa la fricción. Entre más peso tenga el muro encima, más difícil es que el sismo lo deslice.
    aporte_friccion = 0.3 * (Pu_muro * 1000) 
    VR_kg = FR_cort * ((0.5 * vm * AT_cm2) + aporte_friccion)
    VR_ton = VR_kg / 1000

    with res_m2:
        st.markdown("### 🌪️ Revisión por Cortante (Sismo)")
        st.metric("Resistencia a Cortante (VR)", f"{VR_ton:.2f} Ton", f"Sismo Actuante: {Vu_muro:.2f} Ton", delta_color="off")
        
        if VR_ton >= Vu_muro:
            st.success("✅ ¡Pasa! El muro soporta el sismo. Solo necesita confinamiento estándar (castillos y dalas perimetrales).")
        else:
            st.error("❌ El muro fallará con grietas diagonales por sismo. Soluciones: Necesita acero de refuerzo interior (en las juntas o huecos) o debes hacer un muro más largo.")
