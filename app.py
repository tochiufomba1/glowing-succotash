import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, session, jsonify, send_file, make_response, abort
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS
import redis
from celery import Celery
import pickle
import random
import string
import json
from flask_session import Session
import io
import re
import numpy as np 
from urllib.parse import urlparse
import psycopg2
from flask_compress import Compress
import helpers
import tasks
from psycopg2 import sql

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
url = urlparse(os.environ.get("REDIS_URL"))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password, ssl=(url.scheme == "rediss"), ssl_cert_reqs=None)

app = Flask(__name__, template_folder="./frontend/dist", static_url_path='/static', static_folder='./frontend/dist/static')
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = os.environ.get("SESSION_TYPE")
app.config["SESSION_REDIS"] = r

CORS(app, supports_credentials=True)
Compress(app)
Session(app)
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route("/")
def index():
    return render_template("index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        helpers.createTable(session,business,filename)
        return "Success"

app.add_url_rule(
    "/upload", endpoint="upload_file", build_only=True
)

@app.route('/api/dataTable')
def data():
    # data for the table and summary tabs
    df_pickled = session.get('bertDescriptions', None)
    df_summary = session.get('summaryPage', None)

    # collect chart of account options for given business
    cur = conn.cursor()
    
    try:
        res = cur.execute(
            sql.SQL("SELECT description FROM {};").format(sql.Identifier(tableName))
        )
    except Exception as e:
        print(e)

    res = cur.fetchall()
    COA = [str(row[0]) for row in res]
    cur.close()
    
    # convert to JSON and send to frontend
    if df_pickled and df_summary and COA:
        df = pickle.loads(df_pickled)
        df_json = df.to_json(orient='records')
        df2 = pickle.loads(df_summary)
        df_json2 = df2.to_json(orient='records')

        optionsJSON = json.dumps(COA)

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
    cur = conn.cursor()
    try:
        cur.execute(
            sql.SQL("INSERT INTO {table} (description, account) VALUES (%s, %s)").format(table=sql.Identifier(session.get('business'))), [row['Description'],row['Account']]
        )
    except Exception as e:
        print("couldn't add row")

def recordDifferences(oldData, newData):
    # find differences (rows that user updated in 'newData')
    merged_df = pd.merge(oldData, newData, how='right', indicator=True)

    # collect differences into dataframe
    final_df = merged_df[merged_df['_merge'] == 'right_only']
    final_df.drop(columns=['_merge', 'index'])
    final_df = final_df[['Description', 'Account']]
   
    # TODO: Handle differences
    if(final_df.shape[0] != 0):
        final_df.apply(add_row, axis=1)
        
        # execute script to retrain model

    return

@app.route('/api/export')
def export():
    df_pickled = session.get('data', None)
    itemizedUnloaded = session.get('bertDescriptions', None)
    task = tasks.createExcelFile.apply_async(args=[df_pickled, itemizedUnloaded])
    
    return jsonify({'job_id': task.id})

app.add_url_rule(
    "/api/export", endpoint="data", build_only=True
)

@app.route('/api/export/<task_id>')
def exportFile(task_id):
    task = tasks.createExcelFile.AsyncResult(task_id)
    if task.state == 'SUCCESS': 
        helpers.deleteTmpFile(os.environ.get("UPLOAD_FOLDER"),session.get('filename'))
        output = io.BytesIO(task.result) 
        return send_file(output, as_attachment=True, download_name='labeledDatax.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
    else: 
        abort(500)
    

@app.route("/api/updateItem/<int:id>", methods=['PUT'])
def updateTable(id):
    data = request.get_json()

    # update itemized table
    itemizedUnloaded = session.get('bertDescriptions', None)
    df_itemized = pickle.loads(itemizedUnloaded)
    df_itemized.iloc[id, 3] = data['Account']
    session['bertDescriptions'] = pickle.dumps(df_itemized)

    dataw = {
        'message': 'Hello, world!',
        'number': 42
    }
    
    return jsonify(dataw)

@app.route("/api/updateSummary/<int:id>", methods=['PUT'])
def updatSummaryTable(id):
    data = request.get_json()
    
    # update summary table
    summaryUnloaded = session.get('summaryPage', None)
    df_summary = pickle.loads(summaryUnloaded)
    df_summary.iloc[id, 1] = data['Account'] # REVIEW
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

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER")
    app.config["SESSION_COOKIE_HTTPONLY"] = os.environ.get("SESSION_COOKIE_HTTPONLY")
    app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE")
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE")
    app.config["SESSION_USE_SIGNER"] = os.environ.get("SESSION_USE_SIGNER")
    app.run(debug=False, host='0.0.0.0', port=port)