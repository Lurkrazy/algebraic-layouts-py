#!/usr/bin/env python3
"""Example usage of the algebraic_layouts library."""

from algebraic_layouts import make_swizzle, to_cute


def example_basic_usage():
    """Demonstrate basic swizzle pattern creation and usage."""
    print("=== Basic Usage Example ===")
    
    # Create swizzle parameters for a 4x4 access pattern with stride 16
    params = make_swizzle(num_rows=4, num_cols=4, stride=16)
    
    print(f"Swizzle Parameters:")
    print(f"  col_mask: 0x{params.col_mask:x}")
    print(f"  col_shift: {params.col_shift}")
    print(f"  stride: {params.stride}")
    print(f"  row_banks: {params.row_banks}")
    print(f"  total_rows: {params.total_rows}")
    
    # Convert to cute format
    cute = to_cute(params)
    print(f"  cute::Swizzle<{cute.B}, {cute.M}, {cute.S}>")
    
    print("\nMemory layout (first 4x4 block):")
    for row in range(4):
        offsets = []
        for col in range(4):
            offset = params(row, col)
            offsets.append(f"{offset:3d}")
        print("  " + " ".join(offsets))


def example_bank_conflicts():
    """Demonstrate how swizzling reduces bank conflicts."""
    print("\n=== Bank Conflict Reduction Example ===")
    
    # Without swizzling (identity layout)
    print("Without swizzling:")
    for row in range(4):
        banks = []
        for col in range(4):
            offset = row * 4 + col
            bank = offset % 4  # Assume 4 memory banks
            banks.append(f"{bank}")
        print("  " + " ".join(banks))
    
    # With swizzling
    print("\nWith swizzling:")
    params = make_swizzle(num_rows=4, num_cols=4, stride=4)
    
    for row in range(4):
        banks = []
        for col in range(4):
            offset = params(row, col)
            bank = offset % 4  # Assume 4 memory banks
            banks.append(f"{bank}")
        print("  " + " ".join(banks))


def example_gpu_tensor_layout():
    """Example showing GPU tensor memory layout optimization."""
    print("\n=== GPU Tensor Layout Example ===")
    
    # Common GPU memory access pattern: 8 threads accessing 16 elements each
    params = make_swizzle(num_rows=8, num_cols=16, stride=128)
    
    print(f"GPU Memory Layout Parameters:")
    print(f"  Threads: 8, Elements per thread: 16, Memory stride: 128")
    print(f"  col_mask: 0x{params.col_mask:x}, col_shift: {params.col_shift}")
    
    # Show memory bank distribution for first few accesses
    print("\nMemory bank distribution (first 8x8 region, assuming 8 banks):")
    for row in range(8):
        banks = []
        for col in range(8):
            offset = params(row, col)
            bank = offset % 8
            banks.append(f"{bank}")
        print("  " + " ".join(banks))


if __name__ == "__main__":
    example_basic_usage()
    example_bank_conflicts() 
    example_gpu_tensor_layout()