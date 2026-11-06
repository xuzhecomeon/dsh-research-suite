#!/usr/bin/env python3
"""
Style manager for science-figures skill.
Integrates scienceplots library with fallback built-in styles.
"""
import matplotlib.pyplot as plt
import warnings

# scienceplots style aliases map to their actual style names
SCIENCEPLOTS_STYLES = [
    "ieee",
    "nature",
    "springer",
    "aaas",
    "science",
    "lancet",
    "acs",
    "aps",
]

# Built-in fallback styles that approximate scienceplots when it's not installed
# Each entry: (name, rc_params_dict)
BUILTIN_STYLES = {
    "ieee": {
        "figure.figsize": (6.5, 4.5),
        "figure.dpi": 300,
        "font.size": 8,
        "font.family": "serif",
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "lines.linewidth": 1.2,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    },
    "nature": {
        "figure.figsize": (7, 5),
        "figure.dpi": 300,
        "font.size": 7,
        "font.family": "sans-serif",
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "axes.linewidth": 0.6,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "lines.linewidth": 1.0,
        "grid.alpha": 0.2,
    },
    "springer": {
        "figure.figsize": (7.8, 5.2),
        "figure.dpi": 300,
        "font.size": 8,
        "font.family": "serif",
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "axes.linewidth": 0.7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "lines.linewidth": 1.1,
        "grid.alpha": 0.3,
    },
    "aaas": {
        "figure.figsize": (5.5, 4),
        "figure.dpi": 300,
        "font.size": 7,
        "font.family": "sans-serif",
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "axes.linewidth": 0.5,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "lines.linewidth": 1.0,
    },
    "science": {
        "figure.figsize": (5.5, 4.5),
        "figure.dpi": 300,
        "font.size": 7,
        "font.family": "sans-serif",
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "axes.linewidth": 0.5,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "lines.linewidth": 1.0,
    },
    "lancet": {
        "figure.figsize": (8, 5.5),
        "figure.dpi": 300,
        "font.size": 9,
        "font.family": "serif",
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "lines.linewidth": 1.3,
    },
    "acs": {
        "figure.figsize": (6, 4.5),
        "figure.dpi": 300,
        "font.size": 8,
        "font.family": "sans-serif",
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "lines.linewidth": 1.2,
    },
    "aps": {
        "figure.figsize": (6.5, 4.5),
        "figure.dpi": 300,
        "font.size": 8,
        "font.family": "serif",
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "axes.linewidth": 0.7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "lines.linewidth": 1.1,
    },
}

# Color palettes per journal style
COLOR_PALETTES = {
    "ieee": ["#0072BD", "#D95319", "#EDB120", "#7E2F8E", "#77AC30", "#4DBEEE", "#A2142F"],
    "nature": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000"],
    "springer": ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F", "#FDAF91", "#AD002A", "#1B1919"],
    "aaas": ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280", "#BB0021", "#5F559B", "#A20056"],
    "science": ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280", "#BB0021"],
    "lancet": ["#00468B", "#ED0000", "#42B540", "#0099B4", "#525252", "#7F6F00", "#ED7D31"],
    "acs": ["#E37222", "#07889B", "#66B9BF", "#EEAA7B", "#155265", "#E3A41B", "#7F7F7F"],
    "aps": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"],
}

DEFAULT_STYLE = "nature"
SCIENCEPLOTS_AVAILABLE = False
SCIENCEPLOTS_UNREACHABLE = False


def _check_scienceplots():
    """Check if scienceplots is available and can be imported."""
    global SCIENCEPLOTS_AVAILABLE, SCIENCEPLOTS_UNREACHABLE
    if SCIENCEPLOTS_UNREACHABLE:
        return False
    try:
        import scienceplots
        SCIENCEPLOTS_AVAILABLE = True
        return True
    except ImportError:
        SCIENCEPLOTS_AVAILABLE = False
        SCIENCEPLOTS_UNREACHABLE = True
        return False


def setup_style(style_name=DEFAULT_STYLE, custom_rc=None):
    """
    Set up the matplotlib style for the given journal.

    Args:
        style_name: One of the SCIENCEPLOTS_STYLES
        custom_rc: Optional dict of rcParams overrides

    Returns:
        dict with color palette and style metadata
    """
    style_name = style_name.lower().strip()
    if style_name not in SCIENCEPLOTS_STYLES and style_name not in BUILTIN_STYLES:
        print(f"Warning: Unknown style '{style_name}', falling back to 'nature'")
        style_name = "nature"

    # scienceplots only provides 3 secondary styles: ieee, nature, science
    _SCIENCEPLOTS_REAL_STYLES = {"ieee", "nature", "science"}

    if _check_scienceplots():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if style_name in _SCIENCEPLOTS_REAL_STYLES:
                plt.style.use(["science", style_name])
            else:
                # Use "science" base + our built-in rc params for unsupported styles
                plt.style.use("science")
                rc = BUILTIN_STYLES.get(style_name, BUILTIN_STYLES["nature"])
                plt.rcParams.update(rc)
    else:
        rc = BUILTIN_STYLES.get(style_name, BUILTIN_STYLES["nature"])
        plt.rcParams.update(rc)

    # Always apply a few quality defaults
    # Disable LaTeX (usetex) to avoid LaTeX dependency issues;
    # matplotlib's built-in mathtext handles math rendering fine.
    # Also provide sans-serif fallbacks for serif fonts (Windows lacks Times).
    plt.rcParams.update({
        "text.usetex": False,
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times", "serif"],
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "axes.unicode_minus": False,
    })

    # Apply any user overrides
    if custom_rc:
        plt.rcParams.update(custom_rc)

    return {
        "colors": COLOR_PALETTES.get(style_name, COLOR_PALETTES["nature"]),
        "name": style_name,
        "scienceplots_loaded": SCIENCEPLOTS_AVAILABLE,
    }


def list_styles():
    """Return list of available style names."""
    return SCIENCEPLOTS_STYLES[:]


def reset_style():
    """Reset matplotlib rcParams to defaults."""
    plt.rcdefaults()
