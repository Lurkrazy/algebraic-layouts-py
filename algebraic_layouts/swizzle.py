"""Swizzle pattern implementations for memory layout optimization.

This module provides functionality for calculating and applying swizzle patterns
to optimize memory access patterns, particularly useful for GPU memory layouts.
"""

from typing import Union


def shiftl(x: int, shm: int) -> int:
    """Shift left or right based on shift amount.
    
    Args:
        x: Value to shift
        shm: Shift amount (positive for left shift, negative for right shift)
        
    Returns:
        Shifted value
    """
    return x << shm if shm > 0 else x >> -shm


class SwizzleParams:
    """Parameters for swizzle pattern calculation and application."""
    
    def __init__(self, col_mask: int = 0, col_shift: int = 0, stride: int = 0, 
                 row_banks: int = 1, total_rows: int = 0):
        """Initialize swizzle parameters.
        
        Args:
            col_mask: Mask for column swizzling (power-of-two component)
            col_shift: Shift amount for column swizzling
            stride: Matrix stride
            row_banks: Number of row banks (non-power-of-two component)
            total_rows: Total number of rows in matrix
        """
        self.col_mask = col_mask
        self.col_shift = col_shift
        self.stride = stride
        self.row_banks = row_banks
        self.total_rows = total_rows
    
    def __call__(self, row: int, col: int) -> int:
        """Apply swizzle pattern to get final offset.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Swizzled offset
        """
        # Handle non-power-of-two component
        if self.row_banks != 1:
            row = ((row * self.row_banks) % self.total_rows + 
                   row // (self.total_rows // self.row_banks))
        
        # Handle power-of-two component
        if self.col_mask != 0:
            col = col ^ shiftl(row & self.col_mask, self.col_shift)
        
        return row * self.stride + col


class CuteSwizzleParams:
    """Cute-style swizzle parameters for compatibility."""
    
    def __init__(self, B: int = 0, M: int = 0, S: int = 0):
        """Initialize cute swizzle parameters.
        
        Args:
            B: Bank bits
            M: Mode parameter  
            S: Stride parameter
        """
        self.B = B
        self.M = M
        self.S = S


def _popcount(x: int) -> int:
    """Count number of set bits in integer."""
    return bin(x).count('1')


def _countr_zero(x: int) -> int:
    """Count trailing zero bits."""
    if x == 0:
        return 32  # Assuming 32-bit integers like C++
    count = 0
    while (x & 1) == 0:
        x >>= 1
        count += 1
    return count


def _is_power_of_two(x: int) -> bool:
    """Check if x is a power of 2."""
    return x != 0 and (x & (x - 1)) == 0


def make_swizzle(num_rows: int, num_cols: int, stride: int, total_rows: int = 0) -> SwizzleParams:
    """Calculate swizzle parameters based on access pattern.
    
    Args:
        num_rows: Number of rows accessed in a transaction
        num_cols: Number of columns accessed in a transaction
        stride: Stride of the matrix
        total_rows: Total number of rows in the matrix (0 for auto)
        
    Returns:
        SwizzleParams object with calculated parameters
        
    Raises:
        ValueError: If parameters don't meet requirements
    """
    # Validation (equivalent to static_assert in C++)
    if not isinstance(num_rows, int) or num_rows < 0:
        raise ValueError("num_rows must be a non-negative integer")
    if not isinstance(num_cols, int) or num_cols < 0:
        raise ValueError("num_cols must be a non-negative integer")
    if not isinstance(stride, int) or stride < 0:
        raise ValueError("stride must be a non-negative integer")
    
    if not _is_power_of_two(num_cols) or num_cols == 0:
        raise ValueError("num_cols must be a power of 2")
    if not _is_power_of_two(num_rows) or num_rows == 0:
        raise ValueError("num_rows must be a power of 2")
    if stride == 0:
        raise ValueError("stride must not be zero")
    
    if total_rows == 0:
        total_rows = num_rows
    
    # Factorize stride into stride_scale * 2^stride_bits
    stride_bits = _countr_zero(stride)
    bank_bits = _countr_zero(num_cols * num_rows)
    col_bits = _countr_zero(num_cols)
    
    # Handle non-power-of-two component
    if stride != (1 << stride_bits) and col_bits > stride_bits:
        row_banks = 1 << (col_bits - stride_bits)
        if total_rows % row_banks != 0:
            raise ValueError("total_rows must be divisible by row_banks")
        
        return SwizzleParams(
            col_mask=0,
            col_shift=0,
            stride=stride,
            row_banks=row_banks,
            total_rows=total_rows
        )
    
    col_shift = col_bits
    col_mask = (1 << (bank_bits - col_bits)) - 1
    
    # Can't use the lowest bits for swizzling in this case
    if bank_bits > stride_bits:
        col_shift -= bank_bits - stride_bits
        col_mask = (((1 << (stride_bits - col_bits)) - 1) << 
                   (bank_bits - stride_bits))
    
    return SwizzleParams(
        col_mask=col_mask,
        col_shift=col_shift,
        stride=stride,
        row_banks=1,
        total_rows=0
    )


def to_cute(param: SwizzleParams) -> CuteSwizzleParams:
    """Convert SwizzleParams to CuteSwizzleParams format.
    
    Args:
        param: SwizzleParams to convert
        
    Returns:
        CuteSwizzleParams object
    """
    result = CuteSwizzleParams()
    if param.col_mask == 0:
        return result
    
    result.B = _popcount(param.col_mask)
    result.M = _countr_zero(param.col_mask) + param.col_shift
    result.S = _countr_zero(param.stride) - param.col_shift
    
    return result