# Flask utils
from flask import Flask, request, render_template
import numpy as np
import sys
from pylab import *
from PIL import Image, ImageChops, ImageEnhance
from keras.models import load_model
import os
image_saved_path = './static/images/upload.jpg'

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'jpg'}

filename = './models/ELA_CNN.h5'
model = load_model(filename)

def allowed_file(filename):
  return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def home(): 
  return render_template('index.html')


@app.route('/imgclf')
def imgclf(): 
  return render_template('imgclf.html',condval='nooutput')


@app.route('/predictfile',methods=['POST'])
def predictfile():
  file = None
  file = request.files['file']
  if file and allowed_file(file.filename):
    print(file)
    # calculate ELA
    image = Image.open(file).convert('RGB')
    image.save(image_saved_path, 'JPEG', quality=90)
    saved_image = Image.open(image_saved_path)
    ela = ImageChops.difference(image, saved_image)
    extrema = ela.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    ela_im = ImageEnhance.Brightness(ela).enhance(scale)

    # prepare image for testing
    image = array(ela_im.resize((128, 128))).flatten() / 255.0
    image = image.reshape(-1, 128, 128, 3)
    # prediction
    prob = model.predict(image)[0]
    idx = np.argmax(prob)
    pred = model.predict(image)
    pred = pred.argmax(axis=1)[0]

    label = "Image is Tampered" if pred == 1 else "Image is Not Tampered"
    #return label, prob[idx]
    
  return render_template('imgclf.html',res2 = label,image = image_saved_path)



if __name__ == '__main__':
    app.run(debug=False)

