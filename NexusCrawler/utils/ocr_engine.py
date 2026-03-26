# utils/ocr_engine.py
import easyocr
import cv2
import numpy as np

class DropOCR:
    def __init__(self):
        # 初始化 OCR 模型，加载到 GPU (如果有 CUDA) 或 CPU
        self.reader = easyocr.Reader(['ch_sim', 'en'])

    def extract_counts(self, image_path: str):
        """识别图片中的掉落数字"""
        img = cv2.imread(image_path)
        if img is None: return None
        
        # 实际工程建议：根据游戏 UI 比例裁剪出“掉落结果区域” (ROI)
        # 这里先演示全图识别
        results = self.reader.readtext(image_path)
        
        # 逻辑过滤：寻找带有“x”或紧邻物品名称的数字
        parsed_data = {}
        for (bbox, text, prob) in results:
            if prob > 0.5: # 过滤低置信度结果
                print(f"[*] OCR 识别到文本: {text} (置信度: {prob:.2f})")
                # 示例逻辑：如果 text 包含数字，存入结果
                if any(char.isdigit() for char in text):
                    parsed_data[text] = prob
        return parsed_data