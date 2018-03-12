"""
This module contains functions to convert units.
"""
import numpy as np


def Celsius2Kelvin(value):
    """
    Converts a Temperature from °C to K.

    Args:
        value: Value, list or array containing temperatures in °C.

    Returns:
        Same as input format, containing values in K.
    """
    return np.add(value,273.15)


def Kelvin2Celsius(value):
    """
    Converts a Temperature from K to °C.

    Args:
        value: Value, list or array containing temperatures in K.

    Returns:
        Same as input format, containing values in °C.
    """
    return np.subtract(value,273.15)