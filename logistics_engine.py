import json
import os
import datetime
import copy


# ==========================================
# FILE PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_FILE = os.path.join(
    BASE_DIR,
    "food_database.json"
)

STATE_FILE = os.path.join(
    BASE_DIR,
    "package_state.json"
)


# ==========================================
# LOAD PACKAGE STATE
# ==========================================

def load_package_state():
    """
    Loads the package state
    from package_state.json.
    """

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
# LOAD FOOD DATABASE
# ==========================================

def load_food_database():
    """
    Loads food packaging and transit
    specifications from food_database.json.
    """

    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(
            "food_database.json not found."
        )

    with open(
        DB_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# CALCULATE TRANSIT IMPACT
# ==========================================

def calculate_transit_impact(
    state,
    cat_data,
    origin,
    destination,
    transit_hrs,
    actual_temp
):
    """
    Calculates cold-chain impact and
    remaining shelf life.

    The calculation is performed on the
    temporary state passed to this function.
    The original JSON file is NOT modified.
    """

    # ------------------------------------------
    # TRANSIT TIME
    # ------------------------------------------

    transit_days = (
        transit_hrs / 24.0
    )


    # ------------------------------------------
    # TEMPERATURE DIFFERENCE
    # ------------------------------------------

    temp_diff = max(
        0.0,
        actual_temp
        -
        cat_data["target_storage_temp_c"]
    )


    # ------------------------------------------
    # TEMPERATURE ACCELERATION
    # ------------------------------------------

    acceleration_factor = (
        1.0
        +
        (temp_diff * 0.25)
    )


    # ------------------------------------------
    # EFFECTIVE SHELF-LIFE LOSS
    # ------------------------------------------

    effective_days_lost = (
        transit_days
        *
        acceleration_factor
    )


    # ------------------------------------------
    # UPDATE TEMPORARY SHELF LIFE
    # ------------------------------------------

    old_remaining_days = (
        state["remaining_shelf_life_days"]
    )

    new_remaining_days = max(
        0.0,
        round(
            old_remaining_days
            -
            effective_days_lost,
            1
        )
    )

    state[
        "remaining_shelf_life_days"
    ] = new_remaining_days


    # ------------------------------------------
    # COLD CHAIN STATUS
    # ------------------------------------------

    if temp_diff <= 2.0:

        cold_chain_status = (
            "EXCELLENT - Temp Maintained"
        )

    else:

        cold_chain_status = (
            "WARNING - Thermal Abuse Detected"
        )

    state[
        "cold_chain_status"
    ] = cold_chain_status


    # ------------------------------------------
    # TRANSIT SUMMARY
    # ------------------------------------------

    state["transit_summary"] = {

        "origin": origin,

        "destination": destination,

        "transit_hours": transit_hrs,

        "actual_avg_temp_c": actual_temp
    }


    # ------------------------------------------
    # LOGISTICS ANALYSIS
    # ------------------------------------------

    state["logistics_analysis"] = {

        "target_temperature_c":
            cat_data[
                "target_storage_temp_c"
            ],

        "temperature_difference_c":
            round(
                temp_diff,
                2
            ),

        "acceleration_factor":
            round(
                acceleration_factor,
                2
            ),

        "effective_days_lost":
            round(
                effective_days_lost,
                2
            ),

        "analysis_timestamp":
            datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }


    return state


# ==========================================
# MAIN FLASK-FRIENDLY FUNCTION
# ==========================================

def run_logistics(
    origin,
    destination,
    transit_hrs,
    actual_temp
):
    """
    Main function called by Flask.

    The package state is loaded from JSON,
    copied into temporary memory, and then
    calculated.

    package_state.json is NOT modified.
    """

    # ------------------------------------------
    # LOAD DATA
    # ------------------------------------------

    original_state = load_package_state()

    db = load_food_database()


    # ------------------------------------------
    # CREATE TEMPORARY STATE
    # ------------------------------------------

    state = copy.deepcopy(
        original_state
    )


    # ------------------------------------------
    # GET FOOD CATEGORY
    # ------------------------------------------

    category = state["category"]

    cat_data = db.get(
        category
    )


    if cat_data is None:

        raise ValueError(
            f"Food category '{category}' "
            "not found in food_database.json."
        )


    # ------------------------------------------
    # CALCULATE
    # ------------------------------------------

    state = calculate_transit_impact(

        state,

        cat_data,

        origin,

        destination,

        transit_hrs,

        actual_temp
    )


    # ------------------------------------------
    # RETURN RESULTS
    # ------------------------------------------

    return {

        "state": state,

        "category_data": cat_data,

        "product_name":
            state["product_name"],

        "category":
            state["category"],

        "origin":
            state[
                "transit_summary"
            ]["origin"],

        "destination":
            state[
                "transit_summary"
            ]["destination"],

        "transit_hours":
            state[
                "transit_summary"
            ]["transit_hours"],

        "actual_avg_temp":
            state[
                "transit_summary"
            ]["actual_avg_temp_c"],

        "target_temp":
            cat_data[
                "target_storage_temp_c"
            ],

        "initial_shelf_life":
            state[
                "initial_shelf_life_days"
            ],

        "remaining_shelf_life":
            state[
                "remaining_shelf_life_days"
            ],

        "cold_chain_status":
            state[
                "cold_chain_status"
            ],

        "outer_shipper":
            cat_data[
                "transit_specs"
            ]["outer_shipper"],

        "thermal_liner":
            cat_data[
                "transit_specs"
            ]["thermal_liner"],

        "refrigerant":
            cat_data[
                "transit_specs"
            ]["refrigerant"],

        "humidity_control":
            cat_data[
                "transit_specs"
            ]["humidity_control"],

        "max_allowable_temp":
            cat_data[
                "transit_specs"
            ]["max_allowable_temp"],

        "analysis":
            state.get(
                "logistics_analysis",
                {}
            )
    }


# ==========================================
# ORIGINAL COMMAND-LINE VERSION
# ==========================================

def main():

    print("\n" + "=" * 60)

    print(
        "         LOGISTICS & TRANSIT "
        "MONITORING ENGINE"
    )

    print("=" * 60)


    try:

        state = load_package_state()

        db = load_food_database()

    except Exception as e:

        print(f"\n[!] Error: {e}")

        return


    category = state["category"]

    cat_data = db.get(
        category
    )


    if cat_data is None:

        print(
            "\n[!] Food category not found "
            "in database."
        )

        return


    print(
        f"\n[+] Loaded Cargo: "
        f"{state['product_name']}"
    )

    print(
        f"[+] Category: "
        f"{state['category']}"
    )

    print(
        f"[+] Baseline Shelf Life: "
        f"{state['initial_shelf_life_days']} Days"
    )


    # ------------------------------------------
    # ORIGIN
    # ------------------------------------------

    origin = input(
        f"\nOrigin "
        f"[{state['mfg_location']}]: "
    ).strip()


    if not origin:

        origin = state[
            "mfg_location"
        ]


    # ------------------------------------------
    # DESTINATION
    # ------------------------------------------

    destination = input(
        "Destination "
        "[Default: Mumbai, India]: "
    ).strip()


    if not destination:

        destination = "Mumbai, India"


    # ------------------------------------------
    # TRANSIT HOURS
    # ------------------------------------------

    try:

        transit_hrs = float(
            input(
                "Transit Duration (Hours) "
                "[e.g., 18]: "
            )
        )

    except ValueError:

        transit_hrs = 18.0


    # ------------------------------------------
    # ACTUAL TEMPERATURE
    # ------------------------------------------

    try:

        actual_temp = float(
            input(
                "Actual Avg Transit Temp "
                f"(°C) "
                f"[Target: "
                f"{cat_data['target_storage_temp_c']}°C]: "
            )
        )

    except ValueError:

        actual_temp = (
            cat_data[
                "target_storage_temp_c"
            ]
            +
            2.0
        )


    # ------------------------------------------
    # RUN ENGINE
    # ------------------------------------------

    result = run_logistics(

        origin,

        destination,

        transit_hrs,

        actual_temp
    )


    # ------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------

    print(
        "\n" + "-" * 60
    )

    print(
        "             TRANSIT ANALYSIS"
    )

    print(
        "-" * 60
    )

    print(
        f" Route               : "
        f"{result['origin']} "
        f"➔ "
        f"{result['destination']}"
    )

    print(
        f" Transit Duration    : "
        f"{result['transit_hours']} Hours"
    )

    print(
        f" Target Temperature  : "
        f"{result['target_temp']}°C"
    )

    print(
        f" Actual Avg Temp     : "
        f"{result['actual_avg_temp']}°C"
    )

    print(
        f" Remaining Shelf Life: "
        f"{result['remaining_shelf_life']} Days"
    )

    print(
        f" Cold Chain Status   : "
        f"{result['cold_chain_status']}"
    )

    print(
        "-" * 60
    )


# ==========================================
# RUN STANDALONE VERSION
# ==========================================

if __name__ == "__main__":

    main()