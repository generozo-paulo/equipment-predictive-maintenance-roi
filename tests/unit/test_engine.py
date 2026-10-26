import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.engine import PredictiveMaintenanceEngine

def test_generate_synthetic_telemetry():
    df = PredictiveMaintenanceEngine.generate_synthetic_telemetry(n_equipment=10, days=60)
    assert len(df) > 0
    assert "tube_temperature_celsius" in df.columns
    assert "vibration_amplitude_g" in df.columns
    assert "failure_event" in df.columns
    assert df["tube_temperature_celsius"].mean() > 40.0

def test_kaplan_meier_survival():
    df = PredictiveMaintenanceEngine.generate_synthetic_telemetry(n_equipment=20, days=90)
    km_curve = PredictiveMaintenanceEngine.calculate_kaplan_meier_survival(df)
    assert len(km_curve) > 0
    assert "survival_probability" in km_curve.columns
    # A curva deve ser monotônica decrescente ou constante (entre 0 e 1)
    probs = km_curve["survival_probability"].values
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    assert probs[0] >= probs[-1]

def test_financial_roi_computation():
    roi = PredictiveMaintenanceEngine.compute_financial_roi(
        n_equipment=25,
        unplanned_failures=18,
        preventive_success_rate=0.85,
        avg_exam_ticket_brl=450.0,
        daily_exam_capacity=35,
        emergency_repair_cost_brl=45000.0,
        planned_preventive_cost_brl=12000.0,
        avg_downtime_days_emergency=4.0,
        avg_downtime_days_planned=0.5
    )
    assert roi.unplanned_failures_avoided > 10
    assert roi.direct_maintenance_savings_brl > 300000.0
    assert roi.recovered_exam_revenue_brl > 500000.0
    assert roi.total_financial_roi_brl > 800000.0
    assert roi.downtime_reduction_percent > 70.0
