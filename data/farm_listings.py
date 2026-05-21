FARM_LISTINGS = [
    {
        "id": "elgon_arabica",
        "name": "Elgon Highland Arabica Co-op",
        "region": "Mount Elgon",
        "coffee_type": "arabica",
        "yield_tonnes": 120,
        "min_investment": 500,
        "stake_available_pct": 40,
        "funded_pct": 60,
        "harvest_date": "October 2025",
        "payment_date": "January 2026",
        "risk_level": "Low",
        "risk_score": 68,
        "crop_health": 73.5,
        "drought_flag": False,
        "temp_celsius": 22.1,
        "description": (
            "A cooperative of 340 smallholder farmers in the Mount Elgon "
            "highlands growing high-altitude Arabica at 1,800 to 2,200m. "
            "The region's volcanic soils and consistent rainfall produce "
            "one of Uganda's finest specialty grades."
        ),
    },
    {
        "id": "victoria_robusta",
        "name": "Lake Victoria Robusta Farmers",
        "region": "Lake Victoria Basin",
        "coffee_type": "robusta",
        "yield_tonnes": 340,
        "min_investment": 250,
        "stake_available_pct": 55,
        "funded_pct": 28,
        "harvest_date": "January 2026",
        "payment_date": "April 2026",
        "risk_level": "Moderate",
        "risk_score": 52,
        "crop_health": 58.0,
        "drought_flag": False,
        "temp_celsius": 24.3,
        "description": (
            "A large producer cooperative along the northern Lake Victoria "
            "shore. Robusta grown at lower altitude for high-volume export "
            "to European instant coffee manufacturers. Strong export "
            "relationships with three major trading houses."
        ),
    },
    {
        "id": "rwenzori_arabica",
        "name": "Rwenzori Mountain Arabica Estate",
        "region": "Rwenzori Mountains",
        "coffee_type": "arabica",
        "yield_tonnes": 85,
        "min_investment": 1000,
        "stake_available_pct": 30,
        "funded_pct": 82,
        "harvest_date": "November 2025",
        "payment_date": "February 2026",
        "risk_level": "Low",
        "risk_score": 71,
        "crop_health": 81.0,
        "drought_flag": False,
        "temp_celsius": 21.4,
        "description": (
            "A single-estate Arabica farm in the Rwenzori foothills at "
            "2,100m. Award-winning cup quality with direct trade "
            "relationships with specialty roasters in the UK and Germany. "
            "82% funded — limited stakes remaining."
        ),
    },
    {
        "id": "mbale_robusta",
        "name": "Mbale District Robusta Union",
        "region": "Eastern Uganda",
        "coffee_type": "robusta",
        "yield_tonnes": 210,
        "min_investment": 250,
        "stake_available_pct": 70,
        "funded_pct": 15,
        "harvest_date": "February 2026",
        "payment_date": "May 2026",
        "risk_level": "Moderate",
        "risk_score": 49,
        "crop_health": 62.0,
        "drought_flag": True,
        "temp_celsius": 25.1,
        "description": (
            "A union of 180 farmers in the Mbale and Sironko districts "
            "producing screen 15 Robusta for commodity export. Note: a "
            "drought signal was active in this region during March 2026. "
            "Monitor crop health scores before committing capital."
        ),
    },
    {
        "id": "kasese_arabica",
        "name": "Kasese Highlands Arabica Project",
        "region": "Western Uganda",
        "coffee_type": "arabica",
        "yield_tonnes": 60,
        "min_investment": 500,
        "stake_available_pct": 50,
        "funded_pct": 44,
        "harvest_date": "December 2025",
        "payment_date": "March 2026",
        "risk_level": "Low",
        "risk_score": 64,
        "crop_health": 69.0,
        "drought_flag": False,
        "temp_celsius": 22.8,
        "description": (
            "A development-linked Arabica project in the Kasese highlands "
            "supported by a European agricultural development fund. "
            "Smaller yield but premium pricing secured through forward "
            "contracts with two specialty importers."
        ),
    },
    {
        "id": "gulu_robusta",
        "name": "Gulu Northern Robusta Co-op",
        "region": "Northern Uganda",
        "coffee_type": "robusta",
        "yield_tonnes": 175,
        "min_investment": 250,
        "stake_available_pct": 65,
        "funded_pct": 8,
        "harvest_date": "March 2026",
        "payment_date": "June 2026",
        "risk_level": "Moderate",
        "risk_score": 55,
        "crop_health": 55.0,
        "drought_flag": False,
        "temp_celsius": 26.2,
        "description": (
            "An emerging cooperative in the Gulu district expanding "
            "Robusta cultivation in northern Uganda's fertile plains. "
            "Early stage with strong government backing but limited "
            "export track record. Higher potential return, higher uncertainty."
        ),
    },
]


def get_farm_by_id(farm_id: str) -> dict | None:
    for farm in FARM_LISTINGS:
        if farm["id"] == farm_id:
            return farm
    return None


def get_farms_by_type(coffee_type: str) -> list:
    return [f for f in FARM_LISTINGS if f["coffee_type"] == coffee_type]


def get_farms_by_risk(risk_level: str) -> list:
    return [f for f in FARM_LISTINGS if f["risk_level"] == risk_level]