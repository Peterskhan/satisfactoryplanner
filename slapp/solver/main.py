from slapp.solver.production import ProductionPlanner, Recipe, Item
from slapp.solver.solver import Solution, FreeSupply, optimize
from slapp.solver.costs import (
    CostFn,
    MINIMIZE_POWER,
    MINIMIZE_POINTS,
    MINIMIZE_MACHINES,
    MINIMIZE_RESOURCES,
    resource_penalties,
    weighted,
    WeightedCost,
)
from slapp.solver.display import print_results, DisplayMode


def main() -> None:
    ProductionPlanner.load_buildings()
    ProductionPlanner.load_items()
    ProductionPlanner.load_recipes()

    # --- Configuration ---

    use_alternates: bool = True

    cost_fn: CostFn = resource_penalties({
        'Iron Ore':    1.0,
        'Copper Ore':  1.0,
        'Coal':        2.0,
        'Crude Oil':   3.0,
        'Bauxite':     4.0,
        'Raw Quartz':  4.0,
        'Sulfur':      4.0,
        'Caterium Ore': 4.0,
        'Uranium':     10.0,
        'SAM Ore':     10.0,
        'Nitrogen Gas': 3.0,
        'Limestone':   1.0,
        'Water':       0.0,
    })

    cost_fn = MINIMIZE_POWER

    # --- Recipe selection ---

    recipes: list[Recipe] = [
        r for r in ProductionPlanner._recipes.values()
        if use_alternates or not r.is_alternate
    ]

    # --- Solve ---

    free_supplies: list[FreeSupply] = [
        #FreeSupply(item=ProductionPlanner._items_by_name['Rubber'],  quantity=200.0),
        #FreeSupply(item=ProductionPlanner._items_by_name['Plastic'], quantity=180.0),
    ]

    target = ProductionPlanner._items_by_name['Modular Engine']

    solution: Solution | None = optimize(
        recipes=recipes,
        target_item=target,
        target_quantity=5.0,
        cost_fn=cost_fn,
        free_supplies=free_supplies,
    )

    if solution:
        print_results(solution, mode=DisplayMode.FLAT)

if __name__ == '__main__':
    main()