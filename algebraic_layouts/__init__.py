"""Algebraic Layouts Python Library

A Python implementation of algebraic memory layout optimizations,
particularly swizzle patterns for efficient memory access.
"""

from .swizzle import SwizzleParams, CuteSwizzleParams, make_swizzle, to_cute, shiftl

__version__ = "0.1.0"
__all__ = ["SwizzleParams", "CuteSwizzleParams", "make_swizzle", "to_cute", "shiftl"]