# Spec-Driven Development (SDD) Specification Sheet
## Project: `equipment-predictive-maintenance-roi`

* **Version:** 1.0.0
* **Author:** Paulo Elias Tavares Generozo
* **Domain:** Clinical Engineering, Predictive Maintenance & Financial Analytics (ROI)
* **License:** MIT

---

## 1. Business & Clinical Problem Statement (CRISP-DM Phase 1)

In hospital networks and diagnostic imaging centers, high-value assets like Computed Tomography (CT) scanners and MRI machines cost between R$ 2.5M and R$ 8.0M each.
When a CT tube fails unexpectedly:
1. **Direct Unplanned Downtime Cost:** Emergency technician dispatch, express part freight, and overtime maintenance labor ($R\$\ 8,000 - 15,000$ per incident).
2. **Loss of Exam Revenue:** 30 to 50 scheduled exams canceled per day ($R\$\ 450$ average ticket per CT exam = $R\$\ 13,500 - 22,500$ daily revenue lost).
3. **Clinical Risk:** Delay in critical stroke (*AVC*) and trauma diagnoses in the Emergency Room.

This system combines **Survival Analysis (Kaplan-Meier & Cox Proportional Hazards)** with an **XGBoost Classifier** to predict component failure within 48–72 hours, feeding an interactive **ROI & Financial Loss Prevention Engine**.

---

## 2. Data Contracts & Schemas (Pydantic Models)

### Input Schema (`TelemetryRecord`):
```python
class TelemetryRecord:
    equipment_id: str
    rotation_speed_rpm: float        # Normal range: [120, 240]
    tube_temperature_celsius: float  # Normal: [40, 85], Alert: > 90
    vibration_amplitude_g: float     # Normal: [0.05, 0.45], Alert: > 0.60
    accumulated_scan_seconds: float  # Total exposure time
    oil_pressure_kpa: float          # Normal: [180, 260]
    daily_exam_volume: int           # Daily patient scans
```

### Financial Metric Output Schema (`ROIAnalysisResult`):
```python
class ROIAnalysisResult:
    total_equipment_monitored: int
    unplanned_failures_avoided: int
    direct_maintenance_savings_brl: float
    recovered_exam_revenue_brl: float
    total_financial_roi_brl: float
    downtime_reduction_percent: float
```

---

## 3. Performance & Quality Targets (SLAs)

* **Predictive Recall:** $\ge 85\%$ for failure detection within a 48h advance window.
* **Economic Precision:** Clear separation between preventive replacement cost ($R\$\ 12,000$) vs. emergency corrective cost ($R\$\ 45,000$).
* **Unit Test Coverage:** $\ge 90\%$ on survival curves and economic calculations.
