"""Carga de config/instruments.yaml (compartida por los nodos de voz y detección)."""
from __future__ import annotations

import os
from typing import Dict

import yaml


def default_instruments_path() -> str:
    from ament_index_python.packages import get_package_share_directory
    return os.path.join(get_package_share_directory('surgical_assistant'), 'config', 'instruments.yaml')


def load_instruments_config(path: str = '') -> Dict:
    """Devuelve el dict del YAML. Si `path` está vacío usa el instalado en share/."""
    if not path:
        path = default_instruments_path()
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault('default_alpha_m', 0.0)
    cfg.setdefault('instruments', {})
    return cfg
