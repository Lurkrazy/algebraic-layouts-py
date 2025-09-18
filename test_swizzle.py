#!/usr/bin/env python3
"""Test script for algebraic layouts swizzle functionality.

This script replicates the behavior of the C++ test-swizzle.cpp to verify
that the Python implementation produces identical results.
"""

from algebraic_layouts import SwizzleParams, make_swizzle, to_cute


def apply_swizzle(layout: SwizzleParams, row: int, col: int, 
                  num_banks: int, bank_size: int) -> int:
    """Apply swizzle and calculate bank number."""
    return layout(row, col) // bank_size % num_banks


def print_layout(layout: SwizzleParams, num_rows: int, num_cols: int,
                num_banks: int, bank_size: int) -> None:
    """Print the swizzle layout pattern."""
    row_skip = layout.stride // num_cols
    for row in range(num_rows):
        row_values = []
        for col in range(num_cols):
            bank = apply_swizzle(
                layout, 
                row // row_skip,
                col + (num_cols * row) % row_skip,
                num_banks, 
                bank_size
            )
            row_values.append(f"{bank:3d}")
        print("".join(row_values))


def print_params(param: SwizzleParams, num_cols: int) -> None:
    """Print swizzle parameters in the same format as C++."""
    cute_params = to_cute(param)
    print(f"col_mask: 0x{param.col_mask:x}, col_shift: {param.col_shift}, "
          f"stride: {param.stride}, row_banks: {param.row_banks}, "
          f"total_rows: {param.total_rows}, cute::Swizzle<{cute_params.B}, "
          f"{cute_params.M}, {cute_params.S}>")


def test(num_rows: int, num_cols: int, stride: int, total_rows: int = None,
         real_num_cols: int = None, bank_size: int = None) -> None:
    """Test function that mirrors the C++ template test function."""
    if total_rows is None:
        total_rows = num_rows
    if real_num_cols is None:
        real_num_cols = stride
    if bank_size is None:
        bank_size = num_cols
        
    param = make_swizzle(num_rows, num_cols, stride, total_rows)
    print_params(param, num_cols)
    
    layout_rows = max(total_rows, num_rows * stride // real_num_cols)
    num_banks = num_rows * num_cols // bank_size
    
    print_layout(param, layout_rows, real_num_cols, num_banks, bank_size)


def main():
    """Run all test cases from the C++ version."""
    test(8, 1, 2)
    test(8, 1, 4)
    test(8, 1, 8)
    test(8, 1, 16)
    test(8, 1, 32)

    test(8, 4, 8)
    test(8, 4, 16)
    test(8, 4, 48)
    test(8, 4, 32)
    test(8, 4, 64)

    # TMA swizzle patterns
    test(8, 16, 16)
    test(8, 16, 32)
    test(8, 16, 64)
    test(8, 16, 128)

    test(4, 2, 8)
    test(16, 1, 16)

    # Row-swizzling
    test(4, 2, 5, 16)
    test(4, 2, 9, 16)
    test(2, 4, 9, 16)

    test(4, 4, 32, real_num_cols=8)
    test(4, 4, 32, real_num_cols=16)
    test(4, 2, 16, real_num_cols=8)


if __name__ == "__main__":
    main()