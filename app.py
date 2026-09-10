from flask import Flask, render_template, request
import json
import os
from werkzeug.utils import secure_filename

from qr_system import generate_qr

from smart_pack_inspector import (
    extract_indicator_hue,
    load_food_data,
    calculate_quality
)

from logistics_engine import run_logistics

# FIXED FUNCTION NAME
from consumer_freshness import run_freshness_check

from ai_chatbot import (
    get_chatbot_response,
    QUICK_PROMPTS
)


# =========================================================
# FLASK APP CONFIGURATION
# =========================================================

app = Flask(__name__)

# Maximum uploaded file size = 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Allowed image formats
ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_FILE = os.path.join(
    BASE_DIR,
    "food_database.json"
)

MFG_DB_FILE = os.path.join(
    BASE_DIR,
    "mfg_packaging_db.json"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# TEST FOOD DATABASE
# =========================================================

@app.route("/test-data")
def test_data():

    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            food_data = json.load(f)

        return render_template(
            "test_data.html",
            food_data=food_data
        )

    except Exception as e:

        return render_template(
            "test_data.html",
            food_data={},
            error=str(e)
        )


# =========================================================
# FOOD PACKAGING RECOMMENDATION
# =========================================================

@app.route(
    "/food-data",
    methods=["GET"]
)
def food_data():

    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            food_database = json.load(f)

        selected_food = request.args.get(
            "food"
        )

        selected_data = None

        if selected_food:

            selected_data = food_database.get(
                selected_food
            )

        return render_template(
            "food_data.html",
            food_data=food_database,
            selected_food=selected_food,
            selected_data=selected_data
        )

    except Exception as e:

        return render_template(
            "food_data.html",
            food_data={},
            selected_food=None,
            selected_data=None,
            error=str(e)
        )


# =========================================================
# MANUFACTURER PACKAGING
# =========================================================

@app.route(
    "/manufacturer",
    methods=["GET"]
)
def manufacturer():

    try:

        with open(
            MFG_DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            manufacturer_database = json.load(f)

        selected_food = request.args.get(
            "food"
        )

        selected_data = None

        if selected_food:

            selected_data = manufacturer_database.get(
                selected_food
            )

        return render_template(
            "manufacturer.html",
            manufacturer_data=manufacturer_database,
            selected_food=selected_food,
            selected_data=selected_data
        )

    except Exception as e:

        return render_template(
            "manufacturer.html",
            manufacturer_data={},
            selected_food=None,
            selected_data=None,
            error=str(e)
        )


# =========================================================
# SMART PACK INSPECTOR
# =========================================================

@app.route(
    "/inspection",
    methods=["GET", "POST"]
)
def inspection():

    result = None
    error = None

    if request.method == "POST":

        image_path = None

        try:

            # -----------------------------
            # Food selection
            # -----------------------------

            food_item = request.form.get(
                "food_item"
            )

            if not food_item:

                raise ValueError(
                    "Please select a food item."
                )


            # -----------------------------
            # Temperature
            # -----------------------------

            storage_temp = request.form.get(
                "storage_temp"
            )

            if not storage_temp:

                raise ValueError(
                    "Please enter the storage temperature."
                )

            storage_temp = float(
                storage_temp
            )

            if (
                storage_temp < -50
                or
                storage_temp > 80
            ):

                raise ValueError(
                    "Please enter a realistic temperature."
                )


            # -----------------------------
            # Image
            # -----------------------------

            if "image" not in request.files:

                raise ValueError(
                    "Please upload an image."
                )

            image = request.files["image"]

            if image.filename == "":

                raise ValueError(
                    "Please select an image."
                )


            # -----------------------------
            # Check image extension
            # -----------------------------

            if not allowed_file(
                image.filename
            ):

                raise ValueError(
                    "Invalid image format. "
                    "Please upload JPG, JPEG or PNG."
                )


            # -----------------------------
            # Secure filename
            # -----------------------------

            filename = secure_filename(
                image.filename
            )

            image_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )


            # -----------------------------
            # Save image temporarily
            # -----------------------------

            image.save(
                image_path
            )


            try:

                # -----------------------------
                # Image analysis
                # -----------------------------

                avg_hue = extract_indicator_hue(
                    image_path
                )

                if avg_hue is None:

                    raise ValueError(
                        "Could not detect a valid "
                        "indicator color from the "
                        "uploaded image."
                    )


                # -----------------------------
                # Load food parameters
                # -----------------------------

                food_params = load_food_data(
                    food_item
                )

                if food_params is None:

                    raise ValueError(
                        "This food is not available "
                        "in the inspection database."
                    )


                # -----------------------------
                # Calculate quality
                # -----------------------------

                result = calculate_quality(
                    food_item,
                    food_params,
                    avg_hue,
                    storage_temp
                )


            finally:

                # -----------------------------
                # Delete temporary image
                # -----------------------------

                if (
                    image_path
                    and
                    os.path.exists(image_path)
                ):

                    os.remove(
                        image_path
                    )


        except Exception as e:

            error = str(e)


            # Extra cleanup
            if (
                image_path
                and
                os.path.exists(image_path)
            ):

                try:

                    os.remove(
                        image_path
                    )

                except Exception:

                    pass


    return render_template(
        "inspection.html",
        result=result,
        error=error
    )


# =========================================================
# SMART LOGISTICS
# =========================================================

@app.route(
    "/logistics",
    methods=["GET", "POST"]
)
def logistics():

    result = None
    error = None

    if request.method == "POST":

        try:

            # -----------------------------
            # Origin
            # -----------------------------

            origin = request.form.get(
                "origin",
                ""
            ).strip()

            if not origin:

                raise ValueError(
                    "Please enter the origin."
                )


            # -----------------------------
            # Destination
            # -----------------------------

            destination = request.form.get(
                "destination",
                ""
            ).strip()

            if not destination:

                raise ValueError(
                    "Please enter the destination."
                )


            # -----------------------------
            # Transit duration
            # -----------------------------

            transit_hours = request.form.get(
                "transit_hours",
                ""
            ).strip()

            if not transit_hours:

                raise ValueError(
                    "Please enter the transit duration."
                )

            transit_hours = float(
                transit_hours
            )

            if transit_hours <= 0:

                raise ValueError(
                    "Transit duration must be greater than 0."
                )

            if transit_hours > 720:

                raise ValueError(
                    "Transit duration is too large."
                )


            # -----------------------------
            # Actual temperature
            # -----------------------------

            actual_temp = request.form.get(
                "actual_temp",
                ""
            ).strip()

            if not actual_temp:

                raise ValueError(
                    "Please enter the actual average temperature."
                )

            actual_temp = float(
                actual_temp
            )

            if (
                actual_temp < -50
                or
                actual_temp > 80
            ):

                raise ValueError(
                    "Please enter a realistic temperature."
                )


            # -----------------------------
            # Run logistics engine
            # -----------------------------

            result = run_logistics(
                origin,
                destination,
                transit_hours,
                actual_temp
            )


        except Exception as e:

            error = str(e)


    return render_template(
        "logistics.html",
        result=result,
        error=error
    )


# =========================================================
# CONSUMER FRESHNESS
# =========================================================

@app.route(
    "/consumer",
    methods=["GET", "POST"]
)
def consumer():

    result = None
    error = None

    if request.method == "POST":

        try:

            # FIXED FUNCTION NAME
            result = run_freshness_check()

        except Exception as e:

            error = str(e)


    return render_template(
        "consumer.html",
        result=result,
        error=error
    )


# =========================================================
# AI CHATBOT
# =========================================================

@app.route(
    "/chatbot",
    methods=["GET", "POST"]
)
def chatbot():

    response = None
    error = None
    user_message = ""

    if request.method == "POST":

        try:

            user_message = request.form.get(
                "message",
                ""
            ).strip()

            if not user_message:

                raise ValueError(
                    "Please enter a question."
                )

            response = get_chatbot_response(
                user_message
            )


        except Exception as e:

            error = str(e)


    return render_template(
        "chatbot.html",
        response=response,
        error=error,
        user_message=user_message,
        quick_prompts=QUICK_PROMPTS
    )


# =========================================================
# QR PRODUCT INFORMATION PAGE
# =========================================================

@app.route("/qr")
def qr_product():

    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            food_database = json.load(f)

        selected_food = request.args.get(
            "product"
        )

        selected_data = None

        if selected_food:

            selected_data = food_database.get(
                selected_food
            )

        return render_template(
            "qr_product.html",
            selected_food=selected_food,
            selected_data=selected_data
        )

    except Exception as e:

        return render_template(
            "qr_product.html",
            selected_food=None,
            selected_data=None,
            error=str(e)
        )


# =========================================================
# QR CODE GENERATION
# =========================================================

@app.route("/generate-qr")
def generate_qr_code():

    url = request.args.get(
        "url"
    )

    if not url:

        return "QR URL is missing", 400

    return generate_qr(
        url
    )


# =========================================================
# RUN FLASK APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run()
