import cv2
import numpy as np
import pytesseract
from localize import lang

class RecognizedResult:
    def __init__(self, image, processed_image, text, timestamp, seq_id):
        self.image = image
        self.processed_image = processed_image
        self.text = text
        self.timestamp = timestamp
        self.seq_id = seq_id


class CombatLogOCR:
    def __init__(self, tesseract_cmd, tesseract_config, extract_color_ranges, language, resize_factor=2, resize_interpolation=cv2.INTER_NEAREST_EXACT):
        self.color_ranges = extract_color_ranges
        self.tesseract_cmd = tesseract_cmd
        self.tesseract_config = tesseract_config
        self.language = language
        self.langset = lang.get(language, lang['en'])
        self.resize_factor = resize_factor
        self.resize_interpolation = resize_interpolation

        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd


    def handle(self, image, timestamp, seq_id):
        processed = self._preprocess_image(image)
        try:
            text = pytesseract.image_to_string(processed, config=self.tesseract_config, lang=self.langset['ocr_lang'])
        except pytesseract.TesseractError as e:
            print(f"OCR Error: {e}")
            text = ""
        return RecognizedResult(image, processed, text, timestamp, seq_id)


    def _preprocess_image(self, image):
        resized = cv2.resize(image, None, fx=self.resize_factor, fy=self.resize_factor, interpolation=self.resize_interpolation)
        extracted = self._extract_multi_color_text(resized, self.color_ranges)
        return extracted


    def _extract_multi_color_text(self, image, color_ranges):
        combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for lower, upper in color_ranges:
            mask = cv2.inRange(image, np.array(lower), np.array(upper))
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        result = cv2.bitwise_and(image, image, mask=combined_mask)
        return result

