DEFAULT_SAVE_FILE_MANIFEST = {
    "slot_name": "New Trainer",
    "save_version": 1,
    "playtime": 0,
    "badges": 0,
    "location": "starter_town",
    "last_played": None
}

DEFAULT_TRAINER = {
    "name": "New Trainer",
    "gender": "male",
    "money": 20,
    "badges": 0,
    "playtime_seconds": 0,
}

DEFAULT_PARTY = {
    "slots": [
        {"name": "Charmadillo", "level": 75, "exp": 0, "health": 1000, "energy": 2000},
        {"name": "Pluma", "level": 3, "exp": 0, "health": 100, "energy": 100},
        None, 
        None, 
        None
    ]
}

DEFAULT_PC = {
    "boxes": [
        [None]*30,  # Box 1
        [None]*30,  # Box 2
        [None]*30,  # Box 3
        [None]*30,  # Box 4
        [None]*30,  # Box 5
        [None]*30,  # Box 6
        [None]*30,  # Box 7
        [None]*30   # Box 8
    ]
}

DEFAULT_WORLD = {
    "current_map": "world",
    "position": {
        "x": 608,
        "y": 714,
        "facing_direction": "down"
    }
}

DEFAULT_FLAGS = {
    "got_starter": False,
    "talked_to_professor": False,
    "bridge_opened": False,
    "champion_defeated": False,
    "characters_defeated" : []
}

DEFAULT_INVENTORY = {
    "items": {
        "Potion": 2,
        "Capsule Cubes": 5
    },
    "key_items": []
}