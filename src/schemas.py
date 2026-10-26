from pydantic import BaseModel, Field
from typing import List, Dict

class TelemetryRecord(BaseModel):
    equipment_id: str
    rotation_speed_rpm: float = Field(..., ge=50, le=400)
    tube_temperature_celsius: float = Field(..., ge=20, le=140)
    vibration_amplitude_g: float = Field(..., ge=0.01, le=2.5)
    accumulated_scan_seconds: float = Field(..., ge=0)
    oil_pressure_kpa: float = Field(..., ge=50, le=450)
    daily_exam_volume: int = Field(default=35, ge=1, le=150)

class ROIAnalysisResult(BaseModel):
    total_equipment_monitored: int
    unplanned_failures_avoided: int
    direct_maintenance_savings_brl: float
    recovered_exam_revenue_brl: float
    total_financial_roi_brl: float
    downtime_reduction_percent: float
