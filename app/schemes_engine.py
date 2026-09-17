"""
Disease-based government scheme suggestion — static, curated mapping.
"""

SCHEME_RULES = {
    "tb": {
        "keywords": ["tb", "tuberculosis", "tapedik", "kshay rog"],
        "schemes": [
            {
                "scheme_name": "Nikshay Poshan Yojana",
                "description": "TB patients ko treatment ke dauran nutritional support ke liye financial assistance milti hai (₹500/month direct benefit transfer).",
            }
        ],
    },
    "cancer": {
        "keywords": ["cancer", "kainsar", "tumor", "tumour"],
        "schemes": [
            {
                "scheme_name": "Ayushman Bharat (PM-JAY)",
                "description": "Cancer sahit kai serious bimariyon ke liye ₹5 lakh tak ka cashless hospitalization cover deta hai eligible families ko.",
            }
        ],
    },
    "kidney_disease": {
        "keywords": ["kidney disease", "kidney failure", "gurda", "dialysis", "kidney kharab"],
        "schemes": [
            {
                "scheme_name": "PM National Dialysis Programme",
                "description": "Government hospitals mein free ya subsidized dialysis facility deta hai chronic kidney disease patients ke liye.",
            }
        ],
    },
}


def find_schemes(text: str):
    text_lower = text.lower()
    for condition_key, rule in SCHEME_RULES.items():
        if any(keyword in text_lower for keyword in rule["keywords"]):
            return condition_key, rule["schemes"]
    return None, []