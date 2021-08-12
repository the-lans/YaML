from enum import Enum


TEXT_TYPES = [
    'No style',
    'Conspiracy theories',
    'TV-reports',
    'Toast',
    'Boy quotes',
    'Advertising slogans',
    'Short stories',
    'Instagram signatures',
    'Wikipedia',
    'Movie synopsis',
    'Horoscope',
    'Folk wisdom',
    'Garage',
]


def get_attr_enum(lst: list):
    return {f'field_{ind}': lst[ind] for ind in range(len(lst))}


BaseModelTextTypes = type('BaseModelTextTypes', (), get_attr_enum(TEXT_TYPES))


class ModelTextTypes(str, Enum):
    field_0 = TEXT_TYPES[0]
    field_1 = TEXT_TYPES[1]
    field_2 = TEXT_TYPES[2]
    field_3 = TEXT_TYPES[3]
    field_4 = TEXT_TYPES[4]
    field_5 = TEXT_TYPES[5]
    field_6 = TEXT_TYPES[6]
    field_7 = TEXT_TYPES[7]
    field_8 = TEXT_TYPES[8]
    field_9 = TEXT_TYPES[9]
    field_10 = TEXT_TYPES[10]
    field_11 = TEXT_TYPES[11]
    field_12 = TEXT_TYPES[12]
