import os
import base64
from easyofd.ofd import OFD
import pytesseract
from PIL import Image
import cv2
import re
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"./Tesseract/tesseract.exe"


def process_saved_ofd(file_dir, temp_file_folder):
    if file_dir.endswith(".ofd"):
        image_paths = convert_ofd_to_images(ofd_path=file_dir, output_folder=temp_file_folder)
        username = extract_chinese_characters(file_dir)
        found_catering = False
        ocr_text = ""
        for img_path in image_paths:
            ocr_text += detect_text(img_path)
        if "餐饮" in ocr_text or "食品" in ocr_text:
            found_catering = True
        amount, ids = extract_information_ofd(image_paths[0])
        buyer_id = None
        seller_id = None
        invoice_date = extract_date(ocr_text)
        if isinstance(amount, float) and amount < 5:
            amount = extract_amount_from_filename(file_dir)
        for i, id_ in enumerate(ids):
            if i == 0:
                buyer_id = id_
            else:
                seller_id = id_
        reimbursement_type = "餐饮" if found_catering else "非餐饮"
        return [username, reimbursement_type, amount, invoice_date, buyer_id, seller_id]
    else:
        return [None, None, None, None, None, None]


def extract_chinese_characters(filename):
    return ''.join(re.findall(r'[\u4e00-\u9fff]+', filename))


def extract_date(text):
    date_pattern = r'\d{4}年\d{2}月\d{2}日'
    matches = re.findall(date_pattern, text)
    if matches:
        date_str = matches[-1]
        # 转换为标准日期格式 "YYYY-MM-DD"
        year = date_str[:4]
        month = date_str[5:7]
        day = date_str[8:10]
        standard_date = f"{year}-{month}-{day}"
        return standard_date
    return None


def extract_amount_from_filename(filename):
    # 提取文件名中的数字部分作为金额替代值
    matches = re.findall(r'\d+', filename)
    if matches:
        return float(matches[0])
    return None


def detect_text(image_path):
    img = read_image_with_chinese_path(image_path)
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    return text


def extract_information_ofd(image_path):
    text = detect_text(image_path)
    prices = re.findall(r'¥?(\d+(?:,\d{3})*\.\d{2})', text)
    prices = [float(price.replace(',', '')) for price in prices]  # 转换为浮点数并去除千位分隔符
    max_price = max(prices) if prices else None

    ids = re.findall(r'\b9\w{17}\b', text)
    filtered_ids = [id_ for id_ in ids if id_ != '91310115671143758E']
    return max_price, filtered_ids


def convert_ofd_to_images(ofd_path, output_folder):
    try:
        with open(ofd_path, "rb") as f:
            ofdb64 = str(base64.b64encode(f.read()), "utf-8")
            ofd = OFD()
            ofd.read(ofdb64, save_xml=False)
            img_np = ofd.to_jpg()
            ofd.del_data()
            image_paths = []
            for idx, img in enumerate(img_np):
                image_path = os.path.join(output_folder, f"page_{idx}.jpg")
                im = Image.fromarray(img)
                im.save(image_path)
                image_paths.append(image_path)
            return image_paths
    except Exception as e:
        print(f"Error converting OFD to images: {e}")
        return []


def read_image_with_chinese_path(file_path):
    image = Image.open(file_path)
    image_np = np.array(image)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return image_cv
