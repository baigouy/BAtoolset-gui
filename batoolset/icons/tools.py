# TODO maybe worth speeding this up especially calls to icons that are not used and or the full list of icons that can take time --> need think

from batoolset.settings.global_settings import set_UI  # set the UI to qtpy

set_UI()
import qtawesome as qta
from batoolset.strings.tools import levenshtein_distance
from qtpy.QtGui import QColor

import re

STYLE_SUFFIXES = [
    "outline", "outlined", "fill", "filled",
    "bold", "thin", "light", "regular",
    "circle", "square",
]

# Cache for available icons
_available_icons_cache = None


def normalize_icon_name(name):
    """Normalize icon name to its semantic core."""
    base = name.split('.')[-1].lower()

    # remove common legacy markers
    base = re.sub(r"-o$", "", base)
    base = re.sub(r"-alt$", "", base)

    # remove style suffixes
    for suffix in STYLE_SUFFIXES:
        base = re.sub(rf"-{suffix}$", "", base)

    return base


def get_closest_icon_name(target_name, available_icons):
    """Find the closest matching icon using semantic matching and Levenshtein distance."""
    target_norm = normalize_icon_name(target_name)
    target_base = target_name.split('.')[-1] if '.' in target_name else target_name
    target_base_norm = normalize_icon_name(target_base)

    best_score = float('inf')
    best_icon = None

    # Split target into words for matching
    target_words = set(target_norm.split('-')) if target_norm else set()

    for icon in available_icons:
        icon_norm = normalize_icon_name(icon)
        icon_base = icon.split('.')[-1] if '.' in icon else icon
        icon_base_norm = normalize_icon_name(icon_base)

        # Strong semantic preference - normalized bases match exactly
        if icon_base_norm == target_base_norm:
            return icon  # Perfect match, return immediately
        elif icon_norm == target_norm:
            score = 0.5
        elif icon_base == target_base:
            score = 1
        elif icon_norm.startswith(target_norm):
            score = 2
        elif target_norm in icon_norm:
            score = 3
        elif target_words and all(word in icon_norm for word in target_words if word):
            score = 4
        else:
            # Only compute Levenshtein for icons with some similarity
            # Skip if length difference is too large
            len_diff = abs(len(target_base_norm) - len(icon_base_norm))
            if len_diff > max(len(target_base_norm), len(icon_base_norm)) * 0.6:
                continue

            # Skip if no common characters at all
            if target_base_norm and icon_base_norm:
                common = set(target_base_norm) & set(icon_base_norm)
                if len(common) < min(3, len(target_base_norm) * 0.3):
                    continue

            dist = levenshtein_distance(target_base_norm, icon_base_norm)

            # Reject if distance is too large
            max_dist = max(len(target_base_norm), len(icon_base_norm)) * 0.5
            if dist > max_dist:
                continue

            score = 10 + dist

        if score < best_score:
            best_score = score
            best_icon = icon

    # If no good match found (score too high), return None to trigger help icon
    if best_score > 15:  # Threshold for "no good match"
        return None

    return best_icon if best_icon else None


def get_available_icons():
    global _available_icons_cache

    if _available_icons_cache is not None:
        return _available_icons_cache

    # Force initialization by creating a dummy icon
    try:
        qta.icon('fa5s.home')
    except Exception:
        pass

    # Get the charmap which contains prefix -> {icon_name: code} mappings
    charmap = qta._instance().charmap

    icon_names = []

    # Iterate through each font prefix (fa5s, mdi, etc.)
    for prefix, icons_dict in charmap.items():
        if isinstance(icons_dict, dict):
            # Add all icon names with their prefix
            for icon_name in icons_dict.keys():
                icon_names.append(f"{prefix}.{icon_name}")

    _available_icons_cache = sorted(icon_names)
    return _available_icons_cache


def get_icon(icon_name, color=None, color_disabled=None, **qta_kwargs):
    """
    Get an icon with fallback support for different icon sets.

    Args:
        icon_name (str): The name of the icon (e.g., 'fa.newspaper-o').
        color (QColor or str or None): Icon color.
        color_disabled (QColor or str or None): Disabled icon color.
        **qta_kwargs: Any additional qtawesome options (options, scale_factor, offset, etc.)

    Returns:
        QIcon
    """

    def to_color_str(c):
        if isinstance(c, QColor):
            return c.name()
        return c

    color_str = to_color_str(color)
    color_disabled_str = to_color_str(color_disabled)

    def make_icon(name):
        kwargs = dict(qta_kwargs)

        if color_str is not None:
            kwargs.setdefault("color", color_str)
        if color_disabled_str is not None:
            kwargs.setdefault("color_disabled", color_disabled_str)

        return qta.icon(name, **kwargs)

    # Try exact icon
    try:
        return make_icon(icon_name)
    except Exception:
        pass

    # Try common icon family upgrades
    if icon_name.startswith('fa.'):
        base_name = icon_name[3:]
        normalized_base = base_name.replace('-o', '').replace('-alt', '')

        for prefix in ['fa5s.', 'fa5.', 'fa5b.', 'fa6s.', 'fa6.', 'fa6b.']:
            try:
                return make_icon(prefix + normalized_base)
            except Exception:
                pass

    # Fuzzy fallback
    available_icons = get_available_icons()
    closest_icon = get_closest_icon_name(icon_name, available_icons)

    if closest_icon is None:
        return make_icon("mdi.help")

    try:
        return make_icon(closest_icon)
    except Exception:
        return make_icon("mdi.help")



if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    import sys

    # Create a QApplication instance
    app = QApplication(sys.argv)

    if False:
        # Get all available icon names
        # Get the QtAwesome instance and access its icon map
        # Force initialization by creating a dummy icon first
        try:
            qta.icon('fa5s.home')
        except:
            pass

        # Now try to get the icon names
        icon_names = list(qta._instance().charmap.keys())
        print(icon_names)
        print(f"Total icons: {len(icon_names)}")
        sys.exit(0)

    # Icons to test (mix of valid, legacy, and invalid)
    test_icons = [
        "fa.newspaper-o",
        "fa.save",
        "fa.folder",
        "fa.file-o",
        "fa.plus",
        "fa.times",
        "fa.trash-o",
        "fa.pencil",
        "fa.cog",
        "fa.search",
        "fa.home",
        "fa.this-does-not-exist",  # intentional failure
        "ri.layout-row-line",  # intentional failure
        'fa.folder-open-o',
        'fa.check'
    ]

    window = QWidget()
    window.setWindowTitle("qtawesome icon loading test")

    layout = QVBoxLayout(window)

    for icon_name in test_icons:
        icon = get_icon(icon_name)

        label = QLabel(f"{icon_name}")
        label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(label)

        print(f"Requested icon: {icon_name}")

    window.show()
    sys.exit(app.exec_())