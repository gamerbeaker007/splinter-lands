from enum import Enum

from src.static.icons import land_grain_farm_icon_url, land_logging_camp_icon_url, land_ore_mine_icon_url, \
    land_quarry_icon_url, land_research_hut_icon_url, land_shard_mine_icon_url, land_keep_icon_url, \
    land_castle_icon_url, land_under_construction_icon_url, fire_element_icon_url, \
    water_element_icon_url, life_element_icon_url, death_element_icon_url, earth_element_icon_url, \
    dragon_element_icon_url, grain_icon_url, stone_icon_url, wood_icon_url, iron_icon_url, sps_icon_url, \
    research_icon_url, tax_icon_url, land_hammer_icon_url, dec_icon_url


class ExtendedEnum(Enum):

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))


grain_conversion_ratios = {
    'WOOD': 4,
    'STONE': 10,
    'IRON': 40,
    'RESEARCH': 200
}

# production_rates = {
#     'GRAIN': 0.02,
#     'WOOD': 0.005,
#     'STONE': 0.002,
#     'IRON': 0.0005,
#     'RESEARCH': 0.0001,
#     'SPS': 0  # Not sure how to calculate so make 0
# }

consume_rates = {
    'GRAIN': 0.01,
    'WOOD': 0.005,
    'STONE': 0.002,
    'IRON': 0.0005,
}

worksite_type_mapping = {
    'Grain Farm': land_grain_farm_icon_url,
    'Logging Camp': land_logging_camp_icon_url,
    'Ore Mine': land_ore_mine_icon_url,
    'Quarry': land_quarry_icon_url,
    'Research Hut': land_research_hut_icon_url,
    'Shard Mine': land_shard_mine_icon_url,
    'KEEP': land_keep_icon_url,
    'CASTLE': land_castle_icon_url,
    'Undeveloped': land_under_construction_icon_url,
}

biome_mapper = {
    'red':  fire_element_icon_url,
    'blue': water_element_icon_url,
    'white': life_element_icon_url,
    'black': death_element_icon_url,
    'green': earth_element_icon_url,
    'gold': dragon_element_icon_url,
}

resource_icon_map = {
    "GRAIN": grain_icon_url,
    "STONE": stone_icon_url,
    "WOOD": wood_icon_url,
    "IRON": iron_icon_url,
    "SPS": sps_icon_url,
    "RESEARCH": research_icon_url,
    "TAX": tax_icon_url,
    "DEC": dec_icon_url,
    "PP": land_hammer_icon_url,
    "": land_hammer_icon_url,
}


class Format(ExtendedEnum):
    wild = 'wild'
    modern = 'modern'


class Edition(ExtendedEnum):
    alpha = 0
    beta = 1
    promo = 2
    reward = 3
    untamed = 4
    dice = 5
    gladius = 6
    chaos = 7
    rift = 8
    soulbound = 10
    rebellion = 12
    soulboundrb = 13
