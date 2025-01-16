import os
from celery import Celery
import pickle
import pandas as pd
from io import BytesIO

app = Celery('tasks')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

@celery.task
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