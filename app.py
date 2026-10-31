from io import BytesIO
from urllib.parse import urlparse

import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


def normalize_url(raw: str) -> str:
    url = raw.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Enter a valid website link, like https://example.com")
    return url


def build_qr_png(url: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        try:
            if not url:
                raise ValueError("Paste a website link first.")
            url = normalize_url(url)
            return render_template("index.html", url=url, show_qr=True, error=None)
        except ValueError as exc:
            error = str(exc)

    return render_template("index.html", url=url, show_qr=False, error=error)


@app.route("/qr")
def qr_image():
    raw = request.args.get("url", "")
    try:
        url = normalize_url(raw)
    except ValueError:
        return "Invalid URL", 400
    return send_file(
        build_qr_png(url),
        mimetype="image/png",
        as_attachment=False,
        download_name="qr-code.png",
    )


@app.route("/download")
def download_qr():
    raw = request.args.get("url", "")
    try:
        url = normalize_url(raw)
    except ValueError:
        return "Invalid URL", 400
    return send_file(
        build_qr_png(url),
        mimetype="image/png",
        as_attachment=True,
        download_name="qr-code.png",
    )


if __name__ == "__main__":
    app.run(debug=True)
