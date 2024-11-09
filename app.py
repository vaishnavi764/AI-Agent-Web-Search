from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import json

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'csv'}

# Check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to decode private key to check for correctness
def check_private_key_format():
    # Read the credentials.json file
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
    
    # Extract the private key
    private_key = credentials.get("private_key")
    
    # Check if private key is present
    if private_key:
        # Remove the BEGIN/END markers and decode the base64
        private_key_clean = private_key.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\n", "")
        
        try:
            decoded_key = base64.b64decode(private_key_clean)
            print("Decoded private key: ", decoded_key)
        except Exception as e:
            print(f"Error decoding private key: {e}")
    else:
        print("Private key not found in credentials.")

# Run the check for the private key
check_private_key_format()

# Route to upload CSV or connect Google Sheets
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                return redirect(url_for('preview_file', filename=file.filename))

        # Handle Google Sheets URL
        if 'gsheet_url' in request.form:
            gsheet_url = request.form['gsheet_url']
            data = fetch_google_sheet(gsheet_url)
            return render_template('index.html', data=data)

    return render_template('index.html', data=None)

# Route to display uploaded CSV file data
@app.route('/preview/<filename>', methods=['GET'])
def preview_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = pd.read_csv(filepath)
    return render_template('index.html', data=data.to_html(classes='table table-striped'))

# Fetch data from Google Sheets
def fetch_google_sheet(gsheet_url):
    # Scope for accessing Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    
    # Loading credentials from 'credentials.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    # Get the sheet by URL
    sheet = client.open_by_url(gsheet_url)
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_records()
    
    # Convert to pandas DataFrame and return
    return pd.DataFrame(data)

if __name__ == '__main__':
    app.run(debug=True)
