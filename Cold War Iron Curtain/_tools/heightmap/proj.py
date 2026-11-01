"""The map's projection: Patterson cylindrical, 84N at the top edge, Bering Strait at the left edge.

Pixel (x, y) here is image space (row 0 = north). Game z = H - y.
"""
import numpy as np

W, H = 4864, 2560
LON0 = -169.0          # left edge: Bering Strait, so Chukotka stays with Russia
LAT_N = 84.0
_C = (1.0148, 0.23185, -0.14499, 0.02406)
K = W / (2 * np.pi)    # pixels per radian of longitude


def patt(phi):
    c1, c3, c5, c7 = _C
    return c1 * phi + c3 * phi**5 + c5 * phi**7 + c7 * phi**9


def patt_inv(y):
    c1, c3, c5, c7 = _C
    p = y / c1
    for _ in range(12):
        p = p - (patt(p) - y) / (c1 + 5 * c3 * p**4 + 7 * c5 * p**6 + 9 * c7 * p**8)
    return p


TOP = patt(np.radians(LAT_N))


def to_px(lon, lat):
    """lon/lat (deg) -> image x, y (float pixels, pixel centres at .5)."""
    x = ((np.asarray(lon, np.float64) - LON0) % 360.0) / 360.0 * W
    y = (TOP - patt(np.radians(lat))) * K
    return x, y


def to_lonlat(x, y):
    """image x, y (float pixels) -> lon in [-180, 180), lat (deg)."""
    lon = (LON0 + np.asarray(x, np.float64) / W * 360.0 + 180.0) % 360.0 - 180.0
    lat = np.degrees(patt_inv(TOP - np.asarray(y, np.float64) / K))
    return lon, lat


def grid():
    """lon, lat of every pixel centre, float32 (H, W)."""
    lon, _ = to_lonlat(np.arange(W) + 0.5, 0)
    _, lat = to_lonlat(0, np.arange(H) + 0.5)
    return (np.broadcast_to(lon[None, :], (H, W)).astype(np.float32),
            np.broadcast_to(lat[:, None], (H, W)).astype(np.float32))


if __name__ == "__main__":
    for lo, la in [(0, 0), (-0.13, 51.51), (179.9, -60), (-169.0, 84.0)]:
        x, y = to_px(lo, la)
        lo2, la2 = to_lonlat(x, y)
        assert abs((lo2 - lo + 180) % 360 - 180) < 1e-6 and abs(la2 - la) < 1e-6, (lo, la, lo2, la2)
    print("south edge lat", round(float(to_lonlat(0, H)[1]), 2), "| W*H", W * H, "<= 13238272:", W * H <= 13238272)
