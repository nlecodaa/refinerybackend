import os
import cv2
import fitz  
import numpy as np
import pytesseract
import argparse
import shutil

# Check if Tesseract is available
if shutil.which("tesseract") is None:
    raise EnvironmentError("❌ Tesseract is not installed or not in PATH.")

# PDF to image conversion
def pdf_page_to_image(page, dpi=300):
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Image preprocessing
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

# OCR execution
def ocr(img, lang='eng', psm=6, oem=3):
    config = f'--oem {oem} --psm {psm}'
    return pytesseract.image_to_string(img, lang=lang, config=config)

# Final function to be imported in api.py
def preprocess_image(image_path, lang='eng', save_preproc=False):
    base, ext = os.path.splitext(image_path)

    if ext.lower() == '.pdf':
        doc = fitz.open(image_path)
        full_text = []
        for i, page in enumerate(doc, 1):
            img = pdf_page_to_image(page)
            prep = preprocess(img)
            if save_preproc:
                out_path = f"{base}_page{i:03d}_prep.png"
                cv2.imwrite(out_path, prep)
            full_text.append(ocr(prep, lang))
        return '\n'.join(full_text)
    
    else:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f'Could not read image: {image_path}')
        prep = preprocess(img)
        if save_preproc:
            out_path = f"{base}_prep.png"
            cv2.imwrite(out_path, prep)
        return ocr(prep, lang)

# CLI entry point for standalone usage
def main():
    ap = argparse.ArgumentParser(description='Minimal OCR pipeline for images and PDFs')
    ap.add_argument('input', help='PDF or image file')
    ap.add_argument('-l', '--lang', default='eng', help='Tesseract language(s), e.g. "eng+deu"')
    ap.add_argument('-o', '--output', help='Optional output text file')
    ap.add_argument('--save-preproc', action='store_true', help='Save preprocessed images')
    args = ap.parse_args()

    text = preprocess_image(args.input, args.lang, args.save_preproc)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)

if __name__ == '__main__':
    main()
