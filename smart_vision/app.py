from flask import Flask, request
import numpy as np
import cv2
from PIL import Image
import io
import json
import os
import pytesseract
from twilio.rest import Client
from objdet import *
from currencydet import *

from text_ocr import *


# =========== SOS config ==========
AccountSID = os.getenv("TWILIO_SID")
AuthToken = os.getenv("TWILIO_AUTH_TOKEN")

# =========== Yolo config ==========
INPUT_WIDTH = 640
INPUT_HEIGHT = 640
SCORE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
CONFIDENCE_THRESHOLD = 0.4

yolo_path = "./yolo_v5"
path = "./"

client = Client(AccountSID, AuthToken)

def sendMessage(client_num, message):
    client.messages.create(
        body=message,
        from_=+17473610732,
        to='+91'+client_num
    )

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/detected_obj", methods=["POST"])
def obj_det():
    model_name = "yolov5s.onnx"
    net = build_model(yolo_path, model_name)
    image = request.files["file"].read()
    image = Image.open(io.BytesIO(image))
    npimg = np.array(image)
    image = npimg.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    labelsPath = "classes.txt"
    class_list = load_classes(labelsPath)

    inputImage = format_yolov5(image)
    res, laptop_widths = get_prediction(inputImage, net, class_list)
    if laptop_widths:
        res += ' at distance '
        ref_image = cv2.imread(os.path.join(path,"calibration", "Ref_image.png"))
        _, ref_image_laptop_width = get_prediction(ref_image, net, class_list)
        focal_length_found = focal_length_finder(Known_distance, Known_width, ref_image_laptop_width[0])
        for laptop_width in laptop_widths:
            distance = distance_finder(focal_length_found, Known_width, laptop_width)
        res = res + '{:.2f} centimeters'.format(distance)
    return res

@app.route("/detected_txt", methods=["POST"])
def txt_det():
    image = request.files["file"].read()
    image = Image.open(io.BytesIO(image))
    npimg = np.array(image)
    image = cv2.cvtColor(npimg, cv2.COLOR_BGR2RGB)

    if not os.path.exists("static"):
        os.makedirs("static")

    # Save the captured image
    cv2.imwrite("static/captured_textimg.jpg", image)

    
    result = extract_text(image)
    return "The following text was detected. " + result
    
    

@app.route("/currency", methods=["POST"])
def currency():
    image = request.files["file"].read()
    image = Image.open(io.BytesIO(image))
    npimg = np.array(image)
    image = npimg.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Make sure the 'static' folder exists
    if not os.path.exists("static"):
        os.makedirs("static")

    # Save the captured image
    cv2.imwrite("static/captured_currency.jpg", image)

    res = predict_currency(image)
    response= f"{res} rupees"
    return response


@app.route("/sos", methods=["POST"])
def sos():
    data = json.loads(request.data)
    numbers = data.get('data', [])  
    message = data.get('message', "SOS EMERGENCY FROM BLIND PERSON")

    for num in numbers:
        sendMessage(num, message)

    return "Success"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)