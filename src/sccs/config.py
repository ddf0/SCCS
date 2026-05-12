"""Strongly-typed YAML configuration.

Pydantic v2 schema. Errors at load time are explicit and pinpoint the
offending key — much friendlier than ``KeyError`` halfway through
initialisation.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class I2CConfig(BaseModel):
    bus: int = Field(ge=0, le=7)
    hccd_address: int = Field(ge=0x08, le=0x77)
    magnetometer_address: int = Field(ge=0x08, le=0x77)


class PIDConfig(BaseModel):
    kp: float = Field(ge=0.0)
    ki: float = Field(ge=0.0)
    kd: float = Field(ge=0.0)
    dt_ms: PositiveInt
    current_limit_a: PositiveFloat


class ControlConfig(BaseModel):
    loop_period_ms: PositiveInt
    max_consecutive_errors: PositiveInt


class WebConfig(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    update_interval_ms: PositiveInt


class SCCSConfig(BaseModel):
    i2c: I2CConfig
    pid: PIDConfig
    control: ControlConfig
    web: WebConfig


def load_config(path: str | Path) -> SCCSConfig:
    """Load and validate a YAML config file."""
    raw = yaml.safe_load(Path(path).read_text())
    return SCCSConfig.model_validate(raw)
