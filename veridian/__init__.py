"""Veridian: a causal worldline lattice for machines that must remember *why*."""

from veridian.budget import EnergyBudget
from veridian.lattice import Lattice
from veridian.merge import merge_belief
from veridian.observation import Observation, Triple
from veridian.query import Query, QueryEngine
from veridian.synthetic import GenerationGuard
from veridian.worldline import Worldline

__all__ = [
    "EnergyBudget",
    "GenerationGuard",
    "Lattice",
    "Observation",
    "Query",
    "QueryEngine",
    "Triple",
    "Worldline",
    "merge_belief",
]
__version__ = "0.2.0"
