import pandas as pd
import re
import pickle
import io
from joblib import dump, load
import os

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
    text_test_BERT = text_test_raw.str.lower().replace(r'[^\w\s]|https?://\S+|www\.\S+|https?:/\S+|[^\x00-\x7F]+|zelle payment to |DEBIT PURCHASE -VISA|\d+', '', regex=True)

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
    inputData['Amount'] = inputData['Amount'].fillna(0)
    inputData = inputData[['Date', 'Number', 'Payee', 'Account', 'Amount', 'Description']]

    # add indices to rows for updates to data by users
    inputData = inputData.reset_index(drop=True)
    
    # tables to be sent to user (both use cleaned text)
    interactData = inputData.copy()
    interactData['Description'] = text_test_BERT
    summaryPage = interactData.copy()

    return inputData, interactData, summaryPage

def createTable(session, business, filename):
    OrigDF, BertDF, summaryPage = classify(os.environ.get("UPLOAD_FOLDER"), filename, business)
    session['data'] = pickle.dumps(OrigDF)
    session['bertDescriptions'] = pickle.dumps(BertDF)

    #transformations of summary
    summaryPage = summaryPage.drop_duplicates(subset=['Description', 'Account'], keep='first').copy()
    #summaryPage.drop(columns=['Date', 'Number', 'Payee', 'Amount',], errors='ignore')
    summaryPage = summaryPage[['Description', 'Account']]
    summaryPage['Total'] = summaryPage['Description'].apply(lambda x: BertDF.loc[BertDF['Description'] == x, 'Amount'].sum())
    summaryPage['Instances'] = summaryPage['Description'].apply(lambda x: (BertDF.Description == x).sum())
    summaryPage = summaryPage.reset_index(drop=True)

    session['summaryPage'] = pickle.dumps(summaryPage)
    session['filename'] = filename
    session['business'] = business

def deleteTmpFile(uploadFolder, filename):
    path = os.path.join(uploadFolder, filename)
    if os.path.exists(path):
        os.remove(path)
    else:
        return