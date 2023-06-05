from flask import Flask, request, jsonify
import tensorflow as tf
from keras.models import load_model
from keras_preprocessing.image import load_img, img_to_array
import numpy as np
from google.cloud import storage
from google.auth import default
import os
import uuid
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'temp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['JSON_SORT_KEYS'] = False
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# Create the storage client with the provided credentials and project ID
credentials, project_id = default()
storage_client = storage.Client(credentials=credentials, project=project_id)

# Load the trained model
model = load_model('model.hdf5', compile=False)
labels = ['British Shorthair', 'Chihuahua', 'Golden Retriver', 'Persian', 'Poodle', 'Sphynx']

# Load the breed info
with open('breed_info.json', 'r') as file:
    breed_info = json.load(file)

# Configure Google Cloud Storage
bucket_name = 'test-buck-mixue'  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'imgFile' in request.files:
            file = request.files['imgFile']
            if file and allowed_file(file.filename):
                # Periksa ukuran file
                if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
                    return jsonify({
                        'status': 'error',
                        'message': 'File size exceeds the maximum limit (10MB)'
                    }), 400
                file.seek(0)
                if file.filename != '':
                    # Generate a unique filename
                    unique_filename = f'{uuid.uuid4().hex}_{file.filename}'
                    # Save the file to a temporary location
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(temp_path)
                    # Upload the file to Google Cloud Storage
                    blob = bucket.blob(unique_filename)
                    blob.upload_from_filename(temp_path)

                    # Get the public URL of the uploaded file
                    image_url = f'https://storage.googleapis.com/{bucket.name}/{unique_filename}'

                    # Make a prediction on the uploaded image
                    image = load_img(temp_path, target_size=(150, 150))
                    image_array = img_to_array(image) / 255.0
                    image_array = np.expand_dims(image_array, axis=0)
                    prediction = model.predict(image_array)
                    predicted_label = labels[np.argmax(prediction)]
                    confidence = np.max(prediction)

                    # Delete the temporary file
                    os.remove(temp_path)
                    breed_data = breed_info.get(predicted_label, {})

                    return jsonify({
                        'status': 'success',
                        'message': 'File uploaded successfully',
                        'name': 'Cats' if predicted_label in ['British Shorthair', 'Persian', 'Sphynx'] else 'Dogs',
                        'predicted_label': predicted_label,
                        'confidence': float(confidence),
                        'image_url': image_url,
                        'breed_data': breed_data
                    }), 200

        return jsonify({
            'status': 'error',
            'message': 'No file was uploaded or the file type is not allowed'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'imgFile' in request.files:
            file = request.files['imgFile']
            if file.filename != '':
                # Save the file to a temporary location
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
                file.save(temp_path)
                image = load_img(temp_path, target_size=(150, 150))
                os.remove(temp_path)  # Remove the temporary file

                image_array = img_to_array(image) / 255.0
                image_array = np.expand_dims(image_array, axis=0)
                prediction = model.predict(image_array)
                predicted_label = labels[np.argmax(prediction)]
                confidence = np.max(prediction)

                # Upload the image to Google Cloud Storage
                filename = file.filename
                blob = bucket.blob(filename)
                blob.upload_from_string(file.read())
                image_url = f'https://storage.googleapis.com/{bucket_name}/{filename}'
                breed_data = breed_info.get(predicted_label, {})

                return jsonify({
                    'status': 'success',
                    'message': 'File uploaded successfully',
                    'name': 'Cats' if predicted_label in ['British Shorthair', 'Persian', 'Sphynx'] else 'Dogs',
                    'predicted_label': predicted_label,
                    'confidence': float(confidence),
                    'image_url': image_url,
                    'breed_data': breed_data
                }), 200

        return jsonify({
            'status': 'error',
            'message': 'No file was uploaded'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
