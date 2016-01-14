#!/usr/bin/env python3
import dill
import requests as rq
from creds import TCIA_API_KEY, MASHAPE_API_KEY, PROD_MASHAPE_API_KEY
import ujson
import multiprocessing as mp

app = Flask(__name__)

API_ADDRESS = 'https://tcia.p.mashape.com/'
STUDY = 'TCGA-GBM'
#getPatientStudy

def getStudy(collection=STUDY):
    response = rq.get(API_ADDRESS+'getPatientStudy/',
            headers={'X-Mashape-Key': PROD_MASHAPE_API_KEY, 'api_key': TCIA_API_KEY,
                'Accept': 'application/json'}, params={'Collection': collection,
                    'format': 'JSON'})
    return ujson.loads(response.text)

def getSeries(PatientID, StudyInstanceUID, collection=STUDY):
    response = rq.get(API_ADDRESS+'getSeries/',
            headers={'X-Mashape-Key': PROD_MASHAPE_API_KEY, 'api_key': TCIA_API_KEY,
                'Accept': 'application/json'}, params={'Collection': collection,
                    'PatientID': PatientID,
                    'StudyInstanceUID': StudyInstanceUID,
                    'format': 'JSON'})
    return ujson.loads(response.text)

def getMRI(SeriesInstanceUID, filename):
    response = rq.get(API_ADDRESS+'getImage/',
            headers={'X-Mashape-Key': PROD_MASHAPE_API_KEY, 'api_key': TCIA_API_KEY,
                'Accept': 'application/json'}, params={
                    'SeriesInstanceUID': SeriesInstanceUID}, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

pool = mp.pool(mp.cpu_count)
study = getStudy(STUDY)
print(study)
series = getSeries(study[0]['PatientID'], study[0]['StudyInstanceUID'],
        collection=STUDY)
print(series)

