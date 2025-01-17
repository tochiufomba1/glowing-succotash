import numpy as np
import pandas as pd
import re
import json
from json import JSONEncoder
import psycopg2

# importing sklearn libraries
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import CategoricalNB
from joblib import dump, load

def train(conn, name):
    # query database and create dataframe
    cur = conn.cursor()
    cur.execute("SELECT * FROM generic")
    results = cur.fetchall()
    train_data = pd.DataFrame(results, columns=[desc[0] for desc in cur.description])

    # train the classifier
    vectorizer = CountVectorizer(ngram_range=(1,2), max_features = 3500)

    # get transaction descriptions
    train_col = train_data['description']

    # normalize the names to lowercase and remove special characters, and remove words that are less than 3 characters
    names = train_col.str.lower().replace(r'[^\w\s]|https?://\S+|www\.\S+|https?:/\S+|[^\x00-\x7F]+|zelle payment to |DEBIT PURCHASE -VISA|\d+', '', regex=True)
    y_train = train_data['account']
    x_train = vectorizer.fit_transform(names.values.astype('U')).toarray()

    # train the model
    classifier = RandomForestClassifier(n_estimators=50, random_state=42)
    classifier.fit(x_train, y_train)

    # save the model
    dump([vectorizer,classifier], f"./data/{name}.joblib")
    
    cur.close()