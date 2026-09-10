import cv2
import numpy as np
import math
import datetime
import os


# ==========================================
# 1. SMART PACK INSPECTOR DATABASE
# ==========================================

INSPECTOR_DATABASE = {

    "Strawberries": {

        "ref_shelf_life_days": 7,

        "ref_temp_c": 4,

        "activation_energy_j_mol": 65000,

        "fresh_hue_max": 140,

        "spoiled_hue_min": 20
    },


    "Fresh Milk": {

        "ref_shelf_life_days": 10,

        "ref_temp_c": 4,

        "activation_energy_j_mol": 75000,

        "fresh_hue_max": 130,

        "spoiled_hue_min": 30
    },


    "Raw Poultry/Chicken": {

        "ref_shelf_life_days": 4,

        "ref_temp_c": 4,

        "activation_energy_j_mol": 82000,

        "fresh_hue_max": 140,

        "spoiled_hue_min": 15
    }

}


def load_food_data(food_name):
    """
    Loads food parameters used by the Smart Pack Inspector.
    """

    return INSPECTOR_DATABASE.get(food_name)


# ==========================================
# 2. IMAGE PROCESSING
# ==========================================

def extract_indicator_hue(image_path):
    """
    Loads the indicator image, converts it to HSV,
    removes dark/low-saturation background pixels,
    and calculates the average Hue.

    OpenCV Hue range = 0 to 180.
    """

    # Check whether file exists

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found at path: {image_path}"
        )


    # Read image

    img = cv2.imread(image_path)


    if img is None:

        raise ValueError(
            "Could not decode image file."
        )


    # Convert BGR image to HSV

    hsv_img = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2HSV
    )


    # Extract channels

    hue_channel = hsv_img[:, :, 0]

    saturation_channel = hsv_img[:, :, 1]


    # Remove dark / low-saturation pixels

    valid_mask = saturation_channel > 40


    # Calculate average Hue

    if np.sum(valid_mask) == 0:

        avg_hue = np.mean(hue_channel)

    else:

        avg_hue = np.mean(
            hue_channel[valid_mask]
        )


    return round(
        float(avg_hue),
        2
    )


# ==========================================
# 3. QUALITY & SHELF-LIFE CALCULATION
# ==========================================

def calculate_quality(
    food_item,
    food_params,
    avg_hue,
    storage_temp_c
):
    """
    Calculates freshness percentage
    and estimated remaining shelf life.

    Uses:
    - Indicator Hue
    - Arrhenius temperature acceleration
    - Reference shelf life
    """


    # ------------------------------------------
    # HUE PARAMETERS
    # ------------------------------------------

    fresh_h = food_params["fresh_hue_max"]

    spoiled_h = food_params["spoiled_hue_min"]


    # ------------------------------------------
    # FRESHNESS CALCULATION
    # ------------------------------------------

    raw_freshness = (
        (avg_hue - spoiled_h)
        /
        (fresh_h - spoiled_h)
    ) * 100


    freshness_pct = np.clip(
        raw_freshness,
        0.0,
        100.0
    )


    # ------------------------------------------
    # ARRHENIUS CALCULATION
    # ------------------------------------------

    R = 8.314

    Ea = food_params[
        "activation_energy_j_mol"
    ]


    # Reference temperature

    T_ref = (
        food_params["ref_temp_c"]
        + 273.15
    )


    # Actual temperature

    T_actual = (
        storage_temp_c
        + 273.15
    )


    # Arrhenius equation

    ln_k_ratio = (
        Ea / R
    ) * (
        (1 / T_ref)
        -
        (1 / T_actual)
    )


    acceleration_factor = math.exp(
        ln_k_ratio
    )


    # ------------------------------------------
    # REMAINING SHELF LIFE
    # ------------------------------------------

    base_remaining_days = (
        food_params["ref_shelf_life_days"]
        *
        (freshness_pct / 100.0)
    )


    adjusted_days_left = (
        base_remaining_days
        /
        acceleration_factor
    )


    # ------------------------------------------
    # STATUS
    # ------------------------------------------

    if freshness_pct >= 65:

        status = "SAFE TO EAT"

    elif freshness_pct >= 30:

        status = "CONSUME SOON"

    else:

        status = "SPOILED / DO NOT EAT"


    # ------------------------------------------
    # FINAL RESULT
    # ------------------------------------------

    return {

        "Food": food_item,

        "Freshness_Pct": round(
            float(freshness_pct),
            1
        ),

        "Avg_Hue": avg_hue,

        "Storage_Temp_C": storage_temp_c,

        "Days_Remaining": max(
            0.0,
            round(
                adjusted_days_left,
                1
            )
        ),

        "Status": status
    }


# ==========================================
# 4. OPTIONAL HTML REPORT GENERATOR
# ==========================================

def generate_dashboard(
    results,
    output_filename="food_inspection_report.html"
):
    """
    Generates a standalone HTML inspection report.

    Flask does not need this function,
    but it is kept because your original
    Smart Pack Inspector used it.
    """

    status = results["Status"]

    freshness = results["Freshness_Pct"]

    days_left = results["Days_Remaining"]


    # ------------------------------------------
    # STATUS COLORS
    # ------------------------------------------

    if status == "SAFE TO EAT":

        theme_color = "#10B981"

        badge_bg = "#D1FAE5"

        badge_text = "#065F46"


    elif status == "CONSUME SOON":

        theme_color = "#F59E0B"

        badge_bg = "#FEF3C7"

        badge_text = "#92400E"


    else:

        theme_color = "#EF4444"

        badge_bg = "#FEE2E2"

        badge_text = "#991B1B"


    # ------------------------------------------
    # HTML
    # ------------------------------------------

    html_code = f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>
        Smart Packaging Inspection Report
    </title>

</head>


<body>

    <h1>
        Smart Packaging Inspection Report
    </h1>


    <h2>
        {results['Food']}
    </h2>


    <p>
        Status:
        <strong>
            {status}
        </strong>
    </p>


    <p>
        Freshness:
        <strong>
            {freshness}%
        </strong>
    </p>


    <p>
        Estimated Days Remaining:
        <strong>
            {days_left} days
        </strong>
    </p>


    <p>
        Color Hue:
        {results['Avg_Hue']}°
    </p>


    <p>
        Storage Temperature:
        {results['Storage_Temp_C']}°C
    </p>


</body>

</html>
"""


    # ------------------------------------------
    # SAVE REPORT
    # ------------------------------------------

    with open(
        output_filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html_code)


    return os.path.abspath(
        output_filename
    )


# ==========================================
# 5. STANDALONE TEST MODE
# ==========================================

def main():

    print("=" * 60)

    print(
        "SMART FOOD PACKAGING QUALITY & "
        "SHELF-LIFE ANALYZER"
    )

    print("=" * 60)


    # ------------------------------------------
    # AVAILABLE FOODS
    # ------------------------------------------

    food_items = list(
        INSPECTOR_DATABASE.keys()
    )


    print(
        "\nAvailable Food Items:"
    )


    for index, item in enumerate(
        food_items,
        1
    ):

        print(
            f" [{index}] {item}"
        )


    # ------------------------------------------
    # SELECT FOOD
    # ------------------------------------------

    try:

        choice = int(
            input(
                "\nSelect Food Item Number: "
            )
        ) - 1


        selected_food = food_items[
            choice
        ]


    except (
        ValueError,
        IndexError
    ):

        print(
            "Invalid selection. "
            "Defaulting to Strawberries."
        )

        selected_food = "Strawberries"


    food_params = load_food_data(
        selected_food
    )


    # ------------------------------------------
    # IMAGE PATH
    # ------------------------------------------

    image_path = input(
        "\nEnter path to packaging "
        "indicator photo: "
    ).strip()


    # ------------------------------------------
    # CHECK IMAGE
    # ------------------------------------------

    if not os.path.exists(image_path):

        print(
            "\n[!] Image path not found."
        )

        print(
            "Please provide a valid image."
        )

        return


    # ------------------------------------------
    # TEMPERATURE
    # ------------------------------------------

    try:

        storage_temp = float(
            input(
                "Enter current storage/ambient "
                "temperature in °C: "
            )
        )


    except ValueError:

        print(
            "Invalid temperature. "
            "Defaulting to 22°C."
        )

        storage_temp = 22.0


    # ------------------------------------------
    # ANALYSIS
    # ------------------------------------------

    print(
        "\nRunning colorimetric and "
        "kinetic decay calculations..."
    )


    avg_hue = extract_indicator_hue(
        image_path
    )


    analysis_results = calculate_quality(
        selected_food,
        food_params,
        avg_hue,
        storage_temp
    )


    # ------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------

    print(
        "\n" + "=" * 40
    )

    print(
        "INSPECTION RESULTS"
    )

    print(
        "=" * 40
    )


    print(
        f" Item Analyzed     : "
        f"{analysis_results['Food']}"
    )


    print(
        f" Freshness Score   : "
        f"{analysis_results['Freshness_Pct']}%"
    )


    print(
        f" Color Hue (HSV)   : "
        f"{analysis_results['Avg_Hue']}°"
    )


    print(
        f" Storage Temp      : "
        f"{analysis_results['Storage_Temp_C']}°C"
    )


    print(
        f" Est. Days Left    : "
        f"{analysis_results['Days_Remaining']} Days"
    )


    print(
        f" Status            : "
        f"{analysis_results['Status']}"
    )


    print(
        "=" * 40
    )


# ==========================================
# RUN STANDALONE VERSION
# ==========================================

if __name__ == "__main__":

    main()