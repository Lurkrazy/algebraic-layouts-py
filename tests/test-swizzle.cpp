#include "algebraic-layouts/swizzle.hpp"
#include <stdio.h>

using namespace algebraic_layouts;

template <typename T>
int apply_swizzle(const SwizzleParams<T> &layout, unsigned row, unsigned col,
                  unsigned num_banks, unsigned bank_size) {
  return layout(row, col) / bank_size % num_banks;
}

static void print_layout(const SwizzleParams<unsigned> &layout,
                         unsigned num_rows, unsigned num_cols,
                         unsigned num_banks, unsigned bank_size) {
  int row_skip = layout.stride / num_cols;
  for (unsigned row = 0; row < num_rows; row++) {
    for (unsigned col = 0; col < num_cols; col++) {
      printf("% 3d", apply_swizzle(layout, row / row_skip,
                                   col + num_cols * row % row_skip, num_banks,
                                   bank_size));
    }
    printf("\n");
  }
}

static constexpr void print_params(const SwizzleParams<unsigned> &param,
                                   unsigned num_cols) {
  auto cute_params =
      to_cute(param.stride, param.col_shift, param.col_mask, num_cols);
  printf("col_mask: 0x%x, col_shift: %d, stride: %d, row_banks: %d, "
         "total_rows: %d, cute::Swizzle<%d, %d, %d>\n",
         param.col_mask, param.col_shift, param.stride, param.row_banks,
         param.total_rows, cute_params.B, cute_params.M, cute_params.S);
}

template <unsigned num_rows, unsigned num_cols, unsigned stride,
          unsigned total_rows = 0>
static void test(unsigned real_num_cols = stride,
                 unsigned bank_size = num_cols) {
  constexpr auto param =
      make_swizzle<unsigned, num_rows, num_cols, stride, total_rows>();
  print_params(param, num_cols);
  print_layout(param, num_rows * stride / real_num_cols, real_num_cols,
               num_rows * num_cols / bank_size, bank_size);
}

int main() {
  test<8, 1, 2>();
  test<8, 1, 4>();
  test<8, 1, 8>();
  test<8, 1, 16>();

  test<8, 4, 8>();
  test<8, 4, 16>();
  test<8, 4, 48>();
  test<8, 4, 32>();
  test<8, 4, 64>();

  // TMA swizzle patterns
  test<8, 16, 16>();
  test<8, 16, 32>();
  test<8, 16, 64>();
  test<8, 16, 128>();

  test<4, 2, 8>();
  test<16, 1, 16>();

  // Row-swizzling
  test<8, 2, 24>(24);

  test<4, 4, 32>(8);
  test<4, 4, 32>(16);
}
