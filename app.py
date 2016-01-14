#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import dill
import requests as rq
from creds import TCIA_API_KEY, MASHAPE_API_KEY, PROD_MASHAPE_API_KEY
import ujson
import dicom
import numpy as np
from natsort import natsorted
import os

from bokeh.plotting import figure
from bokeh.io import gridplot, show
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
from bokeh.palettes import Greys9 as greys

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

def loadDICOM(folder):
    list_DCM = []
    for dirName, subdirList, fileList in os.walk(folder):
        for filename in fileList:
            if ".dcm" in filename.lower():  # check whether the file's DICOM
                list_DCM.append(os.path.join(dirName,filename))
    list_DCM = natsorted(list_DCM)
    ref_dcm = dicom.read_file(list_DCM[0])
    ConstPixelDims = (int(ref_dcm.Rows), int(ref_dcm.Columns), len(list_DCM))
    ConstPixelSpacing = (float(ref_dcm.PixelSpacing[0]),
            float(ref_dcm.PixelSpacing[1]), float(ref_dcm.SliceThickness))

    x = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])

    img_array = np.zeros(ConstPixelDims, dtype=ref_dcm.pixel_array.dtype)

    for i, fname in enumerate(list_DCM):
        dcm = dicom.read_file(fname)
        img_array[:,:,i] = dcm.pixel_array
    img_array = img_array/np.max(img_array)*255.0

    return img_array, (x,y,z)


def plot_im_grid(imarray, dims):
    x, y, z  = dims
    plot_list = []
    for layer, depth in zip(range(imarray.shape[-1]), z):
        p = figure(x_range=[x[0], x[-1]], y_range=[y[0], y[-1]],
                title="Depth %.0f mm"%(depth))
        p.image(image=[np.squeeze(imarray[:,:,layer])], x=[0], y=[0],
                dw=x[-1], dh=y[-1], palette="Greys9")
        plot_list.append(p)
    grid = gridplot([plot_list[:6],plot_list[6:12],plot_list[12:]])
    show(grid)
    return components(grid)


@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/gallery')
def gallery():
    imarray, dims = loadDICOM('imgs')

    script, div = plot_im_grid(imarray, dims)

    return render_template('gallery.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507, debug=True)
