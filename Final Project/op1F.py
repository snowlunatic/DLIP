# ============================================================= #
# Librarian assistant system (DLIP final project)
# Desc:     module for option 1 / finding book
# Name:     Soonho Lim, Duwon Yang
# Date:     06-24-2024
# laguage:  python (3.9.18), opencv-python (4.7.0)
# ============================================================= #

import cv2

def get_user_input():
    # Prompt user for input and store the responses
    category = float(input("Enter category: "))
    sub_alpha = input("Enter sub alpha: ")
    category_digits = int(input("Enter category digits (three digits): "))
    year = int(input("Enter year: "))
    
    # Return the user input as a dictionary
    return {
        'category': category,
        'sub_alpha': sub_alpha,
        'sub_category': category_digits,
        'year': year
    }


def find_matching_roi_number(user_input, results):
    # Iterate through each result in the list of results
    for result in results:
        # Check if all fields match between user input and result
        if (
            user_input['category'] == result['category'] and
            user_input['sub_alpha'] == result['sub_alpha'] and
            user_input['sub_category'] == result['sub_category'] and 
            user_input['year'] == result['year']
        ):
            # Return the book number if a match is found
            return result['book_number']
    # Return None if no match is found
    return None


def finding_book(image, text_result, roi_info):
    # Get user input for the book search
    user_input = get_user_input()
    # Find the matching ROI number based on user input
    roi_number = find_matching_roi_number(user_input, text_result)

    # Define the dimensions and position for the result display box
    height, width, _ = image.shape
    box_height = height // 10
    box_width = width // 3
    box_start_y = height - box_height
    box_start_x = width - box_width
    box_end_y = height
    box_end_x = width
    # Draw a black rectangle for the result display box
    cv2.rectangle(image, (box_start_x, box_start_y), (box_end_x, box_end_y), (0, 0, 0), -1)

    if roi_number is not None:
        # Print and display the matching book number
        print(f"Matching Book Number: {roi_number + 1}")
        x1, y1, x2, y2, cp = roi_info[roi_number]
        cv2.putText(image, f"BOOK Found {roi_number + 1}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 180, 170), 5)
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 15)
        text = "The Book number is " + str(roi_number + 1)
    else:
        # Print and display message when no matching result is found
        print("No matching result found.")
        text = "No matching Book."

    # Calculate the text size and position for centered alignment in the result display box
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.5
    thickness = 3
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_width, text_height = text_size
    text_x = box_start_x + (box_width - text_width) // 2
    text_y = box_start_y + (box_height + text_height) // 2

    # Add the text to the image
    cv2.putText(image, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

    return image
