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

# Product colours ported from the original dashboard on main.
#
# Colour follows the product, never its rank, so filtering never repaints the
# survivors. Shades within a category keep individual HS codes distinguishable.
#
# Some lighter slots sit below 3:1 contrast on the white chart surface, so every
# chart also ships a table view and direct value labels rather than relying on
# colour alone.
CATEGORY_COLORS = {
    'New Lead': {
        'base': '#52525b',  # base grey
        'codes': {
            '780110': '#71717a',  # darker grey
            '780191': '#a1a1aa',  # base grey
            '780199': '#d4d4d8'   # lighter grey
        }
    },
    'Ores & Concentrates': {
        'base': '#8c6675',  # sienna brown
        'codes': {
            '260700': '#8c6675'
        }
    },
    'New Batteries': {
        'base': '#16a34a',  # forest green
        'codes': {
            '850710': '#22c55e',  # darker green
            '850720': '#4ade80'   # lighter green
        }
    },
    'Used Batteries & Scrap': {
        'base': '#ea580c',  # bright orange
        'codes': {
            '854810': '#fdba74',  # darker orange
            '780200': '#f97316'   # lighter orange
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
