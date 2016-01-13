from flask import Flask, render_template, request, redirect, dill
import requests
from creds import API_KEY

app = Flask(__name__)

TCIA_ADDRESS = 'https://tcia.p.mashape.com/'
#getPatientStudy

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/gallery')
def gallery():
    response = requests.get(TCIA_ADDRESS)
    div=""
    script=""
    return render_template('gallery.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)
