"""Configuration constants for the Lead Trade Dashboard."""

# Product definitions and categories
PRODUCT_DEFINITIONS = {
    '260700': "Lead ores and concentrates - Raw materials extracted from mines.",
    '780110': "Refined lead (unwrought) - Pure lead metal (99.9%+) that hasn't been worked into products.",
    '780191': "Unwrought unrefined lead with antimony - Refers to unwrought lead that is unrefined and contains antimony as the principal othre element.",
    '780199': "Other refined lead - Unwrought refined lead metal not elsewhere specified.",
    '850710': "Lead-acid batteries for starting engines - New car batteries and other starting/lighting/ignition batteries.",
    '850720': "Other lead-acid batteries - New non-SLI batteries, including for backup power and electric vehicles.",
    '854810': "Waste batteries - Used lead-acid batteries.",
    '780200': "Lead waste and scrap - Various non-battery forms of lead metal waste."
}

# HS codes organized by category.
#
# "New Lead" (refined lead) leads the order because it is the category this
# dashboard exists to track — it is the default selection, it is listed first in
# the filters, and it therefore takes the leading, most-separable colour slots
# below.
HS_CODE_CATEGORIES = {
    'New Lead': [
        ('780110', 'Refined lead - unwrought'),
        ('780191', 'Other unwrought lead, with antimony'),
        ('780199', 'Other unrefined lead')
    ],
    'Ores & Concentrates': [
        ('260700', 'Lead ores and concentrates')
    ],
    'New Batteries': [
        ('850710', 'New lead-acid batteries for starting engines'),
        ('850720', 'Other new lead-acid batteries')
    ],
    'Used Batteries & Scrap': [
        ('854810', 'Waste batteries'),
        ('780200', 'Lead waste and scrap')
    ]
}

# Colour scheme.
#
# These are the eight slots of a colourblind-safe categorical palette, assigned
# in the fixed order above — colour follows the product, never its rank, so
# filtering the selection never repaints the survivors. The ordering is the
# CVD-safety mechanism: as listed, the worst adjacent pair in a stacked bar
# measures ΔE 9.1 (OKLab x100) under simulated colour-vision deficiency, above
# the >=8 target. Re-run the palette validator before changing the order.
#
# Yellow, aqua and magenta sit below 3:1 contrast on the white chart surface, so
# every chart ships a table view and direct value labels rather than relying on
# hue alone.
CATEGORY_COLORS = {
    'New Lead': {
        'base': '#2a78d6',  # blue
        'codes': {
            '780110': '#2a78d6',  # blue
            '780191': '#eb6834',  # orange
            '780199': '#1baf7a'   # aqua
        }
    },
    'Ores & Concentrates': {
        'base': '#eda100',  # yellow
        'codes': {
            '260700': '#eda100'
        }
    },
    'New Batteries': {
        'base': '#e87ba4',  # magenta
        'codes': {
            '850710': '#e87ba4',  # magenta
            '850720': '#008300'   # green
        }
    },
    'Used Batteries & Scrap': {
        'base': '#4a3aa7',  # violet
        'codes': {
            '854810': '#4a3aa7',  # violet
            '780200': '#e34948'   # red
        }
    }
}

# Create helper mappings
HS_CODE_COLORS = {
    hs_code: category_data['codes'][hs_code]
    for category, category_data in CATEGORY_COLORS.items()
    for hs_code in category_data['codes']
}

CATEGORY_COLOR_LIST = [CATEGORY_COLORS[cat]['base'] for cat in HS_CODE_CATEGORIES.keys()]

HS_TO_CATEGORY = {
    hs_code: category
    for category, products in HS_CODE_CATEGORIES.items()
    for hs_code, _ in products
}

# Create labels for HS codes
HS_CODE_LABELS = {
    code: f"{code} - {desc}"
    for category, products in HS_CODE_CATEGORIES.items()
    for code, desc in products
}
