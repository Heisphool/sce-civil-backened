import requests
from bs4 import BeautifulSoup
import pdfkit
import os
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

# --- Python Script ka original logic yahan hai ---

# wkhtmltopdf ka configuration
# Render par yeh build.sh se install ho jayega, isliye config ki zaroorat nahi
config = None

# Semester URLs
SEMESTER_URLS = {
    1: "https://results.beup.ac.in/BTech1stSem2023_B2023Results.aspx",
    2: "https://results.beup.ac.in/BTech2ndSem2024_B2023Results.aspx",
    3: "https://results.beup.ac.in/BTech3rdSem2025_B2023Results.aspx"
}

def get_result_pdf_in_memory(reg_no: str, semester: int):
    """
    Result fetch karke PDF banata hai aur use file ki tarah save karne ke bajaye memory me rakhta hai.
    """
    if semester not in SEMESTER_URLS:
        raise ValueError(f"Galat semester number '{semester}'.")

    url = SEMESTER_URLS[semester]
    
    session = requests.Session()
    resp = session.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    viewstate = soup.find("input", {"id": "__VIEWSTATE"})
    viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})

    if not all([viewstate, viewstategenerator, eventvalidation]):
        raise RuntimeError("Page se zaroori form data nahi mila.")

    payload = {
        "__EVENTTARGET": "", "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator["value"],
        "__EVENTVALIDATION": eventvalidation["value"],
        "ctl00$ContentPlaceHolder1$TextBox_RegNo": reg_no,
        "ctl00$ContentPlaceHolder1$Button_Show": "Show Result"
    }

    result_page = session.post(url, data=payload, timeout=20)
    result_page.raise_for_status()

    if "Registration No. not found" in result_page.text or "Invalid Roll No." in result_page.text:
        raise ValueError(f"Registration number '{reg_no}' nahi mila.")

    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    soup_result = BeautifulSoup(result_page.text, 'html.parser')
    if soup_result.head:
        base_tag = soup_result.new_tag('base', href=f'{base_url}/')
        soup_result.head.insert(0, base_tag)
    
    modified_html_string = str(soup_result)
    
    pdfkit_options = {"enable-local-file-access": None}
    pdf_bytes = pdfkit.from_string(modified_html_string, False, configuration=config, options=pdfkit_options)
    
    return pdf_bytes

# --- Flask Server ka Code ---
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend server for SCE Civil Hub is running."

@app.route('/download-result', methods=['POST'])
def download_result():
    data = request.get_json()
    reg_no = data.get('reg_no')
    semester = data.get('semester')

    if not reg_no or not semester:
        return jsonify({"error": "Registration number aur semester zaroori hai."}), 400

    print(f"Request aayi: Reg No: {reg_no}, Semester: {semester}")

    try:
        pdf_data = get_result_pdf_in_memory(reg_no, int(semester))
        
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'BEUP_Result_Sem{semester}_{reg_no}.pdf'
        )

    except Exception as e:
        print(f"Error aayi: {e}")
        return jsonify({"error": str(e)}), 500

# Server chalane ke liye __main__ block ki zaroorat nahi, Render gunicorn ka use karega.

