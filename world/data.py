
IC = 12


STATS = {
    "attributes": {
        "strength": 1,
        "dexterity": 1,
        "stamina": 1,
        "charisma": 1,
        "manipulation": 1,
        "composure": 1,
        "intelligence": 1,
        "wits": 1,
        "resolve": 1
    },
    "skills": {},
    "disciplines": {},
    "specialties": {},
    "backgrounds": {},
    "pools": {},
    "advantages": {},
    "flaws": {},
    "bio": {},
    "splat": "",
    "notes": "",
    "approved_by": "",
    "approved": False
}

BIO = [
    "full name",
    "birthdate",
    "concept",
    "splat",
    "ambition",
    "sire",
    "desire",
    "predator",
    "clan",
    "generation",
]


SPLATS = [
    "vampire",
    "ghoul",
    "mortal",
]

ATTRIBUTES = [
    "strength",
    "dexterity",
    "stamina",
    "charisma",
    "manipulation",
    "composure",
    "intelligence",
    "wits",
    "resolve"
]

MENTAL = [
    "intelligence",
    "wits",
    "resolve",
    "academics",
    "awareness",
    "finance",
    "investigation",
    "medicine",
    "occult",
    "politics",
    "science",
    "technology"
]

PHYSICAL = [
    "strength",
    "dexterity",
    "stamina",
    "athletics",
    "brawl",
    "craft",
    "drive",
    "firearms",
    "larceny",
    "melee",
    "stealth",
    "survival"
]

SOCIAL = [
    "charisma",
    "manipulation",
    "composure",
    "animal ken",
    "etiquette",
    "insight",
    "intimidation",
    "leadership",
    "performance",
    "persuasion",
    "streetwise",
    "subterfuge"
]

SKILLS = [
    "athletics",
    "brawl",
    "craft",
    "drive",
    "firearms",
    "larceny",
    "melee",
    "stealth",
    "survival",
    "animal ken",
    "etiquette",
    "insight",
    "intimidation",
    "leadership",
    "performance",
    "persuasion",
    "streetwise",
    "subterfuge",
    "academics",
    "awareness",
    "finance",
    "investigation",
    "medicine",
    "occult",
    "politics",
    "science",
    "technology"
]

DISCIPLINES = [
    "animalism",
    "auspex",
    "celerity",
    "dominate",
    "fortitude",
    "obfuscate",
    "oblivion",
    "potence",
    "presence",
    "protean",
    "blood sorcery",
    "thin-blood alchemy"
]
ADVANTAGES = [
    "beautiful",
    "stunning",
    "high-functioning addict",
    "bond resistance",
    "short bond",
    "unbondable",
    "bloodhound",
    "iron gullet",
    "eat food",
    "allies",
    "contacts",
    "fame",
    "influence",
    "haven",
    "herd",
    "mask",
    "zeroed",
    "cobbler",
    "mawla",
    "resources",
    "retainers",
    "status"
]
FLAWS = [
    "illiterate",
    "repulsive",
    "vile",
    "hopeless addiction",
    "addiction",
    "archaic",
    "lving in the past",
    "bondslave",
    "bond junkie",
    "long bond",
    "farmer",
    "organovore",
    "methuselah's thirst",
    "prey exclusion",
    "stake bait",
    "bane",
    "folklore block",
    "stigmata",
    "dark secret",
    "dispised",
    "disliked",
    "no haven",
    "known blankbody",
    "known corpse",
    "adversary",
    "destitude",
    "stalkers",
    "shunned",
    "suspect",
]


POOLS = [
    "health",
    "willpower",
    "blood",
    "humanity",
    "morality",
    "blood potency",
    "hunger"
]


INSTANCED = []


BIO_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "has_specialties": False,
        "specialties": {}

    },
    "clan": {
        "values": [
            "banu haqim",
            "brujah",
            "caitiff",
            "gangrel",
            "hecata",
            "lasombra",
            "malkavian",
            "the ministry",
            "nosferatu",
            "ravnos",
            "salubri",
            "toreador",
            "tremere",
            "tzimisce",
            "ventrue",
            "thin-blood"
        ],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Clan is only available to vampires."
    },
    "sire": {
        "values": [],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Sire is only available to vampires."
    },
    "generation": {
        "values": [16, 15, 14, 13, 12, 11, 10],
        "check": lambda x: x["splat"] in "vampire",
        "check_message": "Generation is only available to vampires."
    },
    "predator": {
        "values": [
            "alleycat",
            "bagger",
            "blood leech",
            "cleaver",
            "consensualist",
            "extortionist",
            "farmer",
            "graverobber",
            "grim reaper",
            "montero",
            "osiris",
            "pursuer",
            "roadside killer",
            "sandman",
            "scenequeen",
            "siren",
            "trapdoor"
        ],
        "check": lambda x: "vampire" in x["splat"],
        "check_message": "Predator is only available to vampires."
    },
}

ATTRIBUTES_GOOD_VALUES = {
    "default": {
        "values": range(1, 20),
        "check": lambda x: True,
        "check_message": "You must have at least one dot in each attribute.",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
}

SKILLS_GOOD_VALUES = {
    "default": {
        "values": range(1, 5),
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": True,
        "specialties": {}
    }
}


ADVANTAGES_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
    "beautiful": {"values": [2]},
    "stunning": {"values": [4]},
    "high-functioning addict": {"values": [1]},
    "bond resistance": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bond Resistance is only available to vampires."
    },
    "short bond": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Short Bond is only available to vampires."
    },
    "unbondable": {
        "values": [4],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Unbondable is only available to vampires."
    },
    "bloodhound": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bloodhound is only available to vampires."
    },
    "iron gullet": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Iron Gullet is only available to vampires."
    },
    "eat food": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Eat Food is only available to vampires."
    },
    "allies": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "contacts": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "fame": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "fame": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "haven": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "herd": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True,
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Herd is only available to vampires."
    },
    "influence": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    }, "mask": {
        "values": [1, 2],
        "instanced": True,
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Mask is only available to vampires."
    },
    "status": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True
    },
    "zeroed": {
        "values": [1],
        "check": lambda x: x["advantages"]["mask"] == 2,
        "check_message": "Zeroed is only available to vampires with Mask 2."
    },
    "cobbler": {
        "values": [1],
        "check": lambda x: x["advantages"]["mask"] == 2,
        "check_message": "Cobbler is only available to vampires with Mask 2."
    },
    "mawla": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True,
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Mawla is only available to vampires."
    },
    "resources": {
        "values": [1, 2, 3, 4, 5],
    },
    "retainer": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True,
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Retainer is only available to vampires."
    }
}


FLAWS_GOOD_VALUES = {
    "default": {
        "values": [],
        "check": lambda x: True,
        "check_message": "Permission Denied",
        "instanced": False,
        "instances": [],
        "has_specialties": False,
        "specialties": {}
    },
    "illiterate": {"values": [1]},
    "repulsive": {"values": [2]},
    "vile": {"values": [4]},
    "hopeless addiction": {"values": [2]},
    "addiction": {"values": [1]},
    "archaic": {
        "values": [1], "check": lambda x: x["splat"] == "vampire",
        "check_message": "Archaic is only available to vampires."
    },
    "living in the past": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Living in the Past is only available to vampires."
    },
    "bondslave": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bondslave is only available to vampires."
    },
    "bond junkie": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Bond Junkie is only available to vampires."
    },
    "long bond": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Long Bond is only available to vampires."
    },
    "farmer": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Farmer is only available to vampires."
    },
    "organavore": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Organavore is only available to vampires."
    },
    "methuselah's thirst": {
        "values": [3], "check": lambda x: x["splat"] == "vampire",
        "check_message": "Methuselah's Thirst is only available to vampires."
    },
    "prey exclusion": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Prey Exclusion is only available to vampires.",
        "instanced": True
    },
    "stake bait": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Stake Bait is only available to vampires."
    },
    "folklore bane": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Folklore Bane is only available to vampires."
    },
    "folklore block": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Folklore Block is only available to vampires."
    },
    "dark secret": {
        "values": [1, 2],
        "instanced": True
    },
    "despised": {
        "values": [2],
        "instnaed": True
    },
    "disliked": {
        "values": [1],
        "instanced": True
    },
    "no haven": {
        "values": [1],
    },
    "obvious predator": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Obvious Predator is only available to vampires."
    },
    "knowwn blankbody": {
        "values": [2],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Known Blankbody is only available to vampires."
    },
    "known corpse": {
        "values": [1],
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Known Corpse is only available to vampires."
    },
    "adverssary": {
        "values": [1, 2, 3, 4, 5],
        "instanced": True,
        "check": lambda x: x["splat"] == "vampire",
        "check_message": "Adversary is only available to vampires."
    },
    "destitute": {
        "values": [1],
    },
    "stalkers": {"values": [1]},
    "shunned": {
        "values": [2],
        "instanced": True
    },
    "suspect": {
        "values": [1],
        "instanced": True
    }

}


DISCIPLINES_GOOD_VALUES = {
    "animalism": {
        "values": range(1, 6),
        "check_message": "Animalism is only available to vampires.",
        "instanced": False,
        "instances": [],
        "has_specialties": True,
        "specialties": {
            "bond famulus": {
                "values": [1],
                "check": lambda x: x.disciplines["animalism"] >= 1,
                "check_message": "Animalism 1 is required."
            },
            "sense the beast": {
                "values": [1],
                "check": lambda x: x.disciplines["animalism"] >= 1,
                "check_message": "Animalism 1 is required."
            },
            "feral whispers": {
                "values": [2],
                "check": lambda x: x.disciplines["animalism"] >= 2,
                "check_message": "Animalism 2 is required."
            },
            "animal succulence": {
                "values": [3],
                "check": lambda x: x.disciplines["animalism"] >= 3,
                "check_message": "Animalism 3 is required."
            },
            "quell the beast": {
                "values": [3],
                "check": lambda x: x.disciplines["animalism"] >= 3,
                "check_message": "Animalism 3 is required."
            },
            "living hive": {
                "values": [3],
                "check": lambda x: x.disciplines["obfuscate"] >= 2 and x.disciplines["animalism"] >= 3,
                "check_message": "Obfuscate 2 and Animalism 3 are required."
            },
            "subsume the spirit": {
                "values": [4],
                "check": lambda x: x.disciplines["animalism"] >= 4,
                "check_message": "Animalism 4 is required."
            },
            "animal dominion": {
                "values": [5],
                "check": lambda x: x.disciplines["animalism"] >= 5,
                "check_message": "Animalism 5 is required."
            },
            "draw out the beast": {
                "values": [5],
                "check": lambda x: x.disciplines["animalism"] >= 5,
                "check_message": "Animalism 5 is required."
            }
        },
    },
    "auspex": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Auspex is only available to vampires.",
        "specialties": {
            "heightened senses": {
                "values": [1],
                "check": lambda x: x.disciplines["auspex"] >= 1,
                "check_message": "Auspex 1 is required."
            },
            "sense the unseen": {
                "values": [1],
                "check": lambda x: x.disciplines["auspex"] >= 1,
                "check_message": "Auspex 1 is required."
            },
            "premonition": {
                "values": [2],
                "check": lambda x: x.disciplines["auspex"] >= 2,
                "check_message": "Auspex 2 is required."
            },
            "scry the soul": {
                "values": [3],
                "check": lambda x: x.disciplines["auspex"] >= 3,
                "check_message": "Auspex 3 is required."
            },
            "shared senses": {
                "values": [3], "check": lambda x: x.disciplines["auspex"] >= 3,
                "check_message": "Auspex 3 is required."
            },
            "spirits touch": {
                "values": [4],
                "check": lambda x: x.disciplines["auspex"] >= 4,
                "check_message": "Auspex 4 is required."
            },
            "clairvoyance": {
                "values": [5],
                "check": lambda x: x.disciplines["auspex"] >= 5,
                "check_message": "Auspex 5 is required."
            },
            "possession": {
                "values": [5],
                "check": lambda x: x.disciplines["auspex"] >= 5 and x["dominate"] >= 3,
                "check_message": "Auspex 5 and Dominate 3 are required."
            },
            "telepathy": {
                "values": [5],
                "check": lambda x: x.disciplines["auspex"] >= 5,
                "check_message": "Auspex 5 is required."
            }
        }
    },
    "celerity": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Celerity is only available to vampires.",
        "specialties": {
            "cats grace": {
                "values": [1],
                "check": lambda x: x.disciplines["celerity"] >= 1,
                "check_message": "Celerity 1 is required."
            },
            "fleetness": {
                "values": [2],
                "check": lambda x: x.disciplines["celerity"] >= 2,
                "check_message": "Celerity 2 is required."
            },
            "blink": {
                "values": [3],
                "check": lambda x: x.disciplines["celerity"] >= 3,
                "check_message": "Celerity 3 is required."
            },
            "traversal": {
                "values": [3],
                "check": lambda x: x.disciplines["celerity"] >= 3,
                "check_message": "Celerity 3 is required."
            },
            "draught of elegance": {
                "values": [4],
                "check": lambda x: x.disciplines["celerity"] >= 4,
                "check_message": "Celerity 4 is required."
            },
            "unerring aim": {
                "values": [4],
                "check": lambda x: x.disciplines["celerity"] >= 4 and x["auspex"] >= 2,
                "check_message": "Celerity 4 and Auspex 2 are required."
            },
            "lightning strike": {
                "values": [5],
                "check": lambda x: x.disciplines["celerity"] >= 5,
                "check_message": "Celerity 5 is required."
            },
            "split second": {
                "values": [5],
                "check": lambda x: x.disciplines["celerity"] >= 5,
                "check_message": "Celerity 5 is required."
            },
        }
    },
    "dominate": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Dominate is only available to vampires.",
        "specialties": {
            "cloud memory": {
                "values": [1],
                "check": lambda x: x.disciplines["dominate"] >= 1,
                "check_message": "Dominate 1 is required."
            },
            "compel": {
                "values": [1],
                "check": lambda x: x.disciplines["dominate"] >= 1,
                "check_message": "Dominate 1 is required."
            },
            "mesmerize": {
                "values": [2],
                "check": lambda x: x.disciplines["dominate"] >= 2,
                "check_message": "Dominate 2 is required."
            },
            "dementation": {
                "values": [2],
                "check": lambda x: x.disciplines["dominate"] >= 2 and x["obfuscate"] >= 2,
                "check_message": "Dominate 2 and Obfuscate 2 are required."
            },
            "submerged directive": {
                "values": [2],
                "check": lambda x: x.disciplines["dominate"] >= 2,
                "check_message": "Dominate 2 is required."
            },
            "the forgetful mind": {
                "values": [3],
                "check": lambda x: x.disciplines["dominate"] >= 3,
                "check_message": "Dominate 3 is required."
            },
            "rationalize": {
                "values": [4],
                "check": lambda x: x.disciplines["dominate"] >= 4,
                "check_message": "Dominate 4 is required."
            },
            "mass manipulation": {
                "values": [5],
                "check": lambda x: x.disciplines["dominate"] >= 5,
                "check_message": "Dominate 5 is required."
            },
            "terminal decree": {
                "values": [5],
                "check": lambda x: x.disciplines["dominate"] >= 5,
                "check_message": "Dominate 5 is required."
            },
        },
    },

    "fortitude": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Fortitude is only available to vampires.",
        "specialties": {
            "resilience": {
                "values": [1],
                "check": lambda x: x.disciplines["fortitude"] >= 1,
                "check_message": "Fortitude 1 is required."
            },
            "unswayable mind": {
                "values": [1],
                "check": lambda x: x.disciplines["fortitude"] >= 1,
                "check_message": "Fortitude 1 is required."
            }
        },
        "toughness": {
            "values": [2],
            "check": lambda x: x.disciplines["fortitude"] >= 2,
            "check_message": "Fortitude 2 is required."
        },
        "enduuring Bbest": {
            "values": [2],
            "check": lambda x: x.disciplines["fortitude"] >= 2,
            "check_message": "Fortitude 2 is required."
        },
        "fortify the inner facade": {
            "values": [3],
            "check": lambda x: x.disciplines["fortitude"] >= 3,
            "check_message": "Fortitude 3 is required."
        },
        "draught of endurance": {
            "values": [4],
            "check": lambda x: x.disciplines["fortitude"] >= 3,
            "check_message": "Fortitude 4 is required."
        },
        "flesh of marble": {
            "values": [5],
            "check": lambda x: x.disciplines["fortitude"] >= 5,
            "check_message": "Fortitude 5 is required."
        },
        "prowess from pain": {
            "values": [5],
            "check": lambda x: x.disciplines["fortitude"] >= 5,
            "check_message": "Fortitude 5 is required."
        },
    },

    "obfuscate": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Obfuscate is only available to vampires.",
        "specialties": {
            "cloak of shadows": {
                "values": [1],
                "check": lambda x: x.disciplines["obfuscate"] >= 1,
                "check_message": "Obfuscate 1 is required."
            }
        },
        "unseen passage": {
            "values": [2],
            "check": lambda x: x.disciplines["obfuscate"] >= 2,
            "check_message": "Obfuscate 2 is required."
        },
        "ghost in the mahine": {
            "values": [3],
            "check": lambda x: x.disciplines["obfuscate"] >= 3,
            "check_message": "Obfuscate 3 is required."
        },
        "mask of a thousand faces": {
            "values": [4],
            "check": lambda x: x.disciplines["obfuscate"] >= 4,
            "check_message": "Obfuscate 4 is required."
        },

        "conseal": {
            "values": [4],
            "check": lambda x: x.disciplines["obfuscate"] >= 4,
            "check_message": "Obfuscate 4 is required."
        },
        "vaniah": {
            "values": [5],
            # make sure they ahve the right disciplone level AND stat category in tests?
            "check": lambda x: x.disciplines["obfuscate"] >= 4 and x.specialties["cloak of shadows"] >= 4,
            "check_message": "Obfuscate 4 and Cloak of Shadows 4 are required."

        },
        "imposters guise": {
            "values": [5],
            "check": lambda x: x.disciplines["obfuscate"] >= 5 and x.specialties["mask of a thousand faces"] >= 4,
            "check_message": "Obfuscate 5 and Mask of a Thousand Faces 4 are required."
        },

    },
    "potence": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Potence is only available to vampires.",
        "specialties": {
            "lethhal body": {
                "values": [1],
                "check": lambda x: x.disciplines["potence"] >= 1,
                "check_message": "Potence 1 is required."
            },
            "soaring leap": {
                "values": [1],
                "check": lambda x: x.disciplines["potence"] >= 1,
                "check_message": "Potence 1 is required."
            },
            "prowess": {
                "values": [2],
                "check": lambda x: x.disciplines["potence"] >= 2,
                "check_message": "Potence 2 is required."
            },
            "brutal feed": {
                "values": [3],
                "check": lambda x: x.disciplines["potence"] >= 3,
                "check_message": "Potence 3 is required."
            },
            "spark of rage": {
                "values": [3],
                "check": lambda x: x.disciplines["potence"] >= 3,
                "check_message": "Potence 3 is required."
            },
            "uncanny grip": {
                "values": [3],
                "check": lambda x: x.disciplines["potence"] >= 3,
            },
            "draught of might": {
                "values": [4],
                "check": lambda x: x.disciplines["potence"] >= 4,
                "check_message": "Potence 4 is required."
            },
            "earth shock": {
                "values": [4],
                "check": lambda x: x.disciplines["potence"] >= 4,
                "check_message": "Potence 4 is required."
            },
            "fist of caine": {
                "values": [5],
                "check": lambda x: x.disciplines["potence"] >= 5,
                "check_message": "Potence 5 is required."
            }
        },
    },
    "presence": {
        "values": range(1, 6),
        "has_specialties": True,
        "check_message": "Presence is only available to vampires.",
        "specialties": {
            "awe": {
                "values": [1],
                "check": lambda x: x.disciplines["presence"] >= 1,
                "check_message": "Presence 1 is required."
            },
            "daunt": {
                "values": [1],
                "check": lambda x: x.disciplines["presence"] >= 1,
                "check_message": "Presence 1 is required."
            },
            "lingering kiss": {
                "values": [2],
                "check": lambda x: x.disciplines["presence"] >= 2,
                "check_message": "Presence 2 is required."
            },
            "dread gaze": {
                "values": [3],
                "check": lambda x: x.disciplines["presence"] >= 3,
                "check_message": "Presence 3 is required."
            },
            "entrancement": {
                "values": [3],
                "check": lambda x: x.disciplines["presence"] >= 3,
                "check_message": "Presence 3 is required."
            },
            "irresistable voice": {
                "values": [4],
                "check": lambda x: x.disciplines["presence"] >= 4,
                "check_message": "Presence 4 is required."
            },

            "summon": {
                "values": [4],
                "check": lambda x: x.disciplines["presence"] >= 4,
                "check_message": "Presence 4 is required."
            },
            "majesty": {
                "values": [5],
                "check": lambda x: x.disciplines["presence"] >= 5,
                "check_message": "Presence 5 is required."
            },
            "star magnetism": {
                "values": [5],
                "check": lambda x: x.disciplines["presence"] >= 5,
                "check_message": "Presence 5 is required."
            },
        },
        "protean": {
            "values": range(1, 6),
            "has_specialties": True,
            "check_message": "Protean is only available to vampires.",
            "specialties": {
                "eyes of the beast": {
                    "values": [1],
                    "check": lambda x: x.disciplines["protean"] >= 1,
                    "check_message": "Protean 1 is required."
                },
                "weight of the feather": {
                    "values": [1],
                    "check": lambda x: x.disciplines["protean"] >= 1,
                    "check_message": "Protean 1 is required."
                },
                "feral weapons": {
                    "values": [2],
                    "check": lambda x: x.disciplines["protean"] >= 2,
                    "check_message": "Protean 2 is required."
                },
                "earth meld": {
                    "values": [3],
                    "check": lambda x: x.disciplines["protean"] >= 3,
                    "check_message": "Protean 3 is required."
                },
                "shape change": {
                    "values": [3],
                    "check": lambda x: x.disciplines["protean"] >= 3,
                    "check_message": "Protean 3 is required."
                },
                "metamorphosis": {
                    "values": [4],
                    "check": lambda x: x.disciplines["protean"] >= 4,
                    "check_message": "Protean 4 is required."
                },
                "mist form": {
                    "values": [5],
                    "check": lambda x: x.disciplines["protean"] >= 5,
                    "check_message": "Protean 5 is required."
                },
                "unfettered heart": {
                    "values": [5],
                    "check": lambda x: x.disciplines["protean"] >= 5,
                    "check_message": "Protean 5 is required."
                },
            },
        },
        "blood_sorcery": {
            "values": range(1, 6),
            "has_specialties": True,
            "check_message": "Blood Sorcery is only available to vampires.",
            "specialties": {
                "corrosive vitae": {
                    "values": [1],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 1,
                    "check_message": "Blood Sorcery 1 is required."
                },
                "a taste for blood": {
                    "values": [1],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 1,
                    "check_message": "Blood Sorcery 1 is required."
                },
                "extinguish vitae": {
                    "values": [2],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 2,
                    "check_message": "Blood Sorcery 2 is required."
                },
                "blood of potency": {
                    "values": [3],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 3,
                    "check_message": "Blood Sorcery 3 is required."
                },
                "scorpion's touch": {
                    "values": [3],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 3,
                    "check_message": "Blood Sorcery 3 is required."
                },
                "theft of vitae": {
                    "values": [4],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 4,
                    "check_message": "Blood Sorcery 4 is required."
                },
                "baal's caress": {
                    "values": [5],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 5,
                    "check_message": "Blood Sorcery 5 is required."
                },
                "cauldron of blood": {
                    "values": [5],
                    "check": lambda x: x.disciplines["blood_sorcery"] >= 5,
                    "check_message": "Blood Sorcery 5 is required."
                },
            }
        },
        "default": {
            "values": [],
            "check": lambda x: x["splat"] in "vampire",
            "check_message": "Permission Denied",
            "instanced": False,
            "instances": [],
            "has_specialties": False,
            "specialties": {}
        }
    }

}


POOLS_GOOD_VALUES = {
    "default": {"values": [], "check": lambda x: True, "check_message": "Permission Denied", "specialties": False, "specialties": {}},
    "humanity": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "check": lambda x: x["splat"] == "vampire"},
    "willpower": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
    "blood potency": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "check": lambda x: x["splat"] == "vampire"},
    "health": {"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
    "hunger": {"values": [1, 2, 3, 4, 5], "check": lambda x: x["splat"] == "vampire"},
}


TOTAL_TRAITS = [
    ("bio", BIO, BIO_GOOD_VALUES),
    ("attributes", ATTRIBUTES, ATTRIBUTES_GOOD_VALUES),
    ("skills", SKILLS, SKILLS_GOOD_VALUES),
    ("advantages", ADVANTAGES, ADVANTAGES_GOOD_VALUES),
    ("flaws", FLAWS, FLAWS_GOOD_VALUES),
    ("disciplines", DISCIPLINES, DISCIPLINES_GOOD_VALUES),
    ("pools", POOLS, POOLS_GOOD_VALUES),
]


def get_trait_list(string):
    for list in TOTAL_TRAITS:
        for trait in list[1]:
            if string in trait:

                # create an object and add the values to it to return
                # TODO: This is a nightmare driven hell machine. Fix it.
                # The dark magics of python are at work here.
                output = {}
                output["trait"] = trait
                output["category"] = list[0]
                output["values"] = list[2][trait]["values"] if trait in list[2] else list[2]["default"]["values"]
                try:
                    output["check"] = list[2][trait]["check"] if trait in list[2] else list[
                        2]["default"]["check"] if "default" in list[2] else lambda x: True
                except KeyError:
                    output["check"] = lambda x: True
                try:
                    output["check_message"] = list[2][trait]["check_message"] if trait in list[2] else list[
                        2]["default"]["check_message"] if "default" in list[2] else "Permission denied."
                except KeyError:
                    output["check_message"] = "Permission denied."

                try:
                    output["has_specialties"] = list[2][trait]["has_specialties"] if trait in list[
                        2] else list[2]["default"]["has_specialties"] if "default" in list[2] else False
                    output["specialties"] = list[2][trait]["specialties"] if trait in list[
                        2] else list[2]["default"]["specialties"] if "default" in list[2] else {}
                except:
                    output["has_specialties"] = False
                    output["specialties"] = {}

                try:
                    output["instanced"] = list[2][trait]["instanced"] if trait in list[
                        2] else list[2]["default"]["instanced"] if "default" in list[2] else False
                except:
                    output["instanced"] = False

                try:
                    output["instances"] = list[2][trait]["instances"] if trait in list[
                        2] else list[2]["default"]["instances"] if "default" in list[2] else []
                except:
                    output["instances"] = []

                return output

# get the category of a trait


def get_trait_category(string):
    for list in TOTAL_TRAITS:
        for trait in list[1]:
            if string in trait:
                return list[0]
