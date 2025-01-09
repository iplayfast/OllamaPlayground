from typing import Dict, Any, Tuple

LANDMARKS: Dict[str, Dict[str, Any]] = {
    "store1": {
        "position": (1, 22),
        "size": (2, 9),  # Verified: SSSSSSSSS is 9 wide, 2 tall
        "doors": [(1, 22)],  # Updated: door is now at the start of the store
        "display_name": "STORE 1"
    },
    "FruitStand": {
        "position": (5, 36),
        "size": (2, 6),
        "doors": [(5, 37)],
        "display_name": "Fruit Stand"
    },
    "store3": {
        "position": (12, 7),
        "size": (2, 7),
        "doors": [(12, 8)],
        "display_name": "STORE 3"
    },
    "house1": {
        "position": (5, 7),
        "size": (4, 5),
        "doors": [(5, 8)],
        "display_name": "HOUSE 1"
    },
    "house2": {
        "position": (3, 48),
        "size": (4, 5),
        "doors": [(3, 49)],
        "display_name": "HOUSE 2"
    },
    "house3": {
        "position": (9, 28),
        "size": (4, 5),
        "doors": [(9, 29)],
        "display_name": "HOUSE 3"
    },
    "house4": {
        "position": (13, 49),
        "size": (4, 5),
        "doors": [(13, 50)],
        "display_name": "HOUSE 4"
    },
    "house5": {
        "position": (15, 34),
        "size": (4, 5),
        "doors": [(15, 35)],
        "display_name": "HOUSE 5"
    },
    "house6": {
        "position": (17, 13),
        "size": (4, 5),
        "doors": [(17, 14)],
        "display_name": "HOUSE 6"
    },
    "house7": {
        "position": (20, 45),
        "size": (4, 5),
        "doors": [(20, 46)],
        "display_name": "HOUSE 7"
    },
    "house8": {
        "position": (22, 22),
        "size": (4, 5),
        "doors": [(22, 23)],
        "display_name": "HOUSE 8"
    },
    "house9": {
        "position": (26, 45),
        "size": (4, 5),
        "doors": [(26, 46)],
        "display_name": "HOUSE 9"
    }
}

def get_landmark_at_position(pos: Tuple[int, int]) -> str | None:
    """Find which landmark (if any) is at the given position"""
    y, x = pos
    for name, info in LANDMARKS.items():
        ly, lx = info['position']
        height, width = info['size']
        if ly <= y < ly + height and lx <= x < lx + width:
            return name
    return None
