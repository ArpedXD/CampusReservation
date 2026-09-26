import ast

SCHOOL_FLOORS = None


def iter_rooms():
    print('es')
    with open("QFloor/rooms.json", 'r') as e:
        SCHOOL_FLOORS = ast.literal_eval(e.read())
        
    for floor, buildings in SCHOOL_FLOORS.items():
        for building, rooms in buildings.items():
            for room in rooms:
                yield floor, building, room