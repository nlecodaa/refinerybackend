import pytesseract
import easyocr
import cv2


def extract_text_tesseract(image):
    return pytesseract.image_to_string(image, lang='eng')
reader = easyocr.Reader(['en']) 
def extract_text_easyocr(image_path):
    result = reader.readtext(image_path, detail=0)
    return " ".join(result)
