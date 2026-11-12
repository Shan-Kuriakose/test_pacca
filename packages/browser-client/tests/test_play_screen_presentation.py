"""AC2 acceptance tests: the play screen is comfortable and accessible.

Contrast is computed from the tokens the styles declare, following the WCAG
relative-luminance formula, rather than eyeballed: every text token must
reach 4.5:1 against its pair and every play-surface boundary token 3:1.
Because phone-sized screens are the point of this story, the entry page must
carry the device-width viewport meta and the screen must expose real
accessible names.
"""

import re
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
STYLES_PATH = PACKAGE_ROOT / "src" / "styles.css"
INDEX_HTML_PATH = PACKAGE_ROOT / "index.html"
PLAY_SCREEN_PATH = PACKAGE_ROOT / "src" / "ui" / "PlayScreen.tsx"

_COLOR_PROPERTY = re.compile(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})(?![\w-])")


def _channel_linears(color: str) -> tuple[float, float, float]:
    digits = color[1:]
    if len(digits) in (3, 4):
        digits = "".join(char + char for char in digits)

    def channel(pair: str) -> float:
        value = int(pair, 16) / 255
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    return channel(digits[0:2]), channel(digits[2:4]), channel(digits[4:6])


def _luminance(color: str) -> float:
    red, green, blue = _channel_linears(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(fore: str, back: str) -> float:
    fore_alpha = 1.0
    if len(fore) == 9:
        fore_alpha = int(fore[7:9], 16) / 255
        fore = fore[0:7]
    if fore_alpha < 1.0:
        fore_red, fore_green, fore_blue = _channel_linears(fore)
        back_red, back_green, back_blue = _channel_linears(back)
        fore = _blend(fore_red, fore_green, fore_blue, fore_alpha,
                      back_red, back_green, back_blue)
    fore_light = _luminance(fore)
    back_light = _luminance(back)
    lighter = max(fore_light, back_light)
    darker = min(fore_light, back_light)
    return (lighter + 0.05) / (darker + 0.05)


def _blend(red: float, green: float, blue: float,
           alpha: float, over_red: float, over_green: float, over_blue: float) -> str:
    def pixel(channel: float, over: float) -> int:
        return round(255 * (alpha * channel + (1 - alpha) * over))

    return "#{:02x}{:02x}{:02x}".format(
        pixel(red, over_red), pixel(green, over_green), pixel(blue, over_blue)
    )


def _declared_colors(source: str) -> dict:
    return dict(re.findall(_COLOR_PROPERTY, source))


def test_screen_tokens_meet_wcag_contrast_ratios():
    source = STYLES_PATH.read_text(encoding="utf-8")
    tokens = _declared_colors(source)

    text_roles = [name.split("-", 1)[1] for name in tokens if name.startswith("fg-")]
    boundary_roles = [name.split("-", 1)[1] for name in tokens
                      if name.startswith("stroke-")]
    assert text_roles, "the styles declare no --fg-* text tokens to review"
    assert boundary_roles, "the styles declare no --stroke-* boundary tokens to review"

    weaknesses = []
    for role in text_roles:
        background = f"bg-{role}"
        assert background in tokens, f"--bg-{role} must exist to pair with --fg-{role}"
        ratio = _contrast_ratio(tokens[f"fg-{role}"], tokens[background])
        if ratio < 4.5:
            weaknesses.append(f"--fg-{role} on --{background}: {ratio:.2f}")
    for role in boundary_roles:
        background = f"bg-{role}"
        assert background in tokens, f"--bg-{role} must exist to pair with --stroke-{role}"
        ratio = _contrast_ratio(tokens[f"stroke-{role}"], tokens[background])
        if ratio < 3.0:
            weaknesses.append(f"--stroke-{role} on --{background}: {ratio:.2f}")

    assert weaknesses == [], (
        "the following token pairs fall below their WCAG minimum: "
        + "; ".join(weaknesses)
    )


def test_the_play_screen_exposes_accessible_names_and_a_phone_viewport():
    index_html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    play_screen = PLAY_SCREEN_PATH.read_text(encoding="utf-8")

    viewport = re.search(r'<meta[^>]+name="viewport"[^>]*>', index_html)
    assert viewport, "the entry page must carry a viewport meta tag for phone browsers"
    assert "width=device-width" in viewport.group(0)

    canvas = re.search(r"<canvas[^>]*>", play_screen)
    assert canvas, "the play screen must render the board as a labelled canvas"
    assert "aria-label" in canvas.group(0) or "aria-labelledby" in canvas.group(0)

    live_region = re.search(
        r"aria-live=[\"'](?:polite|assertive)[\"']", play_screen
    )
    assert live_region, (
        "the score must be announced through an aria-live region, not painted "
        "pixels alone"
    )
