import easyocr
import cv2
import matplotlib.pyplot as plt


reader = easyocr.Reader(['en'], gpu=False)

def extract_text(image_np):
    '''Recognize text directly from a NumPy image array'''
    result = reader.readtext(image_np)
    extracted_text = " ".join([text for (_, text, prob) in result if prob > 0.2])
    return extracted_text if extracted_text else "No text found, try again"

# Function to recognize text from an image
def recognize_text(img_path):
    ''' loads an image and recognizes text using EasyOCR '''
    reader = easyocr.Reader(['en'])  # Initialize the reader for English text
    result = reader.readtext(img_path)
    return result

# Function to display the image and overlay detected text
def overlay_ocr_text(img_path):
    ''' loads an image, recognizes text, and overlays it on the image '''
    
    # Load image
    img = cv2.imread(img_path)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Recognize text from image
    result = recognize_text(img_path)
    
    # If OCR prob is above threshold, overlay bounding box and text
    for bbox, text, prob in result:
        if prob >= 0.2:  # You can adjust this threshold as needed
            print(f'Detected text: {text} (Confidence: {prob:.2f})')
            
            # Get the coordinates of the bounding box
            top_left, top_right, bottom_right, bottom_left = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            
            # Draw rectangle around detected text
            cv2.rectangle(img, top_left, bottom_right, (255, 0, 0), 2)
            
            # Put the detected text on the image
            cv2.putText(img, text, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
   
   
    # Save the captured image
    cv2.imwrite("static/overlayed_text.jpg", img)

    # Display the image with bounding boxes and text overlay
    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    plt.axis('off')
    plt.show()

# Path to your image (update this with your image file)
image_path = './b4.jpeg'

# Run the overlay function to display results
overlay_ocr_text(image_path)
