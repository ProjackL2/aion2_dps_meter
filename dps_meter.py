import queue
import threading
import time

from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from combat_log_ocr import CombatLogOCR
from combat_log_processor import CombatLogParser
from damage_calculator import DamageCalculator
from screen_capturer import ScreenCapturer, Capture
from utils import images_not_similar
from plotter import Plotter
from localize import lang

extract_color_ranges = [
    # White text (normal text)
    ([182, 144, 100], [255, 200, 140]),
    # Orange text (values and names)
    ([170, 105, 32], [255, 160, 51]),
    # Red text (damage text)
    ([100, 26, 10], [195, 31, 31]),
    # Blue text (skills)
    ([14, 85, 134], [16, 152, 248]),
    # Green text (regeneration)
    ([59, 93, 0], [129, 202, 1]),
    # Warn text
    ([135, 37, 37], [253, 87, 87]),
]

class DPSMeter:
    def __init__(self, config):
        tesseract_cmd = config.get('ocr', 'tesseract_cmd')
        tesseract_config = config.get('ocr', 'tesseract_config')
        ocr_thread_count = int(config.get('ocr', 'thread_count'))

        capture_fps = int(config.get('capture', 'fps'))
        capture_region_x = int(config.get('capture', 'region_x'))
        capture_region_y = int(config.get('capture', 'region_y'))
        capture_region_width = int(config.get('capture', 'region_width'))
        capture_region_height = int(config.get('capture', 'region_height'))
        
        language = config.get('language', 'lang')
        if language not in lang:
            #if language is not within supported languages, default to english
            print(f"[Warning] Language '{language}' not supported. Defaulting to English ('en').")
            language = 'en'

        save_combat_log = config.get('debug', 'save_combat_log') == "1"
        ignored_log = config.get('debug', 'ignored_log') == "1"
        damage_log = config.get('debug', 'damage_log') == "1"
        ocr_view = config.get('debug', 'ocr_view') == "1"

        self.running = threading.Event()
        self.running.set()
        self.capture_fps_delay = 1.000 / float(capture_fps)
        self.ocr_view = ocr_view
        self.snapshot_queue = queue.Queue()
        self.ocr_executor = ThreadPoolExecutor(max_workers=ocr_thread_count)
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.analyze_thread = threading.Thread(target=self._analyze_loop)

        self.screen_capturer = ScreenCapturer(x=capture_region_x,
                                              y=capture_region_y,
                                              width=capture_region_width,
                                              height=capture_region_height)

        self.ocr = CombatLogOCR(tesseract_cmd=tesseract_cmd,
                                tesseract_config=tesseract_config,
                                extract_color_ranges=extract_color_ranges,
                                language=language,
                                resize_factor=2,
                                resize_interpolation=cv2.INTER_NEAREST_EXACT)

        self.parser = CombatLogParser(language=language)
        self.parser.set_debug(damage_log, ignored_log)
        self.parser.set_write_log(save_combat_log)

        self.dps_meter = DamageCalculator(language=language)

        self.plotter = Plotter(self.dps_meter, language, max_points=100)


    def run(self):
        self.analyze_thread.start()
        self.capture_thread.start()

        self.plotter.run_blocking()

        self.running.clear()

        self.capture_thread.join()
        self.ocr_executor.shutdown(wait=True)
        self.analyze_thread.join()


    def _capture_loop(self):
        sequential_id = 0
        prev_capture = self.screen_capturer.capture()
        while self.running.is_set():
            capture = self.screen_capturer.capture()

            # do not process the same images
            if images_not_similar(prev_capture.image, capture.image):
                self.ocr_executor.submit(self._handle_screenshot, capture, sequential_id)
                sequential_id += 1

            prev_capture = capture
            time.sleep(self.capture_fps_delay)


    def _handle_screenshot(self, capture: Capture, seq_id):
        snapshot = self.ocr.handle(capture.image, capture.timestamp, seq_id)
        self.snapshot_queue.put(snapshot)


    def _analyze_loop(self):
        next_seq = 0
        buffer = {}
        while self.running.is_set() or not self.snapshot_queue.empty():
            try:
                snapshot = self.snapshot_queue.get(block=True, timeout=10)
            except queue.Empty:
                continue

            # coz of multithreaded ocr processing we need to order results
            buffer[snapshot.seq_id] = snapshot

            while next_seq in buffer:
                next_snapshot = buffer.pop(next_seq)
                next_seq += 1

                if self.ocr_view:
                    vis_frame = self._create_debug_frame(next_snapshot.image, next_snapshot.processed_image, next_snapshot.text)
                    cv2.imshow('OCR Visualize', vis_frame)
                    cv2.waitKey(1)

                damage_list = self.parser.parse_combat_log(next_snapshot.text, next_snapshot.timestamp, next_snapshot.seq_id)
                self.dps_meter.process_damage(damage_list, next_snapshot.timestamp)

            if self.snapshot_queue.qsize() > 100:
                print("Queue size:", self.snapshot_queue.qsize())
        if self.ocr_view:
            cv2.destroyAllWindows()


    def _create_debug_frame(self, original, processed, ocr_text):
        h, w = original.shape[:2]
        display_h = 600
        scale = display_h / h
        display_w = int(w * scale)

        text_canvas = np.zeros((display_h, display_w, 3), dtype=np.uint8)
        original_display = cv2.resize(original, (display_w, display_h))
        processed_display = cv2.resize(processed, (display_w, display_h))

        for i, line in enumerate(ocr_text.split('\n')):
            y = 12 + (i * 12)
            cv2.putText(text_canvas, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

        combined = np.hstack([original_display, processed_display, text_canvas])

        return combined
