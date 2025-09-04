import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from weasyprint import HTML  # pdfkit ke badle WeasyPrint ko import kiya

app = Flask(__name__)
CORS(app)

# University Result URLs
SEMESTER_URLS = {
    "1": "https://results.beup.ac.in/BTech1stSem2023_B2023Results.aspx",
    "2": "https://results.beup.ac.in/BTech2ndSem2024_B2023Results.aspx",
    "3": "https://results.beup.ac.in/BTech3rdSem2025_B2023Results.aspx"
}

def fetch_result_and_save_pdf(reg_no: str, semester: str):
    """
    Result fetch karta hai aur WeasyPrint ka istemal karke PDF banata hai.
    """
    if semester not in SEMESTER_URLS:
        raise ValueError("Galat semester number. Sirf 1, 2, ya 3 valid hai.")

    url = SEMESTER_URLS[semester]
    base_url = "https://results.beup.ac.in/"
    
    session = requests.Session()
    
    # Step 1: Page load karo
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Hidden fields nikalna
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})
    viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})

    if not all([viewstate, viewstategenerator, eventvalidation]):
        raise RuntimeError("Result page se zaroori form fields nahi mile.")

    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator["value"],
        "__EVENTVALIDATION": eventvalidation["value"],
        "ctl00$ContentPlaceHolder1$TextBox_RegNo": reg_no,
        "ctl00$ContentPlaceHolder1$Button_Show": "Show Result"
    }

    # Step 2: POST request bhejna
    result_page = session.post(url, data=payload, timeout=30)
    result_page.raise_for_status()
    result_html_string = result_page.text

    # Step 3: PDF banana (WeasyPrint ke saath)
    # Humein CSS/Images ke liye base URL batana hota hai
    html_doc = HTML(string=result_html_string, base_url=base_url)
    pdf_bytes = html_doc.write_pdf()
    
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
        
        # PDF ko browser mein download ke liye bhejna
        return send_file(
            BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'BEUP_Result_Sem{semester}_{reg_no}.pdf'
        )

    except Exception as e:
        print(f"Error aayi hai: {e}")
        return jsonify({"error": f"Result download nahi kar paaye. Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "Result PDF Downloader server chal raha hai."

# Yeh lines Render.com par zaroori nahi hain
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

