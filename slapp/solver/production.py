import json
from dataclasses import dataclass, field

basic_resources: set[str] = {
    'Limestone',
    'Iron Ore',
    'Copper Ore',
    'Caterium Ore',
    'Coal',
    'Sulfur',
    'Bauxite',
    'Raw Quartz',
    'Uranium',
    'SAM Ore',
    'Crude Oil',
    'Water',
    'Nitrogen Gas',
    'Blue Power Slug',
    'FICSMAS Gift',
    'Hatcher Remains',
    'Hog Remains',
    'Leaves',
    'Mycelia',
    'Purple Power Slug',
    'SAM',
    'Spitter Remains',
    'Stinger Remains',
    'Wood',
    'Yellow Power Slug',
}


@dataclass
class Item:
    class_name: str
    name: str
    sink_points: float
    is_basic: bool

    def __hash__(self) -> int:
        return hash(self.class_name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.class_name == other.class_name


@dataclass
class ItemAmount:
    item: Item
    amount: float


@dataclass
class Building:
    class_name: str
    name: str
    power: float


@dataclass
class Recipe:
    class_name: str
    name: str
    ingredients: list[ItemAmount]
    products: list[ItemAmount]
    is_alternate: bool
    produced_in: list[Building]
    duration: float

    def __hash__(self) -> int:
        return hash(self.class_name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Recipe):
            return NotImplemented
        return self.class_name == other.class_name


class ProductionPlanner:

    _items: dict[str, Item] = {}
    _items_by_name: dict[str, Item] = {}

    _recipes: dict[str, Recipe] = {}
    _recipes_by_name: dict[str, Recipe] = {}

    _buildings: dict[str, Building] = {}
    _buildings_by_name: dict[str, Building] = {}

    @classmethod
    def load_items(cls) -> None:
        with open('slapp/resources/docs/DocsItems.json') as f:
            for item in json.load(f).values():
                item = item[0]
                new_item = Item(
                    class_name=item['className'],
                    name=item['name'],
                    sink_points=float(item['sinkPoints']),
                    is_basic=item['name'] in basic_resources,
                )
                cls._items[new_item.class_name] = new_item
                cls._items_by_name[new_item.name] = new_item

    @classmethod
    def load_buildings(cls) -> None:
        with open('slapp/resources/docs/DocsBuildings.json') as f:
            for building in json.load(f).values():
                building = building[0]
                new_building = Building(
                    class_name=building['className'],
                    name=building['name'],
                    power=float(building['powerUsage']),
                )
                cls._buildings[new_building.class_name] = new_building
                cls._buildings_by_name[new_building.name] = new_building

    @classmethod
    def load_recipes(cls) -> None:
        with open('slapp/resources/docs/DocsRecipes.json') as f:
            for recipe in json.load(f).values():
                recipe = recipe[0]

                ingredients: list[ItemAmount] = [
                    ItemAmount(item=cls._items[e['item']], amount=float(e['amount']))
                    for e in recipe['ingredients']
                ]

                products: list[ItemAmount] = [
                    ItemAmount(item=cls._items[e['item']], amount=float(e['amount']))
                    for e in recipe['products']
                    if e['item'] in cls._items
                ]

                produced_in: list[Building] = [
                    cls._buildings[e]
                    for e in recipe['producedIn']
                    if e in cls._buildings
                ]

                new_recipe = Recipe(
                    class_name=recipe['className'],
                    name=recipe['name'],
                    ingredients=ingredients,
                    products=products,
                    is_alternate=bool(recipe['alternate']),
                    produced_in=produced_in,
                    duration=float(recipe['duration']),
                )
                cls._recipes[new_recipe.class_name] = new_recipe
                cls._recipes_by_name[new_recipe.name] = new_recipe
