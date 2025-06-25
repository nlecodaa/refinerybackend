import pytesseract
import cv2

def extract_text_tesseract(image):
    return pytesseract.image_to_string(image, lang='eng')
