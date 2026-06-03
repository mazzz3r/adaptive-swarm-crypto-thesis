from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class BenchmarkMode(str, Enum):
    STATIC_HEAVY = "static-heavy"
    STATIC_BALANCED = "static-balanced"
    STATIC_LIGHTWEIGHT = "static-lightweight"
    ADAPTIVE = "adaptive"


class RuntimeProfile(str, Enum):
    HEAVY = "heavy"
    BALANCED = "balanced"
    LIGHTWEIGHT = "lightweight"


class ScheduledValue(BaseModel):
    at_s: float = Field(ge=0)
    value: float = Field(ge=0)


class NetworkConfig(BaseModel):
    delay_ms: float = Field(default=0, ge=0)
    jitter_ms: float = Field(default=0, ge=0)
    loss_pct: float = Field(default=0, ge=0, le=100)


class ResourceLimits(BaseModel):
    cpu_limit_cores: float | None = Field(default=None, gt=0)
    memory_limit_mb: int | None = Field(default=None, gt=0)


class Scenario(BaseModel):
    name: str
    mode: BenchmarkMode
    duration_s: float = Field(gt=0)
    message_rate_hz: float = Field(gt=0)
    message_size_bytes: int = Field(gt=0)
    peer_count: int = Field(ge=2)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    resources: ResourceLimits = Field(default_factory=ResourceLimits)
    threat_schedule: list[ScheduledValue] = Field(default_factory=lambda: [ScheduledValue(at_s=0, value=0.1)])
    energy_schedule: list[ScheduledValue] = Field(default_factory=lambda: [ScheduledValue(at_s=0, value=1.0)])
    rekey_interval_s: float = Field(gt=0)
    tags: list[str] = Field(default_factory=list)

    @field_validator("threat_schedule", "energy_schedule")
    @classmethod
    def _ensure_non_empty(cls, value: list[ScheduledValue]) -> list[ScheduledValue]:
        if not value:
            raise ValueError("schedule must not be empty")
        return value

    @model_validator(mode="after")
    def _validate_schedule_order(self) -> "Scenario":
        for schedule_name in ("threat_schedule", "energy_schedule"):
            schedule = getattr(self, schedule_name)
            ordered = sorted(schedule, key=lambda item: item.at_s)
            if ordered[0].at_s != 0:
                ordered.insert(0, ScheduledValue(at_s=0, value=ordered[0].value))
            setattr(self, schedule_name, ordered)
        return self


def load_scenario(path: str | Path) -> Scenario:
    scenario_path = Path(path)
    payload = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"scenario file {scenario_path} does not contain a mapping")
    return Scenario.model_validate(payload)
