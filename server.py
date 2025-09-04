import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from weasyprint import HTML

app = Flask(__name__)
CORS(app)

SEMESTER_URLS = {
    "1": "https://results.beup.ac.in/BTech1stSem2023_B2023Results.aspx",
    "2": "https://results.beup.ac.in/BTech2ndSem2024_B2023Results.aspx",
    "3": "https://results.beup.ac.in/BTech3rdSem2025_B2023Results.aspx"
}

def fetch_result_and_save_pdf(reg_no: str, semester: str):
    """
    Result fetch karta hai aur WeasyPrint ka istemal karke PDF banata hai.
    Timeout badha diya gaya hai.
    """
    if semester not in SEMESTER_URLS:
        raise ValueError("Galat semester number. Sirf 1, 2, ya 3 valid hai.")

    url = SEMESTER_URLS[semester]
    base_url = "https://results.beup.ac.in/"
    
    # ZYADA TIMEOUT KE SAATH SESSION
    session = requests.Session()
    
    print(f"STEP 1: {url} se page fetch kar raha hai...")
    # Timeout 15 se badha kar 45 seconds kar diya gaya hai
    resp = session.get(url, timeout=45)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    print("STEP 1: Page safaltapoorvak fetch hua.")

    viewstate = soup.find("input", {"id": "__VIEWSTATE"})
    viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})

    if not all([viewstate, viewstategenerator, eventvalidation]):
        print("ERROR: Zaroori form fields nahi mile!")
        raise RuntimeError("Result page se zaroori form fields nahi mile. Website ka structure badal gaya ho sakta hai.")

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
    # Timeout 15 se badha kar 45 seconds kar diya gaya hai
    result_page = session.post(url, data=payload, timeout=45)
    result_page.raise_for_status()
    result_html_string = result_page.text
    print("STEP 2: Result page safaltapoorvak mil gaya.")

    print("STEP 3: WeasyPrint se PDF bana raha hai...")
    html_doc = HTML(string=result_html_string, base_url=base_url)
    pdf_bytes = html_doc.write_pdf()
    print("STEP 3: PDF safaltapoorvak ban gayi.")
    
    return pdf_bytes

@app.route('/download-result', methods=['POST'])
def download_result():
    data = request.get_json()
    reg_no = data.get('reg_no')
    semester = data.get('semester')

    if not reg_no or not semester:
        return jsonify({"error": "Registration number aur semester zaroori hai."}), 400

    try:
        pdf_content = fetch_result_and_save_pdf(reg_no, str(semester))
        return send_file(
            BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'BEUP_Result_Sem{semester}_{reg_no}.pdf'
        )
    except Exception as e:
        print(f"SERVER PAR ERROR AAYI HAI: {e}") # Isse Render ke logs mein error dikhega
        return jsonify({"error": f"Result download nahi kar paaye. Server par error: {str(e)}"}), 500

@app.route('/')
def home():
    return "Result PDF Downloader server (v2 - Bulletproof) chal raha hai."

