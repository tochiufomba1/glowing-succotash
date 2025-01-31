import os
from celery import Celery
import pickle
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse
import redis

app = Celery('tasks')
url = urlparse(os.environ.get("REDISCLOUD_URL"))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
app.conf.update(broker_url=os.environ.get("REDISCLOUD_URL"), result_backend=os.environ.get("REDISCLOUD_URL"), broker_connection_retry_on_startup=True)

@app.task
def createExcelFile(df_pickled, itemizedUnloaded):
    # Get frame with the original descriptions
    oldFrame = pickle.loads(df_pickled)

    # Get frame that the user interacts with
    df_itemized = pickle.loads(itemizedUnloaded)

    # Place original descriptions in data user has interacted with
    df_itemized['Description'] = oldFrame['Description'].values

    # Update database
    #recordDifferences(oldFrame, df_itemized)

    # Create excel file
    df_itemized = df_itemized[['Date', 'Number', 'Payee', 'Account', 'Amount', 'Description']] # df_itemized.drop(columns=['index'])
    excel_file = BytesIO()
    df_itemized.to_excel(excel_file, index=False)
    excel_file.seek(0)

    return excel_file.getvalue()