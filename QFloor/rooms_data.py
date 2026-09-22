import ast

SCHOOL_FLOORS = None

with open("QFloor/rooms.json", 'r') as e:
    SCHOOL_FLOORS = ast.literal_eval(e.read())


def iter_rooms():
    """Yield (floor, building, room) for every room -- handy for search or lookup."""
    for floor, buildings in SCHOOL_FLOORS.items():
        for building, rooms in buildings.items():
            for room in rooms:
                yield floor, building, room