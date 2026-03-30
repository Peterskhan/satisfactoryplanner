from dataclasses import dataclass
from typing import Protocol
from slapp.solver.production import Recipe, Building


# --- Protocol ---

class CostFn(Protocol):
    def __call__(self, recipe: Recipe, building: Building) -> float: ...


# --- Weighted combination ---

@dataclass
class WeightedCost:
    fn:     CostFn
    weight: float


def weighted(*terms: WeightedCost) -> CostFn:
    """
    Combine multiple cost functions with weights.

    Usage:
        cost_fn = weighted(
            WeightedCost(MINIMIZE_POWER,    0.7),
            WeightedCost(MINIMIZE_MACHINES, 0.3),
        )
    """
    def combined(recipe: Recipe, building: Building) -> float:
        return sum(t.weight * t.fn(recipe, building) for t in terms)
    return combined


# --- Presets ---

def MINIMIZE_POWER(recipe: Recipe, building: Building) -> float:
    return building.power


def MINIMIZE_MACHINES(recipe: Recipe, building: Building) -> float:
    return 1.0


def MINIMIZE_POINTS(recipe: Recipe, building: Building) -> float:
    return -sum(
        ia.item.sink_points * ia.amount * (60.0 / recipe.duration)
        for ia in recipe.products
    )


def MINIMIZE_RESOURCES(recipe: Recipe, building: Building) -> float:
    return sum(
        ia.amount * (60.0 / recipe.duration)
        for ia in recipe.ingredients
        if ia.item.is_basic
    )

def resource_penalties(penalties: dict[str, float]) -> CostFn:
    """
    Penalize raw resource consumption by item name.

    Items not listed default to 0 (no penalty).

    Usage:
        cost_fn = resource_penalties({
            'Iron Ore':  1.0,
            'Uranium':  10.0,
        })
    """
    def cost(recipe: Recipe, building: Building) -> float:
        return sum(
            penalties.get(ia.item.name, 0.0) * ia.amount * (60.0 / recipe.duration)
            for ia in recipe.ingredients
            if ia.item.is_basic
        )
    return cost