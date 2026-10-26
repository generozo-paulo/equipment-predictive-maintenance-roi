import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engine import PredictiveMaintenanceEngine

st.set_page_config(
    page_title="Equipment Predictive Maintenance & ROI Engine",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Manutenção Preditiva & Calculadora de ROI Hospitalar")
st.markdown("""
Plataforma analítica para predição de falhas em tomógrafos computadorizados (**CT Scanners**) e equipamentos de suporte à vida, integrando **Análise de Sobrevivência (Kaplan-Meier)** e cálculo direto de **Retorno sobre o Investimento (ROI)**.
""")

tabs = st.tabs(["💰 1. Calculadora Executiva de ROI", "📈 2. Análise de Sobrevivência (Kaplan-Meier)", "📡 3. Telemetria de Sensores em Tempo Real"])

# -------------------------------------------------------------
# TAB 1: Calculadora de ROI
# -------------------------------------------------------------
with tabs[0]:
    st.header("Simulador de Impacto Financeiro e Mitigação de Downtime")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parâmetros do Parque Tecnológico")
        n_equip = st.slider("Parque de Tomógrafos Monitorados", min_value=5, max_value=100, value=25, step=5)
        failures_year = st.slider("Histórico de Falhas Críticas / Ano (Parque Total)", min_value=2, max_value=40, value=18, step=1)
        preventive_success = st.slider("Acurácia da IA na Prevenção de Falhas (%)", min_value=50, max_value=99, value=85, step=5) / 100.0
        
        st.subheader("Custos Assistenciais e Operacionais")
        ticket = st.number_input("Valor Médio de Exame de Tomografia (R$)", value=450.0, step=50.0)
        daily_capacity = st.number_input("Capacidade de Exames por Sala/Dia", value=35, step=5)
        emergency_cost = st.number_input("Custo Médio de Manutenção Corretiva Emergencial (R$)", value=45000.0, step=5000.0)
        planned_cost = st.number_input("Custo Médio de Manutenção Preventiva Agendada (R$)", value=12000.0, step=2000.0)
        
        roi_res = PredictiveMaintenanceEngine.compute_financial_roi(
            n_equipment=n_equip,
            unplanned_failures=failures_year,
            preventive_success_rate=preventive_success,
            avg_exam_ticket_brl=ticket,
            daily_exam_capacity=daily_capacity,
            emergency_repair_cost_brl=emergency_cost,
            planned_preventive_cost_brl=planned_cost
        )
        
    with col2:
        st.subheader("Retorno Financeiro e Eficiência Clínica")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Falhas Críticas Evitadas", f"{roi_res.unplanned_failures_avoided} equip.")
        k2.metric("Redução de Downtime", f"{roi_res.downtime_reduction_percent:.1f}%")
        k3.metric("ROI Financeiro Total", f"R$ {roi_res.total_financial_roi_brl:,.2f}")
        
        # Gráfico comparativo de custos
        df_costs = pd.DataFrame({
            "Categoria": ["Economia em Manutenção de Peças", "Receita de Exames Preservada (Sem Ociosidade)"],
            "Valor (R$)": [roi_res.direct_maintenance_savings_brl, roi_res.recovered_exam_revenue_brl]
        })
        fig_bar = px.bar(df_costs, x="Categoria", y="Valor (R$)", color="Categoria", title="Composição da Economia Anual Gerada pela IA", text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.success(f"""
        **Conclusão Executiva:** Com a manutenção preditiva, o hospital deixa de perder **{roi_res.downtime_reduction_percent:.1f}% de tempo de máquina parada**, evitando custos de emergência e gerando uma recuperação financeira líquida de **R$ {roi_res.total_financial_roi_brl:,.2f} anuais**.
        """)

# -------------------------------------------------------------
# TAB 2: Curva de Kaplan-Meier
# -------------------------------------------------------------
with tabs[1]:
    st.header("Curva de Sobrevivência Livre de Falha de Tubos de Raios-X")
    st.write("Estimador não-paramétrico de Kaplan-Meier modelando o tempo até a substituição do tubo em dias de operação contínua.")
    
    df_telemetry = PredictiveMaintenanceEngine.generate_synthetic_telemetry(n_equipment=n_equip, days=180)
    df_km = PredictiveMaintenanceEngine.calculate_kaplan_meier_survival(df_telemetry)
    
    fig_km = px.line(df_km, x="time_days", y="survival_probability", labels={"time_days": "Dias de Operação Contínua", "survival_probability": "Probabilidade de Sobrevivência Sem Falha"}, title="Função de Sobrevivência S(t) do Parque de Tomógrafos")
    fig_km.add_hline(y=0.5, line_dash="dash", line_color="orange", annotation_text="Vida Mediana (50% do parque)")
    st.plotly_chart(fig_km, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: Telemetria de Sensores
# -------------------------------------------------------------
with tabs[2]:
    st.header("Telemetria Contínua de Variáveis Críticas de Degradação")
    
    selected_eq = st.selectbox("Selecione o Tomógrafo para Inspecionar", df_telemetry['equipment_id'].unique())
    sub_df = df_telemetry[df_telemetry['equipment_id'] == selected_eq]
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_temp = px.line(sub_df, x="day", y="tube_temperature_celsius", title=f"Temperatura do Tubo de Raios-X (°C) - {selected_eq}")
        fig_temp.add_hline(y=90.0, line_dash="dash", line_color="red", annotation_text="Limite Crítico (90°C)")
        st.plotly_chart(fig_temp, use_container_width=True)
    with col_t2:
        fig_vib = px.line(sub_df, x="day", y="vibration_amplitude_g", title=f"Vibração do Anel Giratório (G) - {selected_eq}", color_discrete_sequence=['purple'])
        fig_vib.add_hline(y=0.55, line_dash="dash", line_color="red", annotation_text="Limite de Desbalanceamento (0.55 G)")
        st.plotly_chart(fig_vib, use_container_width=True)
