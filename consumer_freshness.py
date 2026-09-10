import json
import os
from datetime import datetime


# ==========================================
# FILE PATH
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATE_FILE = os.path.join(
    BASE_DIR,
    "package_state.json"
)


# ==========================================
# LOAD PACKAGE STATE
# ==========================================

def load_package_state():

    if not os.path.exists(STATE_FILE):

        raise FileNotFoundError(
            "package_state.json not found."
        )

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# CALCULATE FRESHNESS
# ==========================================

def calculate_freshness(state):

    remaining_days = float(
        state["remaining_shelf_life_days"]
    )

    cold_chain_status = state.get(
        "cold_chain_status",
        "UNKNOWN"
    )


    # --------------------------------------
    # FRESHNESS DECISION
    # --------------------------------------

    if remaining_days <= 0:

        freshness_status = (
            "NOT RECOMMENDED"
        )

        recommendation = (
            "The estimated shelf life has expired."
        )

    elif remaining_days <= 1:

        freshness_status = (
            "USE SOON"
        )

        recommendation = (
            "Consume soon and follow the storage instructions."
        )

    else:

        freshness_status = (
            "FRESH"
        )

        recommendation = (
            "The package has remaining estimated shelf life."
        )


    # --------------------------------------
    # COLD CHAIN WARNING
    # --------------------------------------

    if "WARNING" in cold_chain_status.upper():

        freshness_note = (
            "Cold-chain warning detected. "
            "Check storage conditions before consumption."
        )

    else:

        freshness_note = (
            "No cold-chain warning is recorded."
        )


    return {

        "product_name":
            state["product_name"],

        "category":
            state["category"],

        "mfg_date":
            state["mfg_date"],

        "initial_shelf_life":
            state["initial_shelf_life_days"],

        "remaining_shelf_life":
            remaining_days,

        "cold_chain_status":
            cold_chain_status,

        "freshness_status":
            freshness_status,

        "recommendation":
            recommendation,

        "freshness_note":
            freshness_note
    }


# ==========================================
# MAIN FUNCTION FOR FLASK
# ==========================================

def run_freshness_check():

    state = load_package_state()

    return calculate_freshness(
        state
    )


# ==========================================
# STANDALONE TEST
# ==========================================

if __name__ == "__main__":

    try:

        result = run_freshness_check()

        print("\n" + "=" * 50)

        print(
            "       CONSUMER FRESHNESS CHECK"
        )

        print("=" * 50)

        print(
            f"\nProduct: "
            f"{result['product_name']}"
        )

        print(
            f"Category: "
            f"{result['category']}"
        )

        print(
            f"Manufacturing Date: "
            f"{result['mfg_date']}"
        )

        print(
            f"Initial Shelf Life: "
            f"{result['initial_shelf_life']} days"
        )

        print(
            f"Remaining Shelf Life: "
            f"{result['remaining_shelf_life']} days"
        )

        print(
            f"Cold Chain: "
            f"{result['cold_chain_status']}"
        )

        print(
            f"\nFreshness Status: "
            f"{result['freshness_status']}"
        )

        print(
            f"Recommendation: "
            f"{result['recommendation']}"
        )

        print(
            f"Note: "
            f"{result['freshness_note']}"
        )

        print("\n" + "=" * 50)

    except Exception as e:

        print(
            f"\n[!] Error: {e}"
        )