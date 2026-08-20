from __future__ import annotations

from dataclasses import dataclass

from veridian.errors import BudgetExhausted


@dataclass
class EnergyBudget:
    """Hard cap on lattice operations so agent loops cannot run forever.

    Costs are dimensionless "joule-equivalents" — a policy knob, not a
    physics simulation.
    """

    joules: float
    spent: float = 0.0

    def charge(self, cost: float, op: str) -> None:
        if cost < 0:
            raise ValueError("cost must be non-negative")
        if self.spent + cost > self.joules:
            raise BudgetExhausted(
                f"{op} costs {cost:.4f} but only {self.joules - self.spent:.4f} remains"
            )
        self.spent += cost

    def remaining(self) -> float:
        return self.joules - self.spent

    def to_dict(self) -> dict:
        return {"joules": self.joules, "spent": self.spent, "remaining": self.remaining()}
