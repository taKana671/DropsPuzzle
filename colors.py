import random
from enum import Enum

from panda3d.core import LColor

theme_colors = []


class Colors(Enum):

    @classmethod
    def select(cls, n):
        return random.sample([m.value for m in cls], n)

    def __init_subclass__(cls):
        super().__init_subclass__()
        theme_colors.append(cls)


class Blue(Colors):

    VIVID = LColor(0.0, 0.6, 1.0, 1)
    BRIGHT = LColor(0.51, 0.76, 0.93, 1)
    STRONG = LColor(0.13, 0.58, 0.87, 1)
    DEEP = LColor(0.07, 0.32, 0.49, 1)
    # LIGHT = LColor(0.78, 0.87, 0.93, 1)
    SOFT = LColor(0.44, 0.67, 0.82, 1)
    DULL = LColor(0.21, 0.46, 0.63, 1)
    DARK = LColor(0.10, 0.22, 0.30, 1)
    # PALE = LColor(0.81, 0.86, 0.89, 1)
    LIGHT_GRAYISH = LColor(0.54, 0.65, 0.72, 1)
    GRAYISH = LColor(0.31, 0.44, 0.53, 1)
    DARK_GRAYISH = LColor(0.15, 0.21, 0.25, 1)


class LightBlue(Colors):

    VIVID = LColor(0.0, 1.0, 0.9, 1)
    BRIGHT = LColor(0.51, 0.93, 0.89, 1)
    STRONG = LColor(0.13, 0.87, 0.8, 1)
    DEEP = LColor(0.07, 0.49, 0.45, 1)
    # LIGHT = LColor(0.78, 0.93, 0.91, 1)
    SOFT = LColor(0.44, 0.82, 0.78, 1)
    DULL = LColor(0.21, 0.63, 0.59, 1)
    DARK = LColor(0.1, 0.3, 0.28, 1)
    # PALE = LColor(0.81, 0.89, 0.88, 1)
    LIGHT_GRAYISH = LColor(0.54, 0.72, 0.71, 1)
    GRAYISH = LColor(0.31, 0.53, 0.51, 1)
    DARK_GRAYISH = LColor(0.15, 0.25, 0.24, 1)


class Green(Colors):

    VIVID = LColor(0.6, 1.0, 0.0, 1)
    BRIGHT = LColor(0.76, 0.93, 0.51, 1)
    STRONG = LColor(0.58, 0.87, 0.13, 1)
    DEEP = LColor(0.32, 0.49, 0.07, 1)
    # LIGHT = LColor(0.87, 0.93, 0.78, 1)
    SOFT = LColor(0.67, 0.82, 0.44, 1)
    DULL = LColor(0.46, 0.63, 0.21, 1)
    DARK = LColor(0.22, 0.3, 0.1, 1)
    # PALE = LColor(0.86, 0.89, 0.81, 1)
    LIGHT_GRAYISH = LColor(0.65, 0.72, 0.54, 1)
    GRAYISH = LColor(0.44, 0.53, 0.31, 1)
    DARK_GRAYISH = LColor(0.21, 0.25, 0.15, 1)


class Brown(Colors):

    BRIGHT = LColor(0.93, 0.68, 0.51, 1)
    DARK = LColor(0.3, 0.18, 0.1, 1)
    DARK_GRAYISH = LColor(0.25, 0.19, 0.15, 1)
    DEEP = LColor(0.49, 0.24, 0.07, 1)
    DULL = LColor(0.63, 0.38, 0.21, 1)
    GRAYISH = LColor(0.53, 0.4, 0.31, 1)
    # LIGHT = LColor(0.93, 0.84, 0.78, 1)
    LIGHT_GRAYISH = LColor(0.72, 0.61, 0.54, 1)
    # PALE = LColor(0.89, 0.84, 0.81, 1)
    SOFT = LColor(0.82, 0.59, 0.44, 1)
    STRONG = LColor(0.87, 0.42, 0.13, 1)
    VIVID = LColor(1.0, 0.4, 0.0, 1)


class DarkBlue(Colors):

    BRIGHT = LColor(0.51, 0.55, 0.93, 1)
    DARK = LColor(0.1, 0.12, 0.3, 1)
    DARK_GRAYISH = LColor(0.15, 0.16, 0.25, 1)
    DEEP = LColor(0.07, 0.11, 0.49, 1)
    DULL = LColor(0.21, 0.25, 0.63, 1)
    GRAYISH = LColor(0.31, 0.34, 0.53, 1)
    # LIGHT = LColor(0.78, 0.79, 0.93, 1)
    LIGHT_GRAYISH = LColor(0.54, 0.56, 0.72, 1)
    # PALE = LColor(0.81, 0.82, 0.89, 1)
    SOFT = LColor(0.44, 0.48, 0.82, 1)
    STRONG = LColor(0.13, 0.2, 0.91, 1)
    VIVID = LColor(0.0, 0.1, 1.0, 1)


class Purple(Colors):

    BRIGHT = LColor(0.54, 0.51, 0.93, 1)
    DARK = LColor(0.18, 0.1, 0.3, 1)
    DARK_GRAYISH = LColor(0.19, 0.15, 0.25, 1)
    DEEP = LColor(0.24, 0.07, 0.49, 1)
    DULL = LColor(0.38, 0.21, 0.63, 1)
    GRAYISH = LColor(0.4, 0.31, 0.53, 1)
    # LIGHT = LColor(0.84, 0.78, 0.93, 1)
    LIGHT_GRAYISH = LColor(0.61, 0.54, 0.72, 1)
    # PALE = LColor(0.84, 0.81, 0.89, 1)
    SOFT = LColor(0.59, 0.44, 0.82, 1)
    STRONG = LColor(0.42, 0.13, 0.87, 1)
    VIVID = LColor(0.4, 0.0, 1.0, 1)


class LightPurple(Colors):

    BRIGHT = LColor(0.89, 0.51, 0.93, 1)
    DARK = LColor(0.28, 0.1, 0.3, 1)
    DARK_GRAYISH = LColor(0.24, 0.15, 0.25, 1)
    DEEP = LColor(0.45, 0.07, 0.49, 1)
    DULL = LColor(0.59, 0.21, 0.63, 1)
    GRAYISH = LColor(0.51, 0.31, 0.53, 1)
    # LIGHT = LColor(0.91, 0.78, 0.93, 1)
    LIGHT_GRAYISH = LColor(0.71, 0.54, 0.72, 1)
    # PALE = LColor(0.88, 0.81, 0.89, 1)
    SOFT = LColor(0.78, 0.44, 0.82, 1)
    STRONG = LColor(0.8, 0.13, 0.87, 1)
    VIVID = LColor(0.9, 0.0, 1.0, 1)


class Pink(Colors):

    BRIGHT = LColor(0.93, 0.51, 0.76, 1)
    DARK = LColor(0.3, 0.1, 0.22, 1)
    DARK_GRAYISH = LColor(0.25, 0.15, 0.21, 1)
    DEEP = LColor(0.49, 0.07, 0.32, 1)
    DULL = LColor(0.63, 0.21, 0.46, 1)
    GRAYISH = LColor(0.53, 0.31, 0.44, 1)
    # LIGHT = LColor(0.93, 0.78, 0.87, 1)
    LIGHT_GRAYISH = LColor(0.72, 0.54, 0.65, 1)
    # PALE = LColor(0.89, 0.81, 0.86, 1)
    SOFT = LColor(0.82, 0.44, 0.67, 1)
    STRONG = LColor(0.87, 0.13, 0.58, 1)
    VIVID = LColor(1.0, 0.0, 0.6, 1)


class Red(Colors):

    BRIGHT = LColor(0.93, 0.51, 0.55, 1)
    DARK = LColor(0.3, 0.1, 0.12, 1)
    DARK_GRAYISH = LColor(0.25, 0.15, 0.16, 1)
    DEEP = LColor(0.49, 0.07, 0.11, 1)
    DULL = LColor(0.63, 0.21, 0.25, 1)
    GRAYISH = LColor(0.05, 0.31, 0.34, 1)
    # LIGHT = LColor(0.93, 0.78, 0.79, 1)
    LIGHT_GRAYISH = LColor(0.72, 0.54, 0.56, 1)
    # PALE = LColor(0.89, 0.81, 0.82, 1)
    SOFT = LColor(0.82, 0.44, 0.48, 1)
    STRONG = LColor(0.87, 0.13, 0.2, 1)
    VIVID = LColor(1.0, 0.0, 0.1, 1)
