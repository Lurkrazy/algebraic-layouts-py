# Algebraic-layouts

A Python implementation of algebraic memory layout optimizations, particularly swizzle patterns for efficient memory access. This library is useful for GPU memory layout optimization and related applications.

## Installation

```bash
pip install algebraic-layouts
```

Or for development:

```bash
git clone https://github.com/Lurkrazy/algebraic-layouts-py.git
cd algebraic-layouts-py
pip install -e .
```

## Usage

```python
from algebraic_layouts import make_swizzle, SwizzleParams

# Create swizzle parameters for a 4x4 access pattern with stride 32
params = make_swizzle(num_rows=4, num_cols=4, stride=32)

# Apply swizzle to get memory offset
offset = params(row=2, col=3)

# Print swizzle parameters
print(f"col_mask: 0x{params.col_mask:x}")
print(f"col_shift: {params.col_shift}")
print(f"stride: {params.stride}")
```

## API Reference

### SwizzleParams

A class that represents swizzle pattern parameters and can be called to compute swizzled memory offsets.

### make_swizzle(num_rows, num_cols, stride, total_rows=0)

Calculate optimal swizzle parameters based on access pattern.

**Parameters:**
- `num_rows`: Number of rows accessed in a transaction (must be power of 2)
- `num_cols`: Number of columns accessed in a transaction (must be power of 2)
- `stride`: Stride of the matrix (must be non-zero)
- `total_rows`: Total number of rows in the matrix (default: same as num_rows)

**Returns:** SwizzleParams object

### CuteSwizzleParams

Compatible format for cute-style swizzle parameters.

### to_cute(param)

Convert SwizzleParams to CuteSwizzleParams format.

## Testing

Run the test suite to verify the implementation matches the C++ reference:

```bash
python test_swizzle.py
```

## License

MIT License - see LICENSE file for details.

## Original C++ Implementation

This Python library is based on the C++ algebraic layouts implementation. The original algorithms and concepts are implemented in the `include/algebraic-layouts/swizzle.hpp` header file.

