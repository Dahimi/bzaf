"""Dataset converters. Each `load_*` function returns a list of `bzaf.schema.Item`."""
from .ecthr import load_ecthr
from .goemotions import load_goemotions
from .nlupp import load_nlupp
from .sata import load_sata
from .synthetic import load_synthetic
from .unfair_tos import load_unfair_tos
from .wide import load_wide

LOADERS = {
    "sata": load_sata,
    "goemotions": load_goemotions,
    "unfair_tos": load_unfair_tos,
    "synthetic": load_synthetic,
    "nlupp": load_nlupp,
    "ecthr": load_ecthr,
    "wide": load_wide,
}

__all__ = ["LOADERS", "load_ecthr", "load_goemotions", "load_nlupp", "load_sata", "load_synthetic", "load_unfair_tos", "load_wide"]
