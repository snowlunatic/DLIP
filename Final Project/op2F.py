# ============================================================= #
# Librarian assistant system (DLIP final project)
# Desc:     module for option 2 / finding misplaced book
# Name:     Soonho Lim, Duwon Yang
# Date:     06-24-2024
# laguage:  python (3.9.18), opencv-python (4.7.0)
# ============================================================= #

import cv2
import random
import numpy as np
from collections import Counter
import pandas as pd 

def find_notBelong(text_result):
    # Count the occurrences of each category and sub_alpha in text_result
    category_counts = Counter(result['category'] for result in text_result)
    alphabet_counts = Counter(result['sub_alpha'] for result in text_result)

    # Find the most frequent Category and Alphabet with a frequency of 3 or more
    major_category = max((cat for cat in category_counts if category_counts[cat] >= 3), 
                        key=lambda x: category_counts[x], default=None)
    major_alphabet = max((alpha for alpha in alphabet_counts if alphabet_counts[alpha] >= 3), 
                        key=lambda x: alphabet_counts[x], default=None)

    # Find book_numbers with a different Category value
    dif_cat = [result['book_number'] for result in text_result if result['category'] != major_category]

    return dif_cat, major_category, major_alphabet


def find_notArranged(text_result, major_category, major_alphabet):
    # Initialize lists to store book numbers that are out of order
    w_alpha, w_cat, w_year = [], [], []
    # Initialize previous alpha, category, and year for comparison
    p_alpha, p_cat, p_year = None, None, None

    # Iterate through each text result
    for text in text_result:
        category, alpha, cat, year, book_num = text['category'], text['sub_alpha'], text['sub_category'], text['year'], text['book_number']
        
        # Check if the current category matches the major category
        if category == major_category:
            # Ensure previous values and major_alphabet are available for comparison
            if p_alpha and p_cat and p_year and major_alphabet:
                # Check if the current sub_alpha does not match the major alphabet
                if alpha != major_alphabet:
                    # Exclude the first and last book from the comparison
                    if book_num != text_result[0]['book_number'] and book_num != text_result[len(text_result)-1]['book_number']:
                        w_alpha.append(book_num)

                # Check if the current sub_alpha matches the previous one
                if p_alpha == alpha:
                    # Compare sub_category values
                    if p_cat > cat:
                        w_cat.append(book_num)
                    # If sub_category values are the same, compare year values
                    elif p_cat == cat:
                        if p_year > year:
                            w_year.append(book_num - 1)

        # Update previous values for the next iteration
        p_alpha, p_cat, p_year = alpha, cat, year

    # Return the lists of book numbers that are out of order
    return w_alpha, w_cat, w_year


def draw_arrow(im, book_number, color, roi_point, pos):
    # Get the coordinates of the ROI for the given book number
    x1, y1, x2, y2, cp = roi_point[book_number]

    # Determine the x-location for the arrow based on the position ('front' or 'back')
    if pos == "front":
        x_location = x1
    elif pos == "back":
        x_location = x2

    # Calculate the end point of the arrow
    arrow_end_y = y1 + round((y1 - y2) * 0.1)

    # Draw the arrowed line on the image
    cv2.arrowedLine(im, (x_location, arrow_end_y), (x_location, y1), color, 12, tipLength=0.3)


def Horizontal_arrow(im, book_num, color, roi_point, dir):
    print(book_num)
    # Get the coordinates of the ROI for the given book number
    x1, y1, x2, y2, cp = roi_point[book_num]

    # Initialize start and end points for the arrow
    start_point = None
    end_point = None

    # Calculate the center and width of the box
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    box_width = x2 - x1
    arrow_length = box_width // 3

    # Determine the start and end points for the arrow based on direction
    if dir == "right":
        start_point = center_x + arrow_length
        end_point = center_x
        cv2.arrowedLine(im, (end_point, center_y), (start_point, center_y), color, 15, tipLength=0.5)
    elif dir == "left":
        start_point = center_x
        end_point = center_x - arrow_length
        cv2.arrowedLine(im, (start_point, center_y), (end_point, center_y), color, 15, tipLength=0.5)

    else:
        pass



def draw_notBelong(image, roi_info, dif_cat):
    # Check if there are any book numbers with different categories
    if dif_cat:
        ## Category is different
        # Draw a box and an X mark on the ROI with different category values on the original image
        for roi_count in dif_cat:
            print("roicount", roi_count)
            for x1, y1, x2, y2, roi in roi_info:
                # Check if the current ROI index matches the roi_count
                if roi_info.index((x1, y1, x2, y2, roi)) == roi_count:
                    print(roi_info.index((x1, y1, x2, y2, roi)))
                    # Draw a bounding box around the ROI
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                    # Put a text label "BOOK {roi_count+1}" above the bounding box
                    cv2.putText(image, f"BOOK {roi_count+1}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                    # Draw an X mark over the ROI
                    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                    cv2.line(image, (x2, y1), (x1, y2), (0, 0, 255), 10)

    return image


def draw_notArranged(image, roi_info, text_result, major_alphabet, w_alpha, w_cat, w_year):
    # Draw rectangles and arrows for book numbers that have out-of-order alphabets
    if w_alpha and major_alphabet:
        for count in range(len(w_alpha)):
            x1, y1, x2, y2, cp = roi_info[w_alpha[count]]
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color for category discrepancies
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 10)
            print("alphabet: ", text_result[w_alpha[count]]['sub_alpha'])

            # Determine the direction for the arrow based on the sub_alpha comparison
            if text_result[w_alpha[count]]['sub_alpha'] > major_alphabet:
                dir = "right"
            else:
                dir = "left"
            print("dir: ", dir)
            Horizontal_arrow(image, w_alpha[count], color, roi_info, dir)
    
    # Draw rectangles and arrows for book numbers that have out-of-order categories
    if w_cat:
        count = 0
        for roi_num in w_cat:
            x1, y1, x2, y2, cp = roi_info[w_cat[count]]
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color for category discrepancies
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 10)

            current_item = text_result[roi_num]
            filtered_items = [
                item for item in text_result if
                item['sub_alpha'] == current_item['sub_alpha'] 
            ]
            # Sort filtered items by sub_category
            sort_cat = sorted(filtered_items, key=lambda x: x['sub_category'])
            df = pd.DataFrame(sort_cat)
            print(df)
            position = next((index for index, result in enumerate(sort_cat) if result['book_number'] == roi_num), None)
            print("position:", position)

            if position is not None:
                if position == len(sort_cat) - 1:
                    # If the current item is the last one, use the previous item's ROI number
                    neighbor_position = position - 1
                else:
                    # Otherwise, use the next item's ROI number
                    neighbor_position = position + 1
                
                if neighbor_position >= 0 and neighbor_position < len(sort_cat):
                    neighbor_roi_number = sort_cat[neighbor_position]['book_number']
                    print(f"Current ROI Number: {roi_num}, Neighbor ROI Number: {neighbor_roi_number}")
                    pos = None
                    if roi_num > neighbor_roi_number:
                        pos = "front"
                        print(pos)
                    else:
                        pos = "back"
                        print(pos)
                    draw_arrow(image, neighbor_roi_number, color, roi_info, pos)
            count += 1

    # Draw rectangles and arrows for book numbers that have out-of-order years
    if w_year:
        count = 0
        for roi_num in w_year:
            x1, y1, x2, y2, cp = roi_info[w_year[count]]
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color for year discrepancies
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 10)

            current_item = text_result[roi_num]
            filtered_items = [
                item for item in text_result if
                item['sub_alpha'] == current_item['sub_alpha'] and
                item['sub_category'] == current_item['sub_category'] 
            ]
            # Sort filtered items by year
            sort_year = sorted(filtered_items, key=lambda x: x['year'])
            df = pd.DataFrame(sort_year)
            print(df)
            position = next((index for index, result in enumerate(sort_year) if result['book_number'] == roi_num), None)
            print("position:", position)

            if position is not None:
                if position == len(sort_year) - 1:
                    # If the current item is the last one, use the previous item's ROI number
                    neighbor_position = position - 1
                else:
                    # Otherwise, use the next item's ROI number
                    neighbor_position = position + 1
                
                if neighbor_position >= 0 and neighbor_position < len(sort_year):
                    neighbor_roi_number = sort_year[neighbor_position]['book_number']
                    print(f"Current ROI Number: {roi_num}, Neighbor ROI Number: {neighbor_roi_number}")
                    pos = None
                    if roi_num > neighbor_roi_number:
                        pos = "front"
                        print(pos)
                    else:
                        pos = "back"
                        print(pos)
                    draw_arrow(image, neighbor_roi_number, color, roi_info, pos)
            count += 1

    return image

    
def text_box(image, dif_cat, w_alpha, w_cat, w_year, book):
    # Combine all wrong book numbers into one list and increment by 1 for display
    wrong_books = dif_cat + w_alpha + w_cat + w_year
    wrong_books = [x + 1 for x in wrong_books]
    
    # Get the dimensions of the image
    height, width, _ = image.shape
    
    # Set the messages based on whether there are misplaced books or not
    if wrong_books:
        text2 = "Misplaced book numbers: " + str(wrong_books)
        text3 = "Replace the book following the arrow"
    else:
        text2 = "NO Misplaced Books"
        text3 = "Great job"
    
    # Define the texts to display
    texts = ["Book detected: " + str(book), text2, text3]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    font_color = (255, 255, 255)
    thickness = 5
    
    # Calculate the size of each text and determine the height of the largest text
    text_sizes = [cv2.getTextSize(text, font, font_scale, thickness)[0] for text in texts]
    max_text_height = max([size[1] for size in text_sizes])
    
    # Set the size of the box
    padding = 40
    box_height = height // 10
    box_width = max([size[0] for size in text_sizes]) + padding * 2
    
    # Position the box at the bottom right corner
    top_left = (width - box_width, height - box_height)
    bottom_right = (width, height)
    
    # Draw a black rectangle as the box
    cv2.rectangle(image, top_left, bottom_right, (0, 0, 0), -1)
    
    # Draw each text on the image within the box
    start_y = top_left[1] + padding
    for i, text in enumerate(texts):
        text_size = text_sizes[i]
        text_x = top_left[0] + (box_width - text_size[0]) // 2
        text_y = start_y + i * (max_text_height + padding) + text_size[1]
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)
    
    return image


