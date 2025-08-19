// This file is a part of Algebraic-Layouts. License is MIT.
#pragma once

#include <bit>
#include <stdexcept>

namespace algebraic_layouts {

template <typename T> static constexpr T shiftl(T x, int shm) {
  return shm > 0 ? x << shm : x >> -shm;
}

template <typename T> struct SwizzleParams {
  // For power-of-two component
  T col_mask;
  int col_shift;
  T stride;
  // For non-power-of-two component
  T row_banks;
  T total_rows;

  constexpr T operator()(T row, T col) const {
    if (row_banks != 1) {
      row = row / row_banks + (row % row_banks) * (total_rows / row_banks);
    }
    col = col ^ shiftl(row & col_mask, col_shift);
    return row * stride + col;
  }
};

/// @brief Calculate swizzle parameter based on the access pattern
/// @tparam T type of offset
/// @tparam num_rows number of rows accessed in a transaction
/// @tparam num_cols number of columns accessed in a transaction
/// @tparam stride stride of the matrix
/// @tparam total_rows total number of rows in the matrix
/// @return a set of swizzle parameters
template <typename T, T num_rows, T num_cols, T stride, T total_rows = 0>
static constexpr auto make_swizzle() {
  static_assert(num_cols != 0 && (num_cols & (num_cols - 1)) == 0,
                "num_cols must be a power of 2");
  static_assert(num_rows != 0 && (num_rows & (num_rows - 1)) == 0,
                "num_rows must be a power of 2");
  static_assert(stride != 0, "stride must not be zero");

  // Factorize stride into stride_scalek * 2^stride_bits
  int stride_bits = std::countr_zero(stride);
  T stride_scale = stride / (1 << stride_bits);

  int bank_bits = std::countr_zero(num_cols * num_rows);
  int col_bits = std::countr_zero(num_cols);
  T row_banks = 1;

  // Handle non-power-of-two component
  if (bank_bits < stride_bits && stride_scale != 1) {
    bank_bits = stride_bits;
    row_banks = num_rows / stride_bits;
    if (total_rows == 0 || total_rows % row_banks == 0)
      throw std::invalid_argument("total_rows must be divisible by row_banks");
  }

  int col_shift = std::countr_zero(num_cols);
  T col_mask = (1 << (bank_bits - col_bits)) - 1;

  // Can't use the lowest bits for swizzling in this case
  if (bank_bits > stride_bits) {
    col_shift -= bank_bits - stride_bits;
    col_mask = ((1 << (stride_bits - col_bits)) - 1)
               << (bank_bits - stride_bits);
  }

  SwizzleParams<T> result;
  result.col_shift = col_shift;
  result.col_mask = col_mask;
  result.stride = stride;
  result.row_banks = row_banks;
  result.total_rows = total_rows;

  return result;
}

struct CuteSwizzleParams {
  int B, M, S;
};

static constexpr auto to_cute(unsigned stride, unsigned col_shift,
                              unsigned col_mask, unsigned num_cols = 1) {
  CuteSwizzleParams result;
  result.B = std::popcount(col_mask);
  result.M = std::countr_zero(num_cols);
  unsigned col_mask_zeros = col_mask == 0 ? 0 : std::countr_zero(col_mask);
  result.S = std::countr_zero(stride) + col_mask_zeros - result.M;
  return result;
}

} // namespace algebraic_layouts
