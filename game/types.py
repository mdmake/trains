from enum import Enum


class ObjectType(Enum):
    POINT = 0
    LINE = 1
    CIRCLE = 2
    ANGLE = 3
    RECTANGLE = 4
    BORDER = 5


class ConvertTo(Enum):
    TO_LIST_OF_CIRCLE_OBJECTS = 0
    TO_DICT_OF_CIRCLE_OBJECTS = 1
    TO_SET_OF_CIRCLE_OBJECTS = 2


class NeighboursConnection(Enum):
    BY_LINE = 0
    BY_ARC = 1
