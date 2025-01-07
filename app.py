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
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

#NLP toolkits
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
url = urlparse(os.environ.get("REDIS_URL"))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password, ssl=(url.scheme == "rediss"), ssl_cert_reqs=None)

app = Flask(__name__, template_folder="./frontend/dist", static_url_path='/static', static_folder='./frontend/dist/static')
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = os.environ.get("SESSION_TYPE")
# redis.from_url(os.environ.get("REDIS_URL"))
app.config["SESSION_REDIS"] = r
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
engine = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
CORS(app, supports_credentials=True)
Session(app)

db = SQLAlchemy(app)
class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Business %r>' % self.title

class NewKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    account = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<NewKnowledge %r>' % self.title

class ForeverYoung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    account = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<ForeverYoung %r>' % self.title
    
class Nucare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    account = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Nucare %r>' % self.title

class NucareCOA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<NucareCOA %r>' % self.title

# with app.app_context():
#     db.create_all()
#     df1 = pd.read_excel("./backend/static/nucareCOA.xlsx")

#     try:
#         df1.to_sql('NucareCOA', con=engine, if_exists='replace', index=False)
#     except Exception as e:
#         print("error with data initialization")

# app.config.from_pyfile('./backend/config.py')
# app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL"))
# CORS(app, supports_credentials=True)
# Session(app)

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
            vectorizer, classifier = load('./backend/data/categorizer2.joblib')
        else:
            vectorizer, classifier = load('./backend/data/categorizer.joblib')

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

    # classify data
    x = vectorizer.transform(text_test_BERT.values.astype('U')).toarray()
    categories = classifier.predict(x)

    # add result to resulting dataframe
    inputData.drop(columns=['Details', 'Type', 'Balance', "Num", "Adj", "Name"], errors='ignore')
    inputData['Date'] = pd.to_datetime(inputData['Date'], format= '%Y-%m-%d', errors='coerce')
    inputData['Date'] = inputData['Date'].astype(str) # REVIEW
    inputData['Account'] = pd.Series(categories)
    inputData['Number'] = ""
    inputData['Payee'] = ""
    inputData['Amount'] = ""
    inputData = inputData[['Date', 'Number', 'Payee', 'Account', 'Amount', 'Description']]

    # add indices to rows for updates to data by users
    inputData = inputData.reset_index()
    
    # tables to be sent to user (both use cleaned text)
    interactData = inputData.copy()
    interactData['Description'] = text_test_BERT
    summaryPage = interactData.copy()

    return inputData, interactData, summaryPage

def createTable(business, filename):
    OrigDF, BertDF, summaryPage = classify(os.environ.get("UPLOAD_FOLDER"), filename, business)
    session['data'] = pickle.dumps(OrigDF)
    session['bertDescriptions'] = pickle.dumps(BertDF)

    #transformations of summary
    summaryPage = summaryPage.drop_duplicates(subset=['Description', 'Account'], keep='first').copy()
    summaryPage.drop(columns=['Date', 'Number', 'Payee', 'Amount',], errors='ignore')
    summaryPage = summaryPage[['Description', 'Account']]
    summaryPage = summaryPage.reset_index()

    session['summaryPage'] = pickle.dumps(summaryPage)
    session['filename'] = filename
    session['business'] = business

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
        file.save(os.path.join(os.environ.get("UPLOAD_FOLDER"), filename))
        createTable(business,filename)
        return "Success"

app.add_url_rule(
    "/upload", endpoint="upload_file", build_only=True
)

@app.route('/api/dataTable')
def data():
    # data for the table and summary tabs
    df_pickled = session.get('bertDescriptions', None)
    df_summary = session.get('summaryPage', None)

    # TODO: collect chart of account options for given business
    meta_data = db.MetaData()
    meta_data.reflect(bind=engine)
    NCOA = meta_data.tables['NucareCOA']
    query = db.select(
        NCOA.c.description,
    )

    nucareCOA = engine.execute(query).fetchall()

    # nucareCOA = NucareCOA.query.all()
    #conn = sqlite3.connect('database.db')
    #cur = conn.cursor()

    #res = cur.execute("SELECT * FROM nucareCOA")

    #nucareCOA = [str(row[0]) for row in res]

    #conn.close()
    
    # convert to JSON and send to frontend
    if df_pickled and df_summary and nucareCOA:
        # df = pickle.loads(SESSION_REDIS.get(df_id))
        df = pickle.loads(df_pickled)
        df_json = df.to_json(orient='records')
        df2 = pickle.loads(df_summary)
        df_json2 = df2.to_json(orient='records')

        optionsJSON = json.dumps(nucareCOA)

        print(df)
        print(nucareCOA)

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

def add_row(row):
    newData = Nucare(description=row['Description'], account=row['Account'])
    db.session.add(newData)
    db.session.commit()

def recordDifferences(oldData, newData):
    # oldData['Date'] = oldData['Date'].astype(str)
    # newData['Date'] = newData['Date'].astype(str)
    
    # find differences (rows that user updated in 'newData')
    merged_df = pd.merge(oldData, newData, how='right', indicator=True)

    # collect differences into dataframe
    final_df = merged_df[merged_df['_merge'] == 'right_only']
    final_df.drop(columns=['_merge', 'index'])
    final_df = final_df[['Description', 'Account']]
   
    # TODO: Handle differences
    if(final_df.shape[0] != 0):
        print("not done")
        # final_df.apply(add_row, axis=1)
        
        # execute script to retrain model

    return

@app.route('/api/export', methods=['POST'])
def export():
    # Get frame with the original descriptions
    df_pickled = session.get('data', None)
    oldFrame = pickle.loads(df_pickled)

    # Get frame that the user interacts with
    itemizedUnloaded = session.get('bertDescriptions', None)
    df_itemized = pickle.loads(itemizedUnloaded)

    # Place original descriptions in data user has interacted with
    df_itemized['Description'] = oldFrame['Description'].values

    # Update database
    #recordDifferences(oldFrame, df_itemized)

    # Create excel file
    df_itemized = df_itemized[['Date', 'Number', 'Payee', 'Account', 'Amount', 'Description']]
    # df_itemized.drop(columns=['index'])
    excel_file = io.BytesIO()
    df_itemized.to_excel(excel_file, index=False)
    excel_file.seek(0)

    return send_file(excel_file, as_attachment=True, download_name= session['filename'][:-5] + "_labeled" + ".xlsx")


app.add_url_rule(
    "/api/export", endpoint="data", build_only=True
)

@app.route("/api/updateItem/<int:id>", methods=['PUT'])
def updateTable(id):
    data = request.get_json()

    # update itemized table
    itemizedUnloaded = session.get('bertDescriptions', None)
    df_itemized = pickle.loads(itemizedUnloaded)
    df_itemized.iloc[id, 4] = data['Account']
    session['bertDescriptions'] = pickle.dumps(df_itemized)

    dataw = {
        'message': 'Hello, world!',
        'number': 42
    }
    
    return jsonify(dataw)

# app.add_url_rule(
#     "/api/export", endpoint="data", build_only=True
# )

@app.route("/api/updateSummary/<int:id>", methods=['PUT'])
def updatSummaryTable(id):
    data = request.get_json()
    
    # update summary table
    summaryUnloaded = session.get('summaryPage', None)
    df_summary = pickle.loads(summaryUnloaded)
    df_summary.iloc[id, 2] = data['Account']
    session['summaryPage'] = pickle.dumps(df_summary)

    # update itemized table
    itemizedUnloaded = session.get('bertDescriptions', None)
    df_itemized = pickle.loads(itemizedUnloaded)
    df_itemized.loc[df_itemized['Description'] == data['Description'], ['Account']] = data['Account']
    session['bertDescriptions'] = pickle.dumps(df_itemized)
    
    dataw = {
        'message': 'Hello, world!',
        'number': 42
    }
    
    return jsonify(dataw)

# app.add_url_rule(
#     "/api/export", endpoint="data", build_only=True
# )

if __name__ == '__main__':
    with open("./backend/init_db.py", "r") as f:
        script_code = f.read()
    exec(script_code)
    port = int(os.environ.get("PORT", 5000))
    app.config["SESSION_COOKIE_HTTPONLY"] = os.environ.get("SESSION_COOKIE_HTTPONLY")
    app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE")
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE")
    app.config["SESSION_USE_SIGNER"] = os.environ.get("SESSION_USE_SIGNER")
    app.run(debug=False, host='0.0.0.0', port=port)