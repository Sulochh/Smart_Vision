import os
import cv2
import numpy as np
import mahotas
import pickle
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Constants
BOVW = "./currency_model/bovw_codebook_600.pickle"  # Path to BOVW codebook
IMG_SIZE = 320  # Standard image size to resize to
DATASET_PATH = './dataset-training'  # Path to your training dataset

# Function to extract Hu Moments
def fd_hu_moments(image):
    if image is None or image.size == 0:
        print("Warning: Empty image passed to Hu Moments.")
        return np.zeros(7)  # Return zero vector if image is empty

    # Convert image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    moments = cv2.moments(image)
    feature = cv2.HuMoments(moments).flatten()
    
    # Check Hu moments output length
    if feature.shape[0] != 7:
        print(f"Warning: Hu Moments returned {feature.shape[0]} values, expected 7.")
        feature = np.zeros(7)  # Return zero vector if Hu Moments don't have 7 values
    
    return feature

# Function to extract Haralick Texture Features
def fd_haralick(image):
    if image is None or image.size == 0:
        print("Warning: Empty image passed to Haralick.")
        return np.zeros(13)  # Return zero vector if image is empty
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    haralick = mahotas.features.haralick(gray).mean(axis=0)
    return haralick

# Function to extract Color Histogram Features
def fd_histogram(image):
    if image is None or image.size == 0:
        print("Warning: Empty image passed to Histogram.")
        return np.zeros(8 * 8 * 8)  # Return zero vector if image is empty
    
    # Convert image to HSV
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    bins = 8
    hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

# Function to extract BOVW (Bag of Visual Words) Features
def feature_extract(im):
    if im is None or im.size == 0:
        print("Warning: Empty image passed to BOVW.")
        return np.zeros(600)  # Return zero vector if image is empty
    
    pickle_in = open(BOVW, "rb")
    dictionary = pickle.load(pickle_in)
    sift2 = cv2.SIFT_create()
    bowDiction = cv2.BOWImgDescriptorExtractor(sift2, cv2.BFMatcher(cv2.NORM_L2))
    bowDiction.setVocabulary(dictionary)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    feature = bowDiction.compute(gray, sift.detect(gray))
    return feature.squeeze() if feature is not None else np.zeros(600)

# Function to extract all features from an image
def extract_features(image):
    Hu = fd_hu_moments(image)
    Harl = fd_haralick(image)
    Hist = fd_histogram(image)
    Bovw = feature_extract(image)
    
    # Combine all features into a single vector
    mfeature = np.hstack([Hu, Harl, Hist, Bovw])
    return mfeature

# Load dataset and extract features
def load_data(dataset_path):
    features = []
    labels = []
    for label_dir in os.listdir(dataset_path):
        label_path = os.path.join(dataset_path, label_dir)
        if os.path.isdir(label_path):
            for image_name in os.listdir(label_path):
                image_path = os.path.join(label_path, image_name)
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Warning: Failed to load image {image_path}")
                    continue
                image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))  # Resize image to standard size
                feature = extract_features(image)
                features.append(feature)
                labels.append(label_dir)  # Use the folder name as label
    return np.array(features), np.array(labels)

# Train the Random Forest model
def train_model(dataset_path):
    print("Loading dataset and extracting features...")
    X, y = load_data(dataset_path)
    
    if len(X) == 0 or len(y) == 0:
        print("No valid data found for training.")
        return
    
    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Save the trained model to a file
    joblib.dump(clf, './currency_model/rfclassifier_model.pkl')
    print("Model trained and saved!")


# Test the trained model
def predict_currency(image):
    # image is already passed as a NumPy array
    image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))  # Resize image to standard size
    
    # Extract features from the image
    feature = extract_features(image)
    
    if feature is None:
        return "Feature extraction failed"
    
    # Load the trained classifier model
    clf = joblib.load('./currency_model/rfclassifier_model.pkl')
    
    # Perform prediction
    prediction = clf.predict([feature])
    
    return prediction[0]


# Uncomment below to train the model (comment out if just predicting)
#train_model(DATASET_PATH)

# Test prediction (add path to a test image in your dataset)
#print(predict_currency('./rupee1.jpg'))
