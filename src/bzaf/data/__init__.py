"""Dataset converters. Each `load_*` function returns a list of `bzaf.schema.Item`."""
from .goemotions import load_goemotions
from .sata import load_sata
from .synthetic import load_synthetic
from .unfair_tos import load_unfair_tos

LOADERS = {
    "sata": load_sata,
    "goemotions": load_goemotions,
    "unfair_tos": load_unfair_tos,
    "synthetic": load_synthetic,
}

__all__ = ["LOADERS", "load_goemotions", "load_sata", "load_synthetic", "load_unfair_tos"]
