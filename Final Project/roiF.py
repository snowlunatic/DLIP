# ============================================================= #
# Librarian assistant system (DLIP final project)
# Desc:     ROI functions and text detection
# Name:     Soonho Lim, Duwon Yang
# Date:     06-24-2024
# laguage:  python (3.9.18), opencv-python (4.7.0)
# ============================================================= #

import cv2
import numpy as np
from ultralytics import YOLO
from google.cloud import vision
import os
import re

# Google Cloud Vision API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Program Files/Tesseract-OCR/divine-outlet-426513-u1-80cea1380925.json"

def detect_text(image):
    client = vision.ImageAnnotatorClient()

    success, encoded_image = cv2.imencode('.jpg', image)
    if not success:
        raise RuntimeError("Failed to encode image")

    content = encoded_image.tobytes()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors')

    return [(text.description, text.bounding_poly) for text in texts]

def is_point_in_box(point, box):
    # Unpack the coordinates of the box
    x1, y1, x2, y2 = box
    # Unpack the coordinates of the point
    px, py = point
    # Check if the point is within the bounds of the box
    return x1 <= px <= x2 and y1 <= py <= y2



def set_roi(image, result, threshold=0.6):
    roi_info = []
    for r in result:
        book = 0
        boxes = r.boxes
        centerPoints = []
        valid_boxes = []

        # Process each detected box
        for box in boxes:
            confidence = box.conf[0]
            if confidence > threshold:  # Filter by confidence score
                class_id = int(box.cls)
                if class_id == 73:  # Check if the class is "book"
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    centerPoint = (int((x2 - x1) // 2 + x1), int((y2 - y1) // 2 + y1))
                    centerPoints.append(centerPoint)
                    valid_boxes.append((x1, y1, x2, y2, centerPoint))
        
        # Check if boxes overlap
        for i, (x1, y1, x2, y2, centerPoint) in enumerate(valid_boxes):
            count = sum(is_point_in_box(cp, (x1, y1, x2, y2)) 
                        for j, (cx1, cy1, cx2, cy2, cp) in enumerate(valid_boxes) if i != j)
            if count < 2:  # If not overlapping with more than one box
                book += 1
                roi = image[y1:y2, x1:x2]  # Extract the ROI from the image
                roi_info.append((x1, y1, x2, y2, roi))  # Add ROI info to the list
        
        # Sort ROIs by the x-coordinate of the bounding boxes
        roi_info.sort(key=lambda x: x[0])

    final_roi_info = []
    # Process ROI information
    for idx, (x1, y1, x2, y2, roi) in enumerate(roi_info):
        roi_number = idx + 1
        height = y2 - y1
        new_height = height // 4

        # Select the bottom quarter of the ROI
        sub_y1 = y1 + 3 * new_height
        sub_y2 = y2
        sub_roi = image[sub_y1:sub_y2, x1:x2]

        # Divide the selected part into top and bottom halves
        sub_height = sub_y2 - sub_y1
        mid_y = sub_y1 + sub_height // 2

        # Use only the upper part
        upper_roi = image[sub_y1-20:mid_y, x1:x2]
        final_roi_info.append((x1, sub_y1, x2, mid_y, upper_roi, roi_number))

    # Sort final ROI by the x-coordinate
    final_roi_info.sort(key=lambda x: x[0])
    
    return roi_info, final_roi_info



def text_detect(final_roi_info):
    roi_number = 0
    detected_texts = []
    text = [] 
    text_result = [] 

    for textd in final_roi_info:
        x1, sub_y1, x2, mid_y, roi_image, _ = textd
        # Convert the ROI image to grayscale
        gray_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
        # Apply binary thresholding to the grayscale image
        _, thresh = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY)
        # Detect text from the thresholded image
        detected_texts_list = detect_text(thresh)  # Assume detect_text returns a list of tuples
        # Extract only the text parts from the detection results
        detected_texts_only = [text for text, _ in detected_texts_list]
        # Filter out non-English and non-numeric characters except '.'
        filtered_texts_only = []
        for t in detected_texts_only:
            filtered_text = re.sub(r'[^a-zA-Z0-9.\s]', '', t)
            if filtered_text.strip():  # Add only if there is remaining text
                filtered_texts_only.append(filtered_text)
        detected_texts.append((filtered_texts_only, roi_number))
        
        if filtered_texts_only:
            filtered_text = filtered_texts_only[0]
            # Further split by '\n' and filter out chunks with two or more consecutive letters
            chunks = filtered_text.split('\n')
            valid_chunks = [chunk for chunk in chunks if not re.search(r'[a-zA-Z]{2,}', chunk)]
            # Join valid chunks back with '\n'
            final_text = '\n'.join(valid_chunks)
            # Remove leading non-numeric characters and leading \n and spaces from the first chunk
            if final_text:
                cleaned_final_text = re.sub(r'^[^\d\n]*', '', final_text).lstrip()
                lines = cleaned_final_text.split('\n')
                category = lines[0] if len(lines) > 0 else ""
                sub_alpha = ""
                sub_category = ""
                year = lines[2] if len(lines) > 2 else ""
                # If there is a second line, process it
                if len(lines) > 1:
                    second_line = lines[1]
                    # Remove leading '.' from the second line
                    if second_line.startswith('.'):
                        second_line = second_line[1:]
                    # Split alpha and numeric parts in the second line
                    parts = re.findall(r'[^\W\d_]+|\d+', second_line)
                    if len(parts) > 0:
                        sub_alpha = parts[0]  # First part is alpha
                    if len(parts) > 1:
                        sub_category = parts[1]  # Second part is numeric

                # Post-process category to remove leading zeros and convert to float
                if category:
                    category = re.sub(r'^0+', '', category)
                    category = float(category) if category else 0.0

                # Post-process sub_category to int and adjust to 3 digits
                if sub_category:
                    sub_category = int(sub_category)
                    if sub_category < 10:
                        sub_category *= 100
                    elif sub_category < 100:
                        sub_category *= 10

                # Post-process year to int
                if year:
                    year = int(year)

                text.append([cleaned_final_text])
                text_result.append({
                    "book_number": roi_number,
                    "category": category,
                    "sub_alpha": sub_alpha,
                    "sub_category": sub_category,
                    "year": year
                })
        roi_number += 1

    return text_result