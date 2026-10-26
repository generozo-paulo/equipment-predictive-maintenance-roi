import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from src.schemas import ROIAnalysisResult

class PredictiveMaintenanceEngine:
    """
    Motor Preditivo e Analisador de ROI para Ativos Hospitalares Críticos (Tomógrafos e Ressonâncias).
    """

    @staticmethod
    def generate_synthetic_telemetry(n_equipment: int = 50, days: int = 180, seed: int = 42) -> pd.DataFrame:
        """Gera histórico sintético realista de telemetria hospitalar com falhas por degradação."""
        np.random.seed(seed)
        records = []
        
        for eq_id in range(1, n_equipment + 1):
            base_temp = np.random.uniform(50, 65)
            base_vib = np.random.uniform(0.10, 0.25)
            low_bound = max(10, int(days * 0.3))
            high_bound = max(low_bound + 5, days - 5)
            degradation_start = np.random.randint(low_bound, high_bound)
            
            for day in range(1, days + 1):
                is_degrading = day >= degradation_start
                deg_factor = (day - degradation_start) * 0.15 if is_degrading else 0
                
                temp = base_temp + deg_factor * 1.8 + np.random.normal(0, 2)
                vib = base_vib + deg_factor * 0.035 + np.random.normal(0, 0.02)
                pressure = max(80, 220 - deg_factor * 3 + np.random.normal(0, 5))
                scans = int(np.random.poisson(35))
                
                # Falha iminente se vibração e temperatura ultrapassarem thresholds críticos
                failure_event = 1 if (temp > 92 and vib > 0.55) else 0
                
                records.append({
                    "equipment_id": f"TOMO-HC-{eq_id:03d}",
                    "day": day,
                    "tube_temperature_celsius": float(temp),
                    "vibration_amplitude_g": float(vib),
                    "oil_pressure_kpa": float(pressure),
                    "daily_exam_volume": scans,
                    "failure_event": failure_event
                })
                if failure_event == 1:
                    break
                    
        return pd.DataFrame(records)

    @staticmethod
    def calculate_kaplan_meier_survival(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula a probabilidade de sobrevivência livre de falhas (método de Kaplan-Meier manual/analítico)."""
        grouped = df.groupby('equipment_id').agg(
            duration=('day', 'max'),
            event=('failure_event', 'max')
        ).reset_index()

        times = np.sort(grouped['duration'].unique())
        n_at_risk = len(grouped)
        survival_prob = 1.0
        curve = []

        for t in times:
            d_i = np.sum((grouped['duration'] == t) & (grouped['event'] == 1))
            c_i = np.sum((grouped['duration'] == t) & (grouped['event'] == 0))
            if n_at_risk > 0:
                survival_prob *= (1.0 - (d_i / n_at_risk))
            curve.append({
                "time_days": int(t),
                "at_risk": int(n_at_risk),
                "failures": int(d_i),
                "survival_probability": float(survival_prob)
            })
            n_at_risk -= (d_i + c_i)

        return pd.DataFrame(curve)

    @staticmethod
    def compute_financial_roi(
        n_equipment: int,
        unplanned_failures: int,
        preventive_success_rate: float = 0.85,
        avg_exam_ticket_brl: float = 450.0,
        daily_exam_capacity: int = 35,
        emergency_repair_cost_brl: float = 45000.0,
        planned_preventive_cost_brl: float = 12000.0,
        avg_downtime_days_emergency: float = 4.0,
        avg_downtime_days_planned: float = 0.5
    ) -> ROIAnalysisResult:
        """
        Calcula o impacto financeiro (ROI) e a redução de downtime com manutenção preditiva.
        """
        failures_avoided = int(np.floor(unplanned_failures * preventive_success_rate))
        
        # 1. Economia direta em manutenção de peças e mão-de-obra emergencial
        cost_without_ai = unplanned_failures * emergency_repair_cost_brl
        cost_with_ai = (unplanned_failures - failures_avoided) * emergency_repair_cost_brl + (failures_avoided * planned_preventive_cost_brl)
        direct_savings = float(cost_without_ai - cost_with_ai)

        # 2. Receita de exames recuperada (evitando salas ociosas)
        lost_days_emergency = failures_avoided * avg_downtime_days_emergency
        lost_days_planned = failures_avoided * avg_downtime_days_planned
        saved_downtime_days = lost_days_emergency - lost_days_planned
        recovered_revenue = float(saved_downtime_days * daily_exam_capacity * avg_exam_ticket_brl)

        total_roi = direct_savings + recovered_revenue
        
        # Redução percentual de tempo de inatividade
        total_days_baseline = unplanned_failures * avg_downtime_days_emergency
        downtime_reduction = (saved_downtime_days / total_days_baseline * 100) if total_days_baseline > 0 else 0.0

        return ROIAnalysisResult(
            total_equipment_monitored=n_equipment,
            unplanned_failures_avoided=failures_avoided,
            direct_maintenance_savings_brl=direct_savings,
            recovered_exam_revenue_brl=recovered_revenue,
            total_financial_roi_brl=total_roi,
            downtime_reduction_percent=float(downtime_reduction)
        )
