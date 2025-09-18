"""Unit tests for algebraic_layouts package."""

import pytest
from algebraic_layouts import SwizzleParams, make_swizzle, to_cute, shiftl


class TestShiftl:
    """Test the shiftl function."""
    
    def test_shift_left(self):
        assert shiftl(5, 2) == 20  # 5 << 2
    
    def test_shift_right(self):
        assert shiftl(20, -2) == 5  # 20 >> 2
    
    def test_no_shift(self):
        assert shiftl(10, 0) == 10


class TestSwizzleParams:
    """Test SwizzleParams class."""
    
    def test_init_default(self):
        params = SwizzleParams()
        assert params.col_mask == 0
        assert params.col_shift == 0
        assert params.stride == 0
        assert params.row_banks == 1
        assert params.total_rows == 0
    
    def test_init_with_values(self):
        params = SwizzleParams(col_mask=7, col_shift=2, stride=16, row_banks=2, total_rows=8)
        assert params.col_mask == 7
        assert params.col_shift == 2
        assert params.stride == 16
        assert params.row_banks == 2
        assert params.total_rows == 8
    
    def test_call_simple(self):
        # Test simple case: no swizzling
        params = SwizzleParams(stride=4)
        assert params(0, 0) == 0
        assert params(0, 1) == 1
        assert params(1, 0) == 4
        assert params(1, 1) == 5
    
    def test_call_with_col_swizzling(self):
        # Test with column swizzling
        params = SwizzleParams(col_mask=1, col_shift=1, stride=4)
        # For row=1, col=0: col XOR (row & col_mask) << col_shift = 0 XOR (1 & 1) << 1 = 0 XOR 2 = 2
        assert params(1, 0) == 1 * 4 + 2  # row * stride + swizzled_col
    
    def test_call_with_row_banking(self):
        # Test with row banking
        params = SwizzleParams(stride=4, row_banks=2, total_rows=4)
        # For row=2: new_row = (2 * 2) % 4 + 2 // (4 // 2) = 0 + 1 = 1
        assert params(2, 0) == 1 * 4 + 0


class TestMakeSwizzle:
    """Test make_swizzle function."""
    
    def test_power_of_two_validation(self):
        with pytest.raises(ValueError, match="must be a power of 2"):
            make_swizzle(3, 4, 8)  # num_rows not power of 2
        
        with pytest.raises(ValueError, match="must be a power of 2"):
            make_swizzle(4, 3, 8)  # num_cols not power of 2
    
    def test_stride_validation(self):
        with pytest.raises(ValueError, match="stride must not be zero"):
            make_swizzle(4, 4, 0)
    
    def test_simple_case(self):
        # Test case from C++ tests: test<8, 1, 2>
        params = make_swizzle(8, 1, 2)
        assert params.col_mask == 0x4
        assert params.col_shift == -2
        assert params.stride == 2
        assert params.row_banks == 1
        assert params.total_rows == 0
    
    def test_non_power_of_two_stride(self):
        # Test case with row banking: test<4, 2, 5, 16>
        params = make_swizzle(4, 2, 5, 16)
        assert params.col_mask == 0
        assert params.col_shift == 0
        assert params.stride == 5
        assert params.row_banks == 2
        assert params.total_rows == 16


class TestToCute:
    """Test to_cute function."""
    
    def test_zero_mask(self):
        params = SwizzleParams(col_mask=0)
        cute = to_cute(params)
        assert cute.B == 0
        assert cute.M == 0
        assert cute.S == 0
    
    def test_with_mask(self):
        # Test case: col_mask=0x7, col_shift=0, stride=8
        params = SwizzleParams(col_mask=0x7, col_shift=0, stride=8)
        cute = to_cute(params)
        assert cute.B == 3  # popcount(0x7) = 3
        assert cute.M == 0  # countr_zero(0x7) + 0 = 0 + 0 = 0
        assert cute.S == 3  # countr_zero(8) - 0 = 3 - 0 = 3


class TestIntegration:
    """Integration tests that verify outputs match C++ implementation."""
    
    def test_swizzle_patterns(self):
        """Test several swizzle patterns from the C++ test suite."""
        # Test case: 8, 1, 2
        params = make_swizzle(8, 1, 2)
        cute = to_cute(params)
        assert params.col_mask == 0x4
        assert params.col_shift == -2
        assert cute.B == 1
        assert cute.M == 0
        assert cute.S == 3
        
        # Test case: 8, 4, 8
        params = make_swizzle(8, 4, 8)
        cute = to_cute(params)
        assert params.col_mask == 0x4
        assert params.col_shift == 0
        assert cute.B == 1
        assert cute.M == 2
        assert cute.S == 3
        
        # Test case: 8, 16, 16
        params = make_swizzle(8, 16, 16)
        cute = to_cute(params)
        assert params.col_mask == 0
        assert params.col_shift == 1
        assert cute.B == 0
        assert cute.M == 0
        assert cute.S == 0