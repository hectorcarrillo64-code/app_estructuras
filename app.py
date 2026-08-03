import streamlit as st
import math

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="App Diseño Estructural", layout="wide", page_icon="🏗️")

st.title("🏗️ Diseño de Estructuras: Concreto y Mampostería")
st.markdown("---")

st.header("Módulo 1: Diseño de Vigas de Concreto por Flexión (NTC-CDMX)")
st.caption("Cálculo de Área de Acero Longitudinal con el Bloque de Whitney")

# 2. INPUTS DE USUARIO (Interfaz)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Materiales")
    fc = st.number_input("f'c - Resistencia del concreto (kg/cm²)", value=250, step=10)
    fy = st.number_input("fy - Fluencia del acero (kg/cm²)", value=4200, step=100)

with col2:
    st.subheader("Geometría de la Sección")
    b = st.number_input("Base, b (cm)", value=30, step=5)
    h = st.number_input("Peralte Total, h (cm)", value=60, step=5)
    rec = st.number_input("Recubrimiento al centroide, r (cm)", value=5, step=1)

with col3:
    st.subheader("Fuerzas Internas")
    Mu = st.number_input("Momento Último factorizado, Mu (Ton-m)", value=25.0, step=1.0)
    
# 3. LÓGICA DE CÁLCULO (Motor Estructural)
d = h - rec  # Peralte efectivo

# Factores según NTC-CDMX
FR = 0.90 # Factor de resistencia para flexión
fc_star = 0.80 * fc # NTC: f*c = 0.80 f'c
fc_biprima = 0.85 * fc_star # NTC: f''c = 0.85 f*c

# Factor Beta 1 (Depende de la resistencia del concreto)
if fc <= 280:
    beta1 = 0.85
else:
    beta1 = max(0.65, 1.05 - (fc / 1400))

# Cuantías Reglamentarias
# Cuantía Mínima (NTC)
rho_min = (0.7 * math.sqrt(fc)) / fy 

# Cuantía Balanceada
rho_b = (fc_biprima / fy) * ((6000 * beta1) / (6000 + fy))

# Cuantía Máxima (Usamos 0.75 rho_b para garantizar ductilidad en zonas sísmicas como BC)
rho_max = 0.75 * rho_b 

# Cálculo del Área de Acero (As) para el Mu solicitado
Mu_kgcm = Mu * 100000 # Conversión de Ton-m a kg-cm

# Constante de la ecuación cuadrática del bloque de Whitney
# Ecuación: Mu = FR * b * d^2 * f''c * q(1 - 0.5q)
coeficiente = Mu_kgcm / (FR * b * (d**2) * fc_biprima)

try:
    # Resolviendo para 'q' (índice de refuerzo)
    q = 1 - math.sqrt(1 - (2 * coeficiente))
    rho_req = q * (fc_biprima / fy)
    As_req = rho_req * b * d
    
    As_min_cm2 = rho_min * b * d
    As_max_cm2 = rho_max * b * d
    
    # 4. SALIDA DE RESULTADOS Y ALERTAS VISUALES
    st.markdown("---")
    st.subheader("Resultados del Diseño")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Acero Mínimo", f"{As_min_cm2:.2f} cm²", f"ρ = {rho_min:.4f}")
    res_col2.metric("Acero Requerido (As)", f"{As_req:.2f} cm²", f"ρ = {rho_req:.4f}")
    res_col3.metric("Acero Máximo (Dúctil)", f"{As_max_cm2:.2f} cm²", f"ρ = {rho_max:.4f}")
    
    # Validaciones Normativas (Verde = Pasa, Rojo = Falla)
    if rho_req < rho_min:
        st.warning(f"⚠️ El acero requerido es menor al mínimo normativo. Debes colocar **{As_min_cm2:.2f} cm²** por reglamento.")
    elif rho_req > rho_max:
        st.error(f"❌ ¡Falla! La sección está sobre-reforzada (falla frágil). Debes aumentar la geometría (b, h) o diseñar como viga doblemente reforzada.")
    else:
        st.success(f"✅ ¡Diseño Satisfactorio! La viga es simplemente reforzada y cumple los criterios de ductilidad.")

except ValueError:
    st.error("❌ El Momento Último es demasiado grande para esta sección transversal. La raíz cuadrada es imaginaria. ¡Aumenta el peralte (h) o la base (b)!")
