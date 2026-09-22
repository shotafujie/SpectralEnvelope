// WORLD を JS から呼ぶための薄い C ラッパー（006-wasm-world）。
// sp / ap は行優先の平坦な配列で受け渡し、WORLD が要求する行ポインタの配列はここで組む。
#include <vector>

#include "world/cheaptrick.h"
#include "world/d4c.h"
#include "world/harvest.h"
#include "world/synthesis.h"

static std::vector<double*> rows(double* flat, int n, int width) {
  std::vector<double*> r(n);
  for (int i = 0; i < n; ++i) r[i] = flat + static_cast<size_t>(i) * width;
  return r;
}

extern "C" {

int world_n_frames(int len, int fs, double frame_period) {
  return GetSamplesForHarvest(fs, len, frame_period);
}

void world_harvest(const double* x, int len, int fs, double frame_period, double* f0, double* t) {
  HarvestOption option;
  InitializeHarvestOption(&option);
  option.frame_period = frame_period;
  Harvest(x, len, fs, &option, t, f0);
}

void world_cheaptrick(const double* x, int len, int fs, const double* f0, const double* t, int n,
                      int fft_size, double* sp) {
  CheapTrickOption option;
  InitializeCheapTrickOption(fs, &option);
  option.fft_size = fft_size;
  auto r = rows(sp, n, fft_size / 2 + 1);
  CheapTrick(x, len, fs, t, f0, n, &option, r.data());
}

void world_d4c(const double* x, int len, int fs, const double* f0, const double* t, int n,
               int fft_size, double* ap) {
  D4COption option;
  InitializeD4COption(&option);
  auto r = rows(ap, n, fft_size / 2 + 1);
  D4C(x, len, fs, t, f0, n, fft_size, &option, r.data());
}

void world_synthesize(const double* f0, double* sp, double* ap, int n, int fft_size, int fs,
                      double frame_period, double* y, int y_len) {
  auto rs = rows(sp, n, fft_size / 2 + 1);
  auto ra = rows(ap, n, fft_size / 2 + 1);
  Synthesis(f0, n, rs.data(), ra.data(), fft_size, frame_period, fs, y_len, y);
}

}  // extern "C"
