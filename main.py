from flask import Flask, request, jsonify
from keras.models import load_model
from keras_preprocessing.image import load_img, img_to_array
import numpy as np
from google.cloud import storage
from google.auth import default
from dotenv import load_dotenv
import mysql.connector
import os
import uuid
import json

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_DATABASE
)
cursor = db.cursor()

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
model = load_model('modelv2.hdf5', compile=False)
# labels = ['Chihuahua', 'Golden Retriever', 'Poodle', 'Rottweiler', 'Bulldog', 'Sphynx', 'British Shorthair', 'Persian', 'Bengal']
labels = ['bengal', 'british_shorthair', 'bulldog', 'chihuahua', 'golden_retriever',
                'persian', 'poodle', 'rottweiler', 'sphynx']
cats_labels=['bengal', 'british_shorthair','persian','sphynx']
dogs_labels=['bulldog', 'chihuahua', 'golden_retriever','poodle', 'rottweiler']
# Load the breed info
with open('breed_info.json', 'r') as file:
    breed_info = json.load(file)

# Configure Google Cloud Storage
bucket_name = 'patypet-bucket'  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

import requests

response = requests.get('http://localhost:3000/getGlobalInfo')
global_info = response.json()
email = global_info.get('lastLoggedInEmail')

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'imgFile' in request.files:
            file = request.files['imgFile']
            if file and allowed_file(file.filename):
                if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
                    return jsonify({
                        'status': 'error',
                        'message': 'File size exceeds the maximum limit (10MB)'
                    }), 400
                file.seek(0)
                if file.filename != '':
                    unique_filename = f'{uuid.uuid4().hex}_{file.filename}'
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(temp_path)
                    blob = bucket.blob(unique_filename)
                    blob.upload_from_filename(temp_path)
                    image_url = f'https://storage.googleapis.com/{bucket.name}/{unique_filename}'
                    image = load_img(temp_path, target_size=(224, 224))
                    image_array = img_to_array(image) / 255.0
                    image_array = np.expand_dims(image_array, axis=0)
                    prediction = model.predict(image_array)
                    predicted_label = labels[np.argmax(prediction)]
                    confidence = np.max(prediction).item()
                    os.remove(temp_path)

                    breed_data = breed_info.get(predicted_label, {})

                    if predicted_label in cats_labels:
                        query = "SELECT * FROM groom_product WHERE jenis IN ('kucing','kucing_anjing')"
                    elif predicted_label in dogs_labels:
                        query = "SELECT * FROM groom_product WHERE jenis IN ('anak_anjing', 'anjing', 'kucing_anjing')"
                    else:
                        query = ""

                    if query:
                        cursor.execute(query)
                        groom_result = cursor.fetchall()
                    else:
                        groom_result = []

                    groom_data = []
                    if predicted_label == 'bulldog':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('anjing_kecil_bulldog','anjing_dewasa','anjing_dewasa_kecil','anjing_kecil')"
                    elif predicted_label == 'bengal':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_bengal','kucing_dewasa','kucing_kecil')"
                    elif predicted_label == 'british_shorthair':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_british_shorthair','kucing_kecil_british_shorthair','kucing_dewasa','kucing_kecil')"
                    elif predicted_label == 'golden_retriever':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('anjing_kecil_golden_retriever','kucing_dewasa_golden_retriever','kucing_kecil_golden_retriever','anjing_dewasa','anjing_dewasa_kecil','anjing_kecil')"
                    elif predicted_label == 'chihuahua':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_chihuahua','anjing_dewasa','anjing_dewasa_kecil','anjing_kecil')"
                    elif predicted_label == 'poodle':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_poodle','kucing_kecil_poodle','anjing_dewasa','anjing_dewasa_kecil','anjing_kecil')"
                    elif predicted_label == 'persian':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_persia','kucing_kecil_persia','kucing_dewasa','kucing_kecil')"
                    elif predicted_label == 'sphynx':
                        query_food = "SELECT * FROM food_product WHERE jenis IN ('kucing_dewasa_spyhnx','kucing_dewasa','kucing_kecil')"
                    else:
                        query_food = ""

                    if query_food:
                        cursor.execute(query_food)
                        food_result = cursor.fetchall()
                    else:
                        food_result = []

                    food_data = []
                    shop_data = []
                    for row in groom_result:
                        groom_data.append({
                            'product_name': row[1],
                            'product_price': row[2],
                            'product_url': row[3],
                            'product_img': row[5]
                        })

                    for row in food_result:
                        food_data.append({
                            'product_name': row[1],
                            'product_price': row[2],
                            'product_url': row[3],
                            'product_img': row[5]
                        })

                    shop_data.append({
                        'groom_data': groom_data,
                        'food_data': food_data
                    })

                    query = "INSERT INTO temporary_predictions (email, predicted_label, confidence, image_url) VALUES (%s, %s, %s, %s)"
                    values = (email, predicted_label, confidence, image_url)
                    cursor.execute(query, values)
                    db.commit()
                    global_info['lastLoggedInEmail'] = email
                    
                    return jsonify({
                        'status': 'success',
                        'message': 'File uploaded successfully',
                        'name': 'Cats' if predicted_label in ['bengal', 'british_shorthair','persian','sphynx'] else 'Dogs',
                        'predicted_label': predicted_label,
                        'confidence': float(confidence),
                        'image_url': image_url,
                        'breed_data': breed_data,
                        'shop_data': shop_data,
                        'email': email
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

@app.route('/save', methods=['POST'])
def save():
    try:
        # email = global_info.get('email')
        query = "SELECT * FROM temporary_predictions ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        new_prediction_id = cursor.lastrowid
        data = cursor.fetchall()

        if data:
            row = data[0]
            insert_query = "INSERT INTO predictions (image_url, predicted_label, confidence, email) VALUES (%s, %s, %s, %s)"
            values = (row[2], row[3], row[4], row[5])
            cursor.execute(insert_query, values)
            db.commit()
            global_info['lastLoggedInEmail'] = email

            delete_query = "DELETE FROM temporary_predictions WHERE id = %s"
            cursor.execute(delete_query, (row[0],))
            db.commit()

            return jsonify({
                'status': 'success',
                'message': 'The latest temporary prediction has been saved to the permanent table',
                'prediction_id': new_prediction_id
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No temporary prediction found'
            }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/pet/edit', methods=['PUT'])
def edit_prediction():
    try:
        prediction_id = request.args.get('id')
        new_name = request.args.get('name')

        if not prediction_id or not new_name:
            return jsonify({
                'status': 'error',
                'message': 'Please provide prediction ID and new name'
            }), 400

        select_query = "SELECT * FROM predictions WHERE id = %s"
        cursor.execute(select_query, (prediction_id,))
        prediction = cursor.fetchone()

        if not prediction:
            return jsonify({
                'status': 'error',
                'message': 'Prediction not found'
            }), 404

        update_query = "UPDATE predictions SET name = %s WHERE id = %s"
        cursor.execute(update_query, (new_name, prediction_id))
        db.commit()

        return jsonify({
            'status': 'success',
            'message': 'Prediction name updated successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/allPet', methods=['GET'])
def get_pet():
    try:
        query = "SELECT * FROM predictions"
        cursor.execute(query)
        data = cursor.fetchall()

        columns = [column[0] for column in cursor.description]

        result = []
        for row in data:
            row_data = dict(zip(columns, row))
            result.append(row_data)

        return jsonify({
            'status': 'success',
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/pet/<email>', methods=['GET'])
def get_pet_by_email(email):
    try:
        query = "SELECT * FROM predictions WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchall()

        if data:
            columns = [column[0] for column in cursor.description]
            rows_data = [dict(zip(columns, row)) for row in data]

            return jsonify({
                'status': 'success',
                'data': rows_data
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No predictions found for the email'
            }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
