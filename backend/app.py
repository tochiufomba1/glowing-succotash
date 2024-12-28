import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, session, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS
import redis
import pickle
import random
import string
import json
from flask_session import Session
import io
from joblib import dump, load
import re
import numpy as np 
import sqlite3

#NLP toolkits
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

app = Flask(__name__, template_folder="../frontend/dist", static_url_path='/static', static_folder='../frontend/dist/static')
app.config.from_pyfile('config.py')
app.config["SESSION_REDIS"] = redis.from_url('redis://127.0.0.1:6379')
CORS(app, supports_credentials=True)
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocess transaction description data from user-provided file
def clean_text_BERT(text):
    # Convert words to lower case.
    text = text.lower()

    # Remove special characters and numbers. This also removes the dates 
    # which are not important in classifying expenses
    text = re.sub(r'[^\w\s]|https?://\S+|www\.\S+|https?:/\S+|[^\x00-\x7F]+|zelle payment to |DEBIT PURCHASE -VISA|\d+', '', str(text).strip())
  
    # Tokenise 
    text_list = word_tokenize(text)
    result = ' '.join(text_list)
    return result

def classify(uploadFolder,filename, business):
    global loaded, vectorizer, classifier
    loaded = False
    if not loaded:
        if business == "Nucare":
            vectorizer, classifier = load('./data/categorizer2.joblib')
        else:
            vectorizer, classifier = load('./data/categorizer.joblib')
        # vectorizer, classifier = load('./data/categorizer.joblib')
        loaded = True

    # TODO: Add functionality for csv files
    inputData = pd.read_excel(os.path.join(uploadFolder, filename))

    # Transactions' description column title may change per bank, standardize column title to 'Description'
    if 'Memo' in inputData.columns:
        inputData.rename(columns={'Memo': 'Description'}, inplace=True)
    
    # remove special characters and short words from the input
    inputData.Description = inputData.Description.astype(str)
    text_test_raw = inputData['Description']
    text_test_BERT = text_test_raw.apply(lambda x: clean_text_BERT(x))

    x = vectorizer.transform(text_test_BERT.values.astype('U')).toarray()
    categories = classifier.predict(x)

    # add result to resulting dataframe
    inputData.drop(columns=['Details', 'Type', 'Balance', "Num", "Adj", "Name"], errors='ignore')
    inputData['Date'] = pd.to_datetime(inputData['Date'], format= '%Y-%m-%d', errors='coerce')
    inputData['Date'] = inputData['Date'].astype(str) # REVIEW
    inputData['Account'] = pd.Series(categories)
    inputData['Number'] = ""
    inputData['Payee'] = ""
    #inputData['Amount'] = ""
    inputData = inputData[['Account Number','Date', 'Number', 'Payee', 'Account', 'Amount', 'Description']]
    #inputData = inputData.sort_values(by=['Description'], inplace=True, ascending=True)
    
    interactData = inputData.copy()
    interactData['Description'] = text_test_BERT
    summaryPage = interactData.copy()

    return inputData, interactData, summaryPage

def createTable(business, filename):
    OrigDF, BertDF, summaryPage = classify(app.config['UPLOAD_FOLDER'], filename, business)
    # df = label(app.config['UPLOAD_FOLDER'], business, filename) # create new file?
    session['data'] = pickle.dumps(OrigDF)
    session['bertDescriptions'] = pickle.dumps(BertDF)

    #transformations of summary
    summaryPage = summaryPage.drop_duplicates(subset=['Description', 'Account'], keep='first').copy()
    summaryPage.drop(columns=['Date', 'Number', 'Payee', 'Amount',], errors='ignore')
    summaryPage = summaryPage[['Description', 'Account']]

    session['summaryPage'] = pickle.dumps(summaryPage)
    session['filename'] = filename

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    business = request.form['business']
        
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        print("no selected file")
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        createTable(business,filename)
        return "Success"

app.add_url_rule(
    "/upload", endpoint="upload_file", build_only=True
)

def generate_session_id(length=16):
    """Generates a random session ID string."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/downloads/<name>', methods=['GET'])
def download_file(name):
    print(name)
    # response = make_response(send_file(os.path.join("tmp", name))) 
    # response.headers['Content-Disposition'] = f"attachment; filename={name}"
    # response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    # return response
    return send_file(os.path.join("tmp", name), as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

app.add_url_rule(
    "/downloads/<name>", endpoint="download_file", build_only=True
)

@app.route('/api/dataTable')
def data():
    # data for the table and summary tabs
    df_pickled = session.get('bertDescriptions', None)
    df_summary = session.get('summaryPage', None)

    # collect chart of account options for given business
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    res = cur.execute("SELECT * FROM nucareCOA")

    nucareCOA = [str(row[0]) for row in res]
    
    conn.close()

    # convert to JSON and send to frontend
    if df_pickled and df_summary and nucareCOA:
        # df = pickle.loads(SESSION_REDIS.get(df_id))
        df = pickle.loads(df_pickled)
        df_json = df.to_json(orient='records')
        df2 = pickle.loads(df_summary)
        df_json2 = df2.to_json(orient='records')

        optionsJSON = json.dumps(nucareCOA)

        return jsonify({'table': df_json, 'summary': df_json2, 'options': optionsJSON})
    else:
        dataw = {
        'message': 'Hello, world!',
        'number': 42
        }
        return jsonify(dataw)

app.add_url_rule(
    "/api/dataTable", endpoint="data", build_only=True
)

@app.route('/api/data')
def getData():
    df_pickled = session.get('data2', None)

    if df_pickled:
        # df = pickle.loads(SESSION_REDIS.get(df_id))
        df = pickle.loads(df_pickled)
        df_json = df.to_json(orient='records') 
        return jsonify(df_json)
    else:
        dataw = {
        'message': 'Hello, world!',
        'number': 42
        }
        return jsonify(dataw)

app.add_url_rule(
    "/api/dataTable", endpoint="data", build_only=True
)

def recordDifferences(newData):
    df_pickled = session.get('data', None)
    oldData = pickle.loads(df_pickled)

    oldData['Date'] = oldData['Date'].astype(str)
    newData['Date'] = newData['Date'].astype(str)
    
    # find differences (rows that user updated in 'newData')
    merged_df = pd.merge(oldData, newData, how='right', indicator=True)

    # collect differences into dataframe
    final_df = merged_df[merged_df['_merge'] == 'right_only']
    final_df.drop(columns=['_merge'])

    # write dataframe of differences to database
    conn = sqlite3.connect('database.db')
    df.to_sql('records', conn, index=False)
    conn.close()

@app.route('/api/summary')
def summary():
    df_pickled = session.get('data2', None)
    df = pickle.loads(df_pickled)

    # get unique Description and Account pairings from data table
    unique_df = df.drop_duplicates(subset=['Description', 'Account'], keep='first').copy()
    unique_df.drop(columns=['Date', 'Number', 'Payee', 'Amount',], errors='ignore')
    unique_df = unique_df[['Description', 'Account']]

    # send table to user
    df_json = unique_df.to_json(orient='records') 
    return jsonify(df_json)

@app.route('/api/update', methods=['POST'])
def update():
    df_pickled = session.get('data', None)
    df = pickle.loads(df_pickled)

    # get description
    desc = ""
    newAccount = ""

    df.loc[df['Description'] == desc, 'Account'] = newAccount
    indices = df.index[df['A'] > 1]
    return "ok"
    


@app.route('/api/export', methods=['POST'])
def export():
    # read user edits
    data = request.get_json()
    print(data)
    # newFrame = pd.read_json(io.StringIO(json.dumps(data)))

    df_pickled = session.get('data', None)
    newFrame = pickle.loads(df_pickled)

    # update database
    # recordDifferences(newFrame)

    # create excel file
    excel_file = io.BytesIO()
    newFrame.to_excel(excel_file, index=False)
    excel_file.seek(0)

    return send_file(excel_file, as_attachment=True, download_name= session['filename'][:-5] + "_labeled" + ".xlsx")


app.add_url_rule(
    "/api/export", endpoint="data", build_only=True
)