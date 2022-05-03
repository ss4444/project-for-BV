from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import tensorflow as tf
from keras.models import load_model
from keras_preprocessing import image
import numpy as np
from PIL import Image

model = load_model('model.h5')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        ipath = f'static/files/{file.filename}'
        img = image.load_img(ipath, target_size=(200, 200), color_mode='grayscale')
        img_tensor = image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor /= 255.
        ff = model.predict(img_tensor)
        ff = max(ff).tolist()
        for i in range(len(ff)):
            ff[i] = ff[i] * 100
            ff[i] = round(ff[i], 2)
        ff = 'Cyst: ' + str(ff[0]) + '\n' + 'Normal: ' + str(ff[1]) + '\n' + 'Stone: ' + str(ff[2]) + '\n' + 'Tumor: ' + str(ff[3])
        os.remove(ipath)
        return str(ff)
    return render_template('index.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)