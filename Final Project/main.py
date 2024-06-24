# ============================================================= #
# Librarian assistant system (DLIP final project)
# Desc:     main source code
# Name:     Soonho Lim, Duwon Yang
# Date:     06-24-2024
# laguage:  python (3.9.18), opencv-python (4.7.0)
# ============================================================= #

import cv2
from ultralytics import YOLO
import roiF as roi
import op1F as op1
import op2F as op2

# Load YOLO model
model = YOLO('yolov8x.pt')
image_path = 'sample_image/Wrong_Sub_Category.jpg'

# Read image
image = cv2.imread(image_path)

# Check if the image is loaded correctly
if image is None:
    raise FileNotFoundError(f"Image not found at {image_path}")

cv2.namedWindow("or", cv2.WINDOW_NORMAL)
cv2.imshow("or", image)

# Perform object detection on the image
result = model.predict(source=image, save=True, save_txt=True)

# Process ROI (Region of Interest)
roi_info, final_roi_info = roi.set_roi(image, result, 0.5)

# =================== when validation =================== #
idx = 0
for r in final_roi_info:
    _,_,_,_,roii,_= r
    cv2.namedWindow(f"ROI {idx}", cv2.WINDOW_NORMAL)
    cv2.imshow(f"ROI {idx}", roii)
    idx +=1

# ======================================================= #

# Text detection
text_result = roi.text_detect(final_roi_info)

#text_result[5]['sub_alpha'] = 'A'
# Print detected text results
for i, result in enumerate(text_result):
    print(f"Entry {i}: {result}")
cv2.waitKey(0)

# Option selection for further processing
print("Option 1 for finding book\nOption 2 for arranging misplaced book")
option = int(input("Press '1' for option 1, press '2' for option 2: "))

OPchoice = False

if option == 1:
    OPchoice = True
elif option == 2:
    OPchoice = False
else:
    pass

# ==================== option 1 program ==================== # 
if OPchoice:
    # Execute option 1 function
    image = op1.finding_book(image, text_result, roi_info)

# ==================== option 2 program ==================== # 
else:
    # Find books that do not belong
    dif_cat, major_category, major_alpha = op2.find_notBelong(text_result)
    print("different category", dif_cat)
    if dif_cat:
        # draw box in the result image
        image = op2.draw_notBelong(image, roi_info, dif_cat)
  
    # Find books that are not arranged properly
    w_alpha, w_cat, w_year = op2.find_notArranged(text_result, major_category, major_alpha)
    image = op2.draw_notArranged(image, roi_info, text_result, major_alpha, w_alpha, w_cat, w_year)
    # draw arrows and text box in the result image
    image = op2.text_box(image, dif_cat, w_alpha, w_cat, w_year, len(text_result))


    # Print results for option 2
    print("w_alpha", w_alpha)
    print("w_cat", w_cat)
    print("w_year", w_year)
    print("different category", dif_cat)
    print("major alphabet:", major_alpha)

# Display the result image
cv2.namedWindow("result", cv2.WINDOW_NORMAL)
cv2.imshow("result", image)

# Wait for the user to close the window
while True:
    if cv2.waitKey(5) & 0xFF == 27:
        cv2.destroyAllWindows()
        break
