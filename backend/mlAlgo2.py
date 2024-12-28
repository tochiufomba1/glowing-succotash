import numpy as np
import pandas as pd
import re
import json
from json import JSONEncoder

# importing sklearn libraries
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import CategoricalNB
from joblib import dump, load

def train(name):
    # the training set is just transaction name -> category
    # train_data = pd.read_csv('./data/2020_4NucareTrainingData.csv', encoding='utf-8', header=0)
    # Connect to the database
    conn = sqlite3.connect('database.db')
    cur = con.cursor()

    res = cur.execute("SELECT name FROM businesses")
    businesses = res.fetchall()
    print(businesses)
    
    query = ""
    if name in businesses:
        query = "SELECT * FROM {name}"
    else:
        return # error
    
    originalData = pd.read_sql_query(query, conn)

    conn.close()

    # train the classifier
    vectorizer = CountVectorizer(ngram_range=(1,2), max_features = 3500)

    # let's build a train column based on name, merchant and amount
    # train_col = train_data['name'] + ' ' +  train_data['merchant'] + ' ' + train_data['amount'].map(lambda x: 'income' if x > 0 else 'expense')
    # train_data['NewDesc'] = train_data['Description'] + ' ' + train_data['Name']
    train_col = train_data['Description']
    # normalize the names to lowercase and remove special characters, and remove words that are less than 3 characters
    names = train_col.str.lower().replace(r'[^\w\s]|https?://\S+|www\.\S+|https?:/\S+|[^\x00-\x7F]+|zelle payment to |DEBIT PURCHASE -VISA|\d+', '', regex=True)
    y_train = train_data['Account']
    x_train = vectorizer.fit_transform(names.values.astype('U')).toarray()

    # train the model
    classifier = RandomForestClassifier(n_estimators=50, random_state=42)
    # classifier = CategoricalNB()
    classifier.fit(x_train, y_train)

    # save the model
    dump([vectorizer,classifier], './data/{name}.joblib')

train()