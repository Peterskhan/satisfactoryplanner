import math
from dataclasses import dataclass
from scipy.optimize import linprog
from slapp.solver.production import Recipe, Item, Building
from slapp.solver.costs import CostFn


# --- Types ---

FlowMatrix = list[list[float]]
ItemIndex = dict[Item, int]
RecipeIndex = dict[Recipe, int]


@dataclass
class FreeSupply:
    item:     Item
    quantity: float   # per minute


@dataclass
class LPInputs:
    flow_matrix:          FlowMatrix
    target_dict:          dict[int, float]
    costs:                list[float]
    item_index:           ItemIndex
    recipe_index:         RecipeIndex
    free_source_indices:  set[int]
    supply_bounds:        list[tuple[float, float | None]]


@dataclass
class SolverResult:
    scales:  list[float]
    success: bool
    message: str


@dataclass
class Solution:
    scales:          list[float]
    flow_matrix:     FlowMatrix
    item_index:      ItemIndex
    recipe_index:    RecipeIndex
    target_item:     Item
    target_quantity: float
    cost_fn:         CostFn
    free_supplies:   list[FreeSupply]


# --- Helpers ---

def get_automated_building(recipe: Recipe) -> Building | None:
    """Return the first automated building for a recipe, or None."""
    return recipe.produced_in[0] if recipe.produced_in else None


# --- LP builder ---

def build_lp_inputs(
    recipes:          list[Recipe],
    target_item:      Item,
    target_quantity:  float,
    cost_fn:          CostFn,
    free_supplies:    list[FreeSupply] | None = None,
) -> LPInputs:

    free_supplies = free_supplies or []

    valid_recipes: list[Recipe] = [r for r in recipes if get_automated_building(r) is not None]

    all_items: set[Item] = set()
    for recipe in valid_recipes:
        all_items.update([ia.item for ia in recipe.ingredients])
        all_items.update([ia.item for ia in recipe.products])

    item_index:   ItemIndex   = {item: i for i, item in enumerate(sorted(all_items, key=lambda x: x.name))}
    recipe_index: RecipeIndex = {recipe: i for i, recipe in enumerate(valid_recipes)}

    n_items:   int = len(item_index)
    n_recipes: int = len(recipe_index)

    flow_matrix: FlowMatrix = [[0.0] * n_recipes for _ in range(n_items)]

    for recipe, r_idx in recipe_index.items():
        per_minute: float = 60.0 / recipe.duration
        for ia in recipe.ingredients:
            flow_matrix[item_index[ia.item]][r_idx] -= ia.amount * per_minute
        for ia in recipe.products:
            flow_matrix[item_index[ia.item]][r_idx] += ia.amount * per_minute

    costs: list[float] = [
        cost_fn(recipe, get_automated_building(recipe))
        for recipe, _ in sorted(recipe_index.items(), key=lambda x: x[1])
    ]

    # --- Inject capped free supply columns ---
    # Each free supply adds one column to the flow matrix with:
    #   - +1.0 flow for its item (it produces that item)
    #   - 0.0 cost
    #   - upper bound = the specified quantity
    supply_bounds: list[tuple[float, float | None]] = []

    for supply in free_supplies:
        if supply.item not in item_index:
            continue
        col: list[float] = [0.0] * n_items
        col[item_index[supply.item]] = 1.0
        for row_idx in range(n_items):
            flow_matrix[row_idx].append(col[row_idx])
        costs.append(0.0)
        supply_bounds.append((0.0, supply.quantity))

    target_dict: dict[int, float] = {item_index[target_item]: target_quantity}

    free_source_indices: set[int] = {item_index[item] for item in all_items if item.is_basic}

    return LPInputs(
        flow_matrix=flow_matrix,
        target_dict=target_dict,
        costs=costs,
        item_index=item_index,
        recipe_index=recipe_index,
        free_source_indices=free_source_indices,
        supply_bounds=supply_bounds,
    )


# --- Solver ---

def solve(lp: LPInputs) -> SolverResult:
    n_items:   int = len(lp.flow_matrix)
    n_recipes: int = len(lp.flow_matrix[0])

    A_ub: list[list[float]] = []
    b_ub: list[float]       = []

    for item_idx in range(n_items):
        if item_idx in lp.free_source_indices:
            continue
        row: list[float] = [-lp.flow_matrix[item_idx][r] for r in range(n_recipes)]
        rhs: float       = -lp.target_dict.get(item_idx, 0.0)
        A_ub.append(row)
        b_ub.append(rhs)

    # Recipe columns are unbounded above, supply columns are capped
    bounds: list[tuple[float, float | None]] = (
        [(0.0, None)] * len(lp.recipe_index) + lp.supply_bounds
    )

    result = linprog(lp.costs, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    return SolverResult(
        scales=result.x.tolist() if result.success else [],
        success=result.success,
        message=result.message,
    )


# --- Entry point ---

def optimize(
    recipes:       list[Recipe],
    target_item:   Item,
    target_quantity: float,
    cost_fn:       CostFn,
    free_supplies: list[FreeSupply] | None = None,
) -> Solution | None:

    lp:     LPInputs     = build_lp_inputs(recipes, target_item, target_quantity, cost_fn, free_supplies)
    result: SolverResult = solve(lp)

    if not result.success:
        print(f"Solver failed: {result.message}")
        return None

    return Solution(
        scales=result.scales,
        flow_matrix=lp.flow_matrix,
        item_index=lp.item_index,
        recipe_index=lp.recipe_index,
        target_item=target_item,
        target_quantity=target_quantity,
        cost_fn=cost_fn,
        free_supplies=free_supplies or [],
    )