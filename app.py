from flask import Flask, render_template, request, session, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to something more secure
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home route to redirect to the upload page
@app.route('/')
def home():
    return render_template('index.html')  # Render the index page

# Route for uploading the CSV file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        
        # If no file is selected
        if file.filename == '':
            return "No selected file"
        
        # If the file is valid
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Save the file path in the session
            session['temp_file_path'] = file_path
            
            return redirect(url_for('query'))  # Redirect to the query page after uploading
            
    return render_template('upload.html')  # Render the upload page to select a CSV file

# Route to define search queries and extract column data
@app.route('/query', methods=['GET', 'POST'])
def query():
    error = None  # To store error message if column is not found
    if request.method == 'POST':
        # Strip any whitespace around the selected column and convert to lowercase
        column = request.form['column'].strip().lower()
        print(f"Selected Column: '{column}'")  # Debugging line
        
        if 'temp_file_path' in session:
            temp_file_path = session['temp_file_path']
            
            try:
                df = pd.read_csv(temp_file_path)
                
                # Normalize column names by stripping whitespace and converting to lowercase
                df.columns = df.columns.str.strip().str.lower()
                
                print("CSV Data Loaded Successfully")
                print(f"Columns in CSV (after normalization): {df.columns.tolist()}")  # Debugging line
                
            except FileNotFoundError:
                return "Temporary CSV file not found. Please upload the file again."
            
            # Check if the column exists in the dataframe
            if column in df.columns:
                column_data = df[column].dropna().astype(str).tolist()  # Extract and convert column data to string
                print(f"Extracted Column Data: {column_data}")  # Debugging line
                
                # Store the extracted column data in session to pass to results page
                session['extracted_data'] = [{'Value': value} for value in column_data]
                
                # Redirect to the results page after extracting the data
                return redirect(url_for('results'))
            else:
                error = f"Column '{column}' not found in the CSV."
            
    # If GET request, show the form with normalized columns
    if 'temp_file_path' in session:
        temp_file_path = session['temp_file_path']
        df = pd.read_csv(temp_file_path)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        columns = df.columns.tolist()  # Get normalized column names
        return render_template('query.html', columns=columns, error=error)  # Pass columns and error to the form
    
    return redirect(url_for('upload_file'))  # Redirect to upload if no file is uploaded

# Route to display results (extracted column data)
@app.route('/results')
def results():
    # Retrieve the extracted data from the session
    extracted_data = session.get('extracted_data', [])
    print(f"Extracted Data from Session: {extracted_data}")  # Debugging line

    if extracted_data:
        return render_template('results.html', results=extracted_data)
    else:
        return "No results available. Please upload a CSV and query."

# Route for the help page
@app.route('/help')
def help():
    return render_template('help.html')  # Render a simple help page

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
