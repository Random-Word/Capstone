#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import dill
import requests as rq
from creds import API_KEY
import ujson

app = Flask(__name__)

TCIA_ADDRESS = 'https://tcia.p.mashape.com/'
STUDY = 'TCIA-BGM'
#getPatientStudy

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/gallery')
def gallery():
    response = rq.get(TCIA_ADDRESS+'getPatientStudy/'+STUDY)
    test = ujson.loads(response.text)

    div="test"
    script=""
    return render_template('gallery.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)
