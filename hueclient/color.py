import math
from typing import Tuple
from openrgb.utils import RGBColor

def _convert_xy(x: float, y: float, bri: int, gamut: dict = None) -> RGBColor:
    """
    Convert xy color to RGB color using CIE 1931 color space.
    """

    optimal_bri = max(bri, 5) / 255.0
    z = 1.0 - x - y
    Y = optimal_bri  # brightness (Y component)
    X = (Y / y) * x
    Z = (Y / y) * z

    if gamut:
        # Define the RGB gamut points in xy coordinates
        red = gamut['red']
        green = gamut['green']
        blue = gamut['blue']

        # Helper to calculate cross product
        def cross_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
            return v1[0] * v2[1] - v1[1] * v2[0]

        # Helper to check if point is within the triangle (custom gamut)
        def is_within_gamut(xy: Tuple[float, float]) -> bool:
            v0 = (green['x'] - red['x'], green['y'] - red['y'])
            v1 = (blue['x'] - red['x'], blue['y'] - red['y'])
            v2 = (xy[0] - red['x'], xy[1] - red['y'])

            cross0 = cross_product(v0, v1)
            cross1 = cross_product(v2, v1)
            cross2 = cross_product(v0, v2)

            return (cross0 * cross1 >= 0) and (cross0 * cross2 >= 0) and (cross1 * cross2 >= 0)

        # Clamp to the gamut triangle if outside
        if not is_within_gamut((x, y)):
            # If outside gamut, clip x and y to nearest point inside the triangle
            # Here, for simplicity, just use the closest color point
            x, y = min([(red['x'], red['y']), (green['x'], green['y']), (blue['x'], blue['y'])],
                    key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)

        # RGB conversion with sRGB D65 constants
        r = X * 3.2406 - Y * 1.5372 - Z * 0.4986
        g = -X * 0.9689 + Y * 1.8758 + Z * 0.0415
        b = X * 0.0557 - Y * 0.2040 + Z * 1.0570
    else:
        # RGB conversion using sRGB D65 constants
        r = X * 3.2406 - Y * 1.5372 - Z * 0.4986
        g = -X * 0.9689 + Y * 1.8758 + Z * 0.0415
        b = X * 0.0557 - Y * 0.2040 + Z * 1.0570

    # Gamma correction
    r = 12.92 * r if r <= 0.0031308 else (1.055 * pow(r, 1.0 / 2.4)) - 0.055
    g = 12.92 * g if g <= 0.0031308 else (1.055 * pow(g, 1.0 / 2.4)) - 0.055
    b = 12.92 * b if b <= 0.0031308 else (1.055 * pow(b, 1.0 / 2.4)) - 0.055

    # Clamping and brightness adjustment
    r, g, b = [max(0, min(255, int(c * optimal_bri))) for c in (r, g, b)]
    return RGBColor(r, g, b)

def convert_hue(hue: int, sat: int, bri: int) -> RGBColor:
    """
    Convert hue, saturation, and brightness to RGB color.
    """

    s = sat / 255.0
    v = bri / 255.0

    if s == 0.0:  # Achromatic (grey)
        rgb = int(v * 255)
        return RGBColor(rgb, rgb, rgb)

    hh = hue / 182.04  # scale 0-65535 hue to 0-360 degrees
    i = int(hh)
    ff = hh - i
    p = v * (1.0 - s)
    q = v * (1.0 - (s * ff))
    t = v * (1.0 - (s * (1.0 - ff)))

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    r, g, b = [max(0, min(255, int(c * 255))) for c in (r, g, b)]
    return RGBColor(r, g, b)

# Conversion for color temperature (ct) values
def _convert_ct(ct: int, bri: int) -> RGBColor:
    """
    Convert color temperature to RGB color.
    """

    hectemp = 10000 / ct
    if hectemp <= 66:
        r = 255
        g = 99.4708025861 * math.log(hectemp) - 161.1195681661
        b = 0 if hectemp <= 19 else (138.5177312231 * math.log(hectemp - 10) - 305.0447927307)
    else:
        r = 329.698727446 * pow(hectemp - 60, -0.1332047592)
        g = 288.1221695283 * pow(hectemp - 60, -0.0755148492)
        b = 255

    r, g, b = [max(0, min(255, int(c * (bri / 255.0)))) for c in (r, g, b)]
    return RGBColor(r, g, b)

def light_state_to_rgb_color(state: dict) -> RGBColor:
    """
    Convert Philips Hue light state to RGB color.
    """

    on = state["on"]["on"]
    if not on:
        # use black when light is off
        return RGBColor(0, 0, 0)

    if "color" not in state:
        # use warm white when light has no color control
        return _convert_ct(370, 255)

    color = state["color"]
    bri = state["dimming"]["brightness"] * 100
    if "xy" in color:
        x = color["xy"]["x"]
        y = color["xy"]["y"]
        return _convert_xy(x, y, bri)
    elif "ct" in color:
        ct = color["ct"]
        gamut = state["color"].get("gamut")
        return _convert_ct(ct, bri, gamut)
    elif "hue" in color and "sat" in color:
        hue = color["hue"]
        sat = color["sat"]
        return convert_hue(hue, sat, bri)
    else:
        raise ValueError(f"Unknown color format: {color}")
