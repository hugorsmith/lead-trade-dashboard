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

# HS codes organized by category
HS_CODE_CATEGORIES = {
    'Ores & Concentrates': [
        ('260700', 'Lead ores and concentrates')
    ],
    'New Lead': [
        ('780110', 'Refined lead - unwrought'),
        ('780191', 'Other unwrought lead, with antimony'),
        ('780199', 'Other unrefined lead')
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

# Color scheme for categories
CATEGORY_COLORS = {
    'Ores & Concentrates': {
        'base': '#8c6675',  # Sienna brown
        'codes': {
            '260700': '#8c6675'  # Same as base since only one code
        }
    },
    'New Lead': {
        'base': '#52525b',  # Base gray
        'codes': {
            '780110': '#71717a',  # Darker gray
            '780191': '#a1a1aa',  # Base gray
            '780199': '#d4d4d8'   # Lighter gray
        }
    },
    'New Batteries': {
        'base': '#16a34a',  # Forest green
        'codes': {
            '850710': '#22c55e',  # Darker green
            '850720': '#4ade80'   # Lighter green
        }
    },
    'Used Batteries & Scrap': {
        'base': '#ea580c',  # Bright orange
        'codes': {
            '854810': '#fdba74',  # Darker orange
            '780200': '#f97316'   # Lighter orange
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
