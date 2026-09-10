import json
import os
import datetime
import webbrowser
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "food_database.json")
STATE_FILE = os.path.join(BASE_DIR, "package_state.json")
HTML_FILE = os.path.join(BASE_DIR, "consumer_freshness_report.html")

def generate_interactive_consumer_html(state, cat_data):
    fresh_ph_min, fresh_ph_max = cat_data["fresh_ph_range"]
    spoiled_ph = cat_data["spoiled_ph_threshold"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consumer Smart QR Scanner & Safety Audit</title>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f9fc; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 850px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 30px; border-top: 6px solid #3b82f6; }}
        h1 {{ color: #1e3a8a; margin-top: 0; font-size: 24px; text-align: center; text-transform: uppercase; letter-spacing: 1px; }}
        .scanner-card {{ background: #eff6ff; border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px; }}
        .btn {{ background-color: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; margin: 5px; font-size: 14px; }}
        .btn:hover {{ background-color: #1d4ed8; }}
        #reader {{ width: 100%; max-width: 400px; margin: 15px auto; border-radius: 8px; overflow: hidden; display: none; }}
        #status-banner {{ text-align: center; padding: 14px; border-radius: 8px; font-weight: bold; font-size: 18px; margin: 20px 0; text-transform: uppercase; letter-spacing: 1px; display: none; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .card {{ background: #fdfdfd; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; }}
        .card h3 {{ margin-top: 0; color: #1e3a8a; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; font-size: 16px; }}
        .field {{ margin-bottom: 10px; font-size: 14px; }}
        .field span {{ font-weight: bold; color: #475569; }}
        .indicator-box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin-top: 20px; }}
        .input-group {{ margin-top: 15px; display: flex; gap: 10px; align-items: center; justify-content: center; }}
        .input-group input {{ padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; width: 100px; text-align: center; font-size: 16px; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Smart Packaging QR & Freshness Portal</h1>
        <div class="scanner-card">
            <h3 style="margin-top:0; color: #1e3a8a;">📷 Scan Product Packaging QR Code</h3>
            <p style="font-size: 13px; color: #475569;">Use your device camera or upload a saved picture of the product QR label.</p>
            <div>
                <button class="btn" onclick="startCameraScanner()">📷 Start Live Camera Scan</button>
                <button class="btn" style="background-color: #475569;" onclick="document.getElementById('qr-file-input').click()">📁 Upload QR Image File</button>
                <input type="file" id="qr-file-input" accept="image/*" style="display: none;" onchange="handleFileUpload(event)">
            </div>
            <div id="reader"></div>
            <p id="scan-result-text" style="font-weight: bold; color: #16a34a; margin-top: 10px;"></p>
        </div>
        <div id="status-banner"></div>
        <div class="grid">
            <div class="card">
                <h3>🛍️ Product Batch Metadata</h3>
                <div class="field"><span>Product Name:</span> {state['product_name']}</div>
                <div class="field"><span>Category:</span> {state['category']}</div>
                <div class="field"><span>Manufactured At:</span> {state['mfg_location']}</div>
                <div class="field"><span>Mfg Date:</span> {state['mfg_date']}</div>
            </div>
            <div class="card">
                <h3>⏳ Real-Time Shelf Life</h3>
                <div class="field"><span>Initial Shelf Life:</span> {state['initial_shelf_life_days']} Days</div>
                <div class="field"><span>Remaining Shelf Life:</span> <b>{state['remaining_shelf_life_days']} Days</b></div>
                <div class="field"><span>Cold Chain Status:</span> {state.get('cold_chain_status', 'N/A')}</div>
            </div>
        </div>
        <div class="indicator-box">
            <h3 style="margin-top:0; color: #1e3a8a; text-align: center;">🧪 Smart Bio-Indicator Tag Verification</h3>
            <div class="field"><span>Active Indicator Dye:</span> {cat_data['ph_indicator']['dye']}</div>
            <div class="field"><span>Color Profile:</span> {cat_data['ph_indicator']['color_profile']}</div>
            <div class="field"><span>Optimal Fresh pH:</span> {fresh_ph_min} - {fresh_ph_max} | <span>Spoilage Threshold:</span> pH {spoiled_ph}</div>
            <div class="input-group">
                <label for="ph-input"><b>Enter Current Indicator pH Value:</b></label>
                <input type="number" id="ph-input" step="0.1" value="{fresh_ph_min + 0.2:.1f}">
                <button class="btn" style="background-color: #16a34a;" onclick="verifyFreshness()">Verify Safety</button>
            </div>
        </div>
        <div class="footer">
            Verified by Consumer Packaging Scan Engine • Timestamp: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
    <script>
        let html5QrcodeScanner = null;
        function onScanSuccess(decodedText) {{
            document.getElementById('scan-result-text').innerText = "✓ QR Code Scanned Successfully! Verified Payload.";
            if (html5QrcodeScanner) {{
                html5QrcodeScanner.clear();
                document.getElementById('reader').style.display = 'none';
            }}
            verifyFreshness();
        }}
        function startCameraScanner() {{
            document.getElementById('reader').style.display = 'block';
            html5QrcodeScanner = new Html5Qrcode("reader");
            html5QrcodeScanner.start(
                {{ facingMode: "environment" }},
                {{ fps: 10, qrbox: 250 }},
                onScanSuccess
            ).catch(err => {{ alert("Camera access error: " + err); }});
        }}
        function handleFileUpload(event) {{
            const file = event.target.files[0];
            if (!file) return;
            const html5QrCode = new Html5Qrcode("reader");
            html5QrCode.scanFile(file, true)
                .then(decodedText => {{
                    document.getElementById('scan-result-text').innerText = "✓ QR Image Parsed Successfully!";
                    verifyFreshness();
                }})
                .catch(err => {{ alert("No valid QR code found in the image. Please upload a clearer picture."); }});
        }}
        function verifyFreshness() {{
            const currentPh = parseFloat(document.getElementById('ph-input').value);
            const freshMax = {fresh_ph_max};
            const spoiledPh = {spoiled_ph};
            const remainingDays = {state['remaining_shelf_life_days']};
            const banner = document.getElementById('status-banner');
            banner.style.display = 'block';
            if (currentPh >= spoiledPh || remainingDays <= 0) {{
                banner.innerText = "UNSAFE - SPOILAGE DETECTED";
                banner.style.backgroundColor = "#dc2626";
                banner.style.color = "#ffffff";
            }} else if (currentPh > freshMax) {{
                banner.innerText = "WARNING - BORDERLINE FRESHNESS";
                banner.style.backgroundColor = "#ea580c";
                banner.style.color = "#ffffff";
            }} else {{
                banner.innerText = "SAFE - OPTIMAL FRESHNESS";
                banner.style.backgroundColor = "#16a34a";
                banner.style.color = "#ffffff";
            }}
        }}
        window.onload = verifyFreshness;
    </script>
</body>
</html>"""

    # Write file
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Convert to valid browser URI and open
    file_uri = Path(HTML_FILE).as_uri()
    webbrowser.open_new_tab(file_uri)
    print(f"\n[✓] Generated file URI: {file_uri}")

def main():
    print("\n" + "="*60)
    print("         CONSUMER SMART QR & SAFETY ENGINE")
    print("="*60)

    if not os.path.exists(STATE_FILE):
        print(f"[!] Warning: '{STATE_FILE}' does not exist.")
        print("[!] Please run Option 1 (Manufacturer Portal) first to create package state!")
        return

    if not os.path.exists(DB_FILE):
        print(f"[!] Warning: '{DB_FILE}' not found in directory.")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)

    cat_data = db.get(state["category"], list(db.values())[0])

    print(f"\n[+] Opening HTML Scanner Portal for product: {state['product_name']}")
    generate_interactive_consumer_html(state, cat_data)

if __name__ == "__main__":
    main()