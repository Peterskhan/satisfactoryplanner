import math
from dataclasses import dataclass
from enum import Enum, auto

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from slapp.solver.production import Recipe, Item, Building
from slapp.solver.solver import Solution, get_automated_building

console: Console = Console()

DISPLAY_WIDTH: int = 150

# --- Types ---

@dataclass
class RecipeNode:
    recipe:   Recipe
    scale:    float
    machines: int
    building: str
    inputs:   dict[Item, float]   # item -> qty per minute at this scale
    outputs:  dict[Item, float]   # item -> qty per minute at this scale
    power:    float               # MW at this scale


@dataclass
class ProductionEdge:
    producer: Recipe
    consumer: Recipe
    item:     Item
    quantity: float               # per minute


@dataclass
class ProductionGraph:
    nodes:         dict[Recipe, RecipeNode]
    edges:         list[ProductionEdge]
    raw_resources: dict[Item, float]   # item -> qty per minute
    byproducts:    dict[Item, float]   # item -> qty per minute


# --- Graph construction ---

def build_production_graph(solution: Solution) -> ProductionGraph:
    index_to_item:   dict[int, Item]   = {i: item   for item,   i in solution.item_index.items()}
    index_to_recipe: dict[int, Recipe] = {i: recipe for recipe, i in solution.recipe_index.items()}

    active: dict[int, float] = {
        r_idx: scale
        for r_idx, scale in enumerate(solution.scales)
        if scale > 1e-6 and r_idx in index_to_recipe
    }

    # Build nodes
    nodes: dict[Recipe, RecipeNode] = {}
    for r_idx, scale in active.items():
        recipe:   Recipe   = index_to_recipe[r_idx]
        building: Building = get_automated_building(recipe)
        per_min:  float    = 60.0 / recipe.duration

        nodes[recipe] = RecipeNode(
            recipe=recipe,
            scale=scale,
            machines=math.ceil(scale),
            building=building.name,
            inputs= {ia.item: ia.amount * per_min * scale for ia in recipe.ingredients},
            outputs={ia.item: ia.amount * per_min * scale for ia in recipe.products},
            power=building.power * scale,
        )

    # Build edges and identify raw resources
    edges:         list[ProductionEdge] = []
    raw_resources: dict[Item, float]    = {}

    for item_idx, item in index_to_item.items():
        producers: list[tuple[int, float]] = [
            (r_idx, scale) for r_idx, scale in active.items()
            if solution.flow_matrix[item_idx][r_idx] * scale > 1e-6
        ]
        consumers: list[tuple[int, float]] = [
            (r_idx, scale) for r_idx, scale in active.items()
            if solution.flow_matrix[item_idx][r_idx] * scale < -1e-6
        ]

        if not consumers:
            continue

        # Net flow: positive means more is produced than consumed
        net: float = sum(
            solution.flow_matrix[item_idx][r_idx] * active[r_idx]
            for r_idx in active
        )

        if not producers or net < -1e-6:
            # More is consumed than produced — the deficit comes from outside
            if producers:
                # Partially covered by production, rest is external input
                total = -net
            else:
                total = sum(
                    -solution.flow_matrix[item_idx][r_idx] * scale
                    for r_idx, scale in consumers
                )
            raw_resources[item] = total
            continue

        for p_idx, _ in producers:
            for c_idx, _ in consumers:
                qty: float = solution.flow_matrix[item_idx][p_idx] * active[p_idx]
                edges.append(ProductionEdge(
                    producer=index_to_recipe[p_idx],
                    consumer=index_to_recipe[c_idx],
                    item=item,
                    quantity=qty,
                ))

    # Byproducts: produced but not consumed and not the target
    consumed_items: set[Item] = {edge.item for edge in edges}
    byproducts: dict[Item, float] = {}
    for node in nodes.values():
        for item, qty in node.outputs.items():
            if item not in consumed_items and item != solution.target_item:
                byproducts[item] = byproducts.get(item, 0.0) + qty

    return ProductionGraph(nodes=nodes, edges=edges, raw_resources=raw_resources, byproducts=byproducts)


# --- Graph analysis ---

def is_tree(graph: ProductionGraph) -> bool:
    """Returns True if no item is produced by more than one recipe."""
    producer_counts: dict[Item, int] = {}
    for edge in graph.edges:
        producer_counts[edge.item] = producer_counts.get(edge.item, 0) + 1
    return all(v == 1 for v in producer_counts.values())


def topological_sort(graph: ProductionGraph) -> list[Recipe]:
    dependencies: dict[Recipe, set[Recipe]] = {recipe: set() for recipe in graph.nodes}

    for edge in graph.edges:
        dependencies[edge.consumer].add(edge.producer)

    sorted_recipes: list[Recipe] = []
    remaining: set[Recipe]       = set(graph.nodes.keys())

    while remaining:
        ready: set[Recipe] = {
            r for r in remaining
            if dependencies[r].issubset(set(sorted_recipes))
        }

        if not ready:
            # Cycle detected — break it by picking the recipe
            # with the fewest unsatisfied dependencies
            ready = {min(
                remaining,
                key=lambda r: len(dependencies[r] - set(sorted_recipes))
            )}

        sorted_recipes.extend(sorted(ready, key=lambda r: r.name))
        remaining -= ready

    # --- Second pass: ensure dependents always appear after their dependencies ---
    # Re-sort using the dependency order as a key
    order: dict[Recipe, int] = {r: i for i, r in enumerate(sorted_recipes)}

    def effective_order(recipe: Recipe) -> int:
        # A recipe's position should be after all its dependencies
        dep_positions: list[int] = [order[d] for d in dependencies[recipe] if d in order]
        return max(dep_positions, default=order[recipe])

    return sorted(sorted_recipes, key=effective_order)


# --- Display ---

class DisplayMode(Enum):
    AUTO = auto()   # tree if possible, flat otherwise
    TREE = auto()   # always tree (may duplicate nodes for DAGs)
    FLAT = auto()   # always flat


def print_flat(graph: ProductionGraph, target_item: Item, target_quantity: float, solution: Solution) -> None:
    producer_of:  dict[Item, Recipe]       = {}
    consumers_of: dict[Item, list[Recipe]] = {}
    for edge in graph.edges:
        producer_of[edge.item] = edge.producer
        consumers_of.setdefault(edge.item, []).append(edge.consumer)

    # --- Recipes table ---
    recipes_table: Table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )
    recipes_table.add_column("Recipe",   style="bold white", min_width=20)
    recipes_table.add_column("Building", style="dim white",  min_width=15)
    recipes_table.add_column("Machines", justify="right",    min_width=14)
    recipes_table.add_column("Power",    justify="right",    min_width=10, style="cyan")
    recipes_table.add_column("Flows",    min_width=30)

    for recipe in topological_sort(graph):
        node: RecipeNode = graph.nodes[recipe]
        flow_lines: list[str] = []

        for item, qty in node.inputs.items():
            if item in graph.raw_resources:
                flow_lines.append(f"[yellow]← {item.name}[/yellow]  {qty:.1f}/min  [dim][raw][/dim]")
            elif item in producer_of:
                flow_lines.append(f"[yellow]← {item.name}[/yellow]  {qty:.1f}/min  [dim]from: {producer_of[item].name}[/dim]")
            else:
                flow_lines.append(f"[yellow]← {item.name}[/yellow]  {qty:.1f}/min  [dim red][?][/dim red]")

        for item, qty in node.outputs.items():
            destinations: list[Recipe] = consumers_of.get(item, [])
            if not destinations:
                flow_lines.append(f"[green]→ {item.name}[/green]  {qty:.1f}/min  [dim][target][/dim]")
            else:
                dest_names: str = ", ".join(r.name for r in destinations)
                flow_lines.append(f"[green]→ {item.name}[/green]  {qty:.1f}/min  [dim]to: {dest_names}[/dim]")

        recipes_table.add_row(
            recipe.name,
            node.building,
            f"{node.machines} [dim]({node.scale:.2f})[/dim]",
            f"{node.power:.1f} MW",
            "\n".join(flow_lines),
        )

    recipes_panel: Panel = Panel(
        recipes_table,
        title=f"[bold green]{target_item.name}[/bold green]  [dim]@ {target_quantity:.1f} /min[/dim]",
        border_style="green",
        box=box.HEAVY_EDGE,
        width=DISPLAY_WIDTH,
    )

    # --- Totals ---
    total_power:    float = sum(n.power    for n in graph.nodes.values())
    total_machines: int   = sum(n.machines for n in graph.nodes.values())

    machines_by_building: dict[str, int] = {}
    for node in graph.nodes.values():
        machines_by_building[node.building] = machines_by_building.get(node.building, 0) + node.machines

    # --- Summary table ---
    summary_table: Table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=False,
        expand=True,
        show_edge=False,
        padding=(0, 1),
    )
    summary_table.add_column("Label", style="dim white",  ratio=3)
    summary_table.add_column("Value", justify="right",    ratio=1)

    # Raw resources section
    summary_table.add_row("[bold yellow]Raw Resources[/bold yellow]", "")
    for item, qty in sorted(graph.raw_resources.items(), key=lambda x: x[0].name):
        summary_table.add_row(f"  {item.name}", f"{qty:.1f} /min")

    if graph.byproducts:
        summary_table.add_row("", "")
        summary_table.add_row("[bold yellow]Byproducts[/bold yellow]", "")
        for item, qty in sorted(graph.byproducts.items(), key=lambda x: x[0].name):
            summary_table.add_row(f"  {item.name}", f"{qty:.1f} /min")

    # Free supply usage section
    if solution.free_supplies:
        summary_table.add_row("", "")
        summary_table.add_row("[bold yellow]Free Supplies[/bold yellow]", "")
        n_recipe_cols: int = len(solution.recipe_index)
        for supply_idx, supply in enumerate(solution.free_supplies):
            used: float = solution.scales[n_recipe_cols + supply_idx]
            summary_table.add_row(
                f"  {supply.item.name}",
                f"{used:.1f} / {supply.quantity:.1f} /min",
            )

    # Totals section
    summary_table.add_row("", "")
    summary_table.add_row("[bold cyan]Totals[/bold cyan]", "")
    summary_table.add_row("  Total Machines", str(total_machines))
    summary_table.add_row("  Total Power",    f"{total_power:.1f} MW")

    # Machines by building type
    summary_table.add_row("", "")
    summary_table.add_row("[bold cyan]Machines by Building[/bold cyan]", "")
    for building_name, count in sorted(machines_by_building.items()):
        summary_table.add_row(f"  {building_name}", str(count))

    summary_panel: Panel = Panel(
        summary_table,
        title="[bold yellow]Summary[/bold yellow]",
        border_style="yellow",
        box=box.HEAVY_EDGE,
        width=DISPLAY_WIDTH,
    )

    console.print()
    console.print(recipes_panel)
    console.print(summary_panel)
    console.print()


def print_tree(graph: ProductionGraph, target_item: Item, target_quantity: float) -> None:
    children: dict[Recipe, list[tuple[Recipe, Item, float]]] = {
        recipe: [] for recipe in graph.nodes
    }
    for edge in graph.edges:
        if edge.consumer in children:
            children[edge.consumer].append((edge.producer, edge.item, edge.quantity))

    root: Recipe = next(
        recipe for recipe, node in graph.nodes.items()
        if target_item in node.outputs
    )

    def render(recipe: Recipe, indent: int = 0) -> None:
        node:   RecipeNode = graph.nodes[recipe]
        prefix: str        = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{recipe.name}  ×{node.machines} ({node.scale:.2f})  ({node.building})  {node.power:.1f} MW")

        for producer, item, qty in children[recipe]:
            print("  " * (indent + 1) + f"[{item.name}: {qty:.1f} /min]")
            render(producer, indent + 1)

        for item, qty in node.inputs.items():
            if item in graph.raw_resources:
                print("  " * (indent + 1) + f"[{item.name}: {qty:.1f} /min]")
                print("  " * (indent + 2) + f"└─ {item.name}  (raw resource)")

    print(f"\n{'─' * 60}")
    print(f"  TARGET: {target_item.name} @ {target_quantity:.1f} /min")
    print(f"{'─' * 60}\n")
    render(root)
    print()


def print_results(solution: Solution, mode: DisplayMode = DisplayMode.AUTO) -> None:
    graph: ProductionGraph = build_production_graph(solution)

    match mode:
        case DisplayMode.AUTO:
            if is_tree(graph):
                print_tree(graph, solution.target_item, solution.target_quantity)
            else:
                print_flat(graph, solution.target_item, solution.target_quantity, solution)
        case DisplayMode.TREE:
            print_tree(graph, solution.target_item, solution.target_quantity)
        case DisplayMode.FLAT:
            print_flat(graph, solution.target_item, solution.target_quantity, solution)