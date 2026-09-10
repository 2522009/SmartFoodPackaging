import qrcode
from io import BytesIO
from flask import send_file


def generate_qr(url):
    """
    Generate a QR code for the given URL
    and return it as a PNG image.
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)

    qr_image = qr.make_image()

    img_bytes = BytesIO()
    qr_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return send_file(
        img_bytes,
        mimetype="image/png"
    )