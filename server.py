import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from weasyprint import HTML

app = Flask(__name__)
CORS(app)

# Semester ke URLs
SEMESTER_URLS = {
    "1": "https://results.beup.ac.in/BTech1stSem2023_B2023Results.aspx",
    "2": "https://results.beup.ac.in/BTech2ndSem2024_B2023Results.aspx",
    "3": "https://results.beup.ac.in/BTech3rdSem2025_B2023Results.aspx"
}


def fetch_result_and_save_pdf(reg_no: str, semester: str):
    """
    BEUP result fetch karta hai aur WeasyPrint ke saath PDF banata hai.
    """
    if semester not in SEMESTER_URLS:
        raise ValueError("Galat semester number. Sirf 1, 2, ya 3 valid hai.")

    url = SEMESTER_URLS[semester]
    base_url = "https://results.beup.ac.in/"

    session = requests.Session()

    print(f"STEP 1: {url} se page fetch kar raha hai...")
    resp = session.get(url, timeout=45)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    print("STEP 1: Page fetch ho gaya ✅")

    # Form fields dhoondhna
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})
    viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})

    if not all([viewstate, viewstategenerator, eventvalidation]):
        print("ERROR: Zaroori form fields nahi mile ❌")
        raise RuntimeError("Result page ka structure badal gaya hai.")

    # Form submit karne ka payload
    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator["value"],
        "__EVENTVALIDATION": eventvalidation["value"],
        "ctl00$ContentPlaceHolder1$TextBox_RegNo": reg_no,
        "ctl00$ContentPlaceHolder1$Button_Show": "Show Result"
    }

    print(f"STEP 2: Roll No. {reg_no} ke liye form submit kar raha hai...")
    result_page = session.post(url, data=payload, timeout=45)
    result_page.raise_for_status()
    result_html_string = result_page.text
    print("STEP 2: Result page aa gaya ✅")

    print("STEP 3: WeasyPrint se PDF bana raha hai...")
    # Naye version ka syntax: HTML(string).write_pdf(BytesIO)
    pdf_io = BytesIO()
    HTML(string=result_html_string, base_url=base_url).write_pdf(pdf_io)
    pdf_io.seek(0)
    print("STEP 3: PDF ready ho gayi ✅")

    return pdf_io


@app.route('/download-result', methods=['POST'])
def download_result():
    data = request.get_json()
    reg_no = data.get('reg_no')
    semester = data.get('semester')

    if not reg_no or not semester:
        return jsonify({"error": "Registration number aur semester zaroori hai."}), 400

    try:
        pdf_file = fetch_result_and_save_pdf(reg_no, str(semester))
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'BEUP_Result_Sem{semester}_{reg_no}.pdf'
        )
    except Exception as e:
        print(f"SERVER ERROR: {e}")
        return jsonify({"error": f"Result download nahi ho paya. Error: {str(e)}"}), 500


@app.route('/')
def home():
    return "⚡ Result PDF Downloader server (v3 - Debug mode, WeasyPrint 60.2) chal raha hai."


if __name__ == '__main__':
    app.run(debug=True)
