import math
from scipy.optimize import linprog
from slapp.core.production import Recipe, Item, Building, ProductionPlanner

# --- solver.py

def solve(flow_matrix, target, costs, free_source_indices=None):
    free_source_indices = free_source_indices or set()
    n_items, n_recipes = len(flow_matrix), len(flow_matrix[0])

    A_ub, b_ub = [], []

    for item_idx in range(n_items):
        if item_idx in free_source_indices:
            continue  # no balance constraint — freely available
        row = [-flow_matrix[item_idx][r] for r in range(n_recipes)]
        rhs = -target.get(item_idx, 0)
        A_ub.append(row)
        b_ub.append(rhs)

    bounds = [(0, None)] * n_recipes
    result = linprog(costs, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    return {
        "scales":  result.x.tolist() if result.success else [],
        "success": result.success,
        "message": result.message,
    }

# --- builder.py

def get_automated_building(recipe):
    return recipe.produced_in[0] if recipe.produced_in else None

def build_lp_inputs(recipes, target_item, target_quantity, cost_fn):
    valid_recipes = [r for r in recipes if get_automated_building(r) is not None]

    all_items = set()
    for recipe in valid_recipes:
        all_items.update([ia.item for ia in recipe.ingredients])
        all_items.update([ia.item for ia in recipe.products])

    item_index   = {item: i for i, item in enumerate(sorted(all_items, key=lambda x: x.name))}
    recipe_index = {recipe: i for i, recipe in enumerate(valid_recipes)}

    n_items   = len(item_index)
    n_recipes = len(recipe_index)

    flow_matrix = [[0.0] * n_recipes for _ in range(n_items)]

    for recipe, r_idx in recipe_index.items():
        per_minute = 60.0 / recipe.duration
        for ia in recipe.ingredients:
            flow_matrix[item_index[ia.item]][r_idx] -= ia.amount * per_minute
        for ia in recipe.products:
            flow_matrix[item_index[ia.item]][r_idx] += ia.amount * per_minute

    costs = [cost_fn(recipe, get_automated_building(recipe))
             for recipe, _ in sorted(recipe_index.items(), key=lambda x: x[1])]

    target_dict = {item_index[target_item]: target_quantity}

    # Use is_basic to mark freely available items
    free_source_indices = {item_index[item] for item in all_items if item.is_basic}

    return flow_matrix, target_dict, costs, item_index, recipe_index, free_source_indices

# --- optimizer.py

def optimize(recipes, target_item, target_quantity, cost_fn):
    flow_matrix, target_dict, costs, item_index, recipe_index, free_source_indices = build_lp_inputs(
        recipes, target_item, target_quantity, cost_fn
    )

    result = solve(flow_matrix, target_dict, costs, free_source_indices)

    if not result["success"]:
        print(f"Solver failed: {result['message']}")
        return None

    return {
        "scales":       result["scales"],
        "flow_matrix":  flow_matrix,
        "item_index":   item_index,
        "recipe_index": recipe_index,
    }

def build_production_graph(solution, target_item):
    scales       = solution["scales"]
    flow_matrix  = solution["flow_matrix"]
    item_index   = solution["item_index"]
    recipe_index = solution["recipe_index"]

    index_to_item   = {i: item   for item,   i in item_index.items()}
    index_to_recipe = {i: recipe for recipe, i in recipe_index.items()}

    # Only recipes the solver actually used
    active = {r_idx: scale for r_idx, scale in enumerate(scales) if scale > 1e-6}

    # Build nodes
    nodes = {}
    for r_idx, scale in active.items():
        recipe   = index_to_recipe[r_idx]
        building = get_automated_building(recipe)
        per_min  = 60.0 / recipe.duration

        nodes[recipe] = {
            "scale":    scale,
            "machines": math.ceil(scale),
            "building": building.name,
            "inputs":   {ia.item: ia.amount * per_min * scale for ia in recipe.ingredients},
            "outputs":  {ia.item: ia.amount * per_min * scale for ia in recipe.products},
        }

    # Build edges and identify raw resource consumption
    edges = []         # (producer_recipe, consumer_recipe, item, qty_per_min)
    raw_resources = {} # {item: qty_per_min}

    for item_idx, item in index_to_item.items():
        producers = [(r_idx, scale) for r_idx, scale in active.items()
                     if flow_matrix[item_idx][r_idx] * scale > 1e-6]
        consumers = [(r_idx, scale) for r_idx, scale in active.items()
                     if flow_matrix[item_idx][r_idx] * scale < -1e-6]

        if not consumers:
            continue

        if not producers:
            # Nothing produces it → raw resource
            total = sum(-flow_matrix[item_idx][r_idx] * scale for r_idx, scale in consumers)
            raw_resources[item] = total
            continue

        for p_idx, p_scale in producers:
            for c_idx, c_scale in consumers:
                qty = flow_matrix[item_idx][p_idx] * p_scale
                edges.append((
                    index_to_recipe[p_idx],
                    index_to_recipe[c_idx],
                    item,
                    qty,
                ))

    return nodes, edges, raw_resources

def is_tree(edges):
    producer_counts = {}
    for producer, _, item, _ in edges:
        producer_counts[item] = producer_counts.get(item, 0) + 1
    return all(v == 1 for v in producer_counts.values())


def print_flat(nodes, edges, raw_resources, target_item, target_quantity):
    # Build lookup tables for connections
    # producer_of[item] = recipe that produces it
    # consumers_of[item] = list of recipes that consume it
    producer_of  = {}
    consumers_of = {}
    for producer, consumer, item, qty in edges:
        producer_of[item]  = (producer, qty)
        consumers_of.setdefault(item, []).append((consumer, qty))

    print(f"\n{'─' * 70}")
    print(f"  TARGET: {target_item.name} @ {target_quantity:.1f} /min")
    print(f"{'─' * 70}\n")

    for recipe, node in nodes.items():
        print(f"  {recipe.name:<40}  ×{node['machines']}  ({node['scale']:.2f})  {node['building']}")

        # Inputs
        for item, qty in node["inputs"].items():
            if item in raw_resources:
                print(f"    ← {item.name:<30} {qty:>8.1f} /min  [raw]")
            elif item in producer_of:
                source_recipe, _ = producer_of[item]
                print(f"    ← {item.name:<30} {qty:>8.1f} /min  from: {source_recipe.name}")
            else:
                print(f"    ← {item.name:<30} {qty:>8.1f} /min  [?]")

        # Outputs
        for item, qty in node["outputs"].items():
            destinations = consumers_of.get(item, [])
            if not destinations:
                print(f"    → {item.name:<30} {qty:>8.1f} /min  [target output]")
            else:
                dest_names = ", ".join(r.name for r, _ in destinations)
                print(f"    → {item.name:<30} {qty:>8.1f} /min  to: {dest_names}")

        print()

    print(f"  RAW RESOURCES")
    print(f"  {'─' * 57}")
    for item, qty in raw_resources.items():
        print(f"  {item.name:<35} {qty:>9.1f} /min")
    print()

def print_tree(nodes, edges, raw_resources, target_item, target_quantity):
    # Build lookup: recipe -> list of (producer_recipe, item, qty)
    children = {recipe: [] for recipe in nodes}
    for producer, consumer, item, qty in edges:
        if consumer in children:
            children[consumer].append((producer, item, qty))

    # Root is the recipe that produces the target item
    root = next(r for r, node in nodes.items() if target_item in node["outputs"])

    def render(recipe, indent=0):
        node   = nodes[recipe]
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{recipe.name}  ×{node['machines']}  ({node['building']})")

        for producer, item, qty in children[recipe]:
            print("  " * (indent + 1) + f"[{item.name}: {qty:.1f} /min]")
            render(producer, indent + 1)

        # Raw resource inputs
        for item, qty in node["inputs"].items():
            if item in raw_resources:
                print("  " * (indent + 1) + f"[{item.name}: {qty:.1f} /min]")
                print("  " * (indent + 2) + f"└─ {item.name}  (raw resource)")

    print(f"\n{'─' * 60}")
    print(f"  TARGET: {target_item.name} @ {target_quantity:.1f} /min")
    print(f"{'─' * 60}\n")
    render(root)
    print()


def print_results(solution, target_item, target_quantity):
    if solution is None:
        print("No solution found.")
        return

    nodes, edges, raw_resources = build_production_graph(solution, target_item)

    if is_tree(edges):
        print_tree(nodes, edges, raw_resources, target_item, target_quantity)
    else:
        print_flat(nodes, edges, raw_resources, target_item, target_quantity)

# --- main.py

ProductionPlanner.load_buildings()
ProductionPlanner.load_items()
ProductionPlanner.load_recipes()

my_recipes = [r for r in ProductionPlanner._recipes.values() if not r.is_alternate]
target = ProductionPlanner._items_by_name['Heavy Modular Frame']

my_recipes.append(ProductionPlanner._recipes_by_name['Cast Screws'])

solution = optimize(
    recipes=my_recipes,
    target_item=target,
    target_quantity=1,
    cost_fn=lambda r, b: 1
)

print_results(solution, target, 30)