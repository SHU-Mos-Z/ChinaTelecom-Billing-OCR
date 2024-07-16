import pytesseract
from PIL import Image
import cv2
import re
import numpy as np
from pyzbar import pyzbar

pytesseract.pytesseract.tesseract_cmd = r"./Tesseract/tesseract.exe"


def process_saved_photo(image_path):
    text = detect_text(image_path)
    keyword = "餐饮"
    reimbursement_type = "餐饮" if keyword in text else "非餐饮"
    # 提取所有金额并转换为浮点数
    prices = re.findall(r'¥?(\d+(?:,\d{3})*\.\d{2})', text)
    prices = [float(price.replace(',', '')) for price in prices]
    print(prices)
    # 将价格列表按降序排序
    sorted_prices = sorted(prices, reverse=True)
    # 分别将最大的和第二大的金额赋值给 total_tax 和 total
    total_tax = format_price(sorted_prices[0]) if len(sorted_prices) > 0 else None
    if len(sorted_prices) > 0:
        sorted_prices.pop(0)
    total = format_price(sorted_prices[0]) if len(sorted_prices) > 0 else None
    if len(sorted_prices) > 0:
        sorted_prices.pop(0)
    cost = ''
    combs = find_combinations(sorted_prices, float(total))
    if len(combs) > 0:
        for single_cost in combs[0]:
            cost += (str(single_cost) + ',')
    ids = re.findall(r'\b\d\w{17}\b', text)
    seller_id = [id_ for id_ in ids if id_ != '91310115671143758E']
    buyer_id = [id_ for id_ in ids if id_ not in seller_id]
    if not seller_id:
        seller_id = ['']
    if not buyer_id:
        buyer_id = ['91310115671143758E']
    username = extract_chinese_characters(image_path)
    invoice_date = extract_date(text)
    invoice_id = ''
    for qr_result in str(extract_qr_code_data(image_path)).split(','):
        if qr_result.startswith('243') or qr_result.startswith('031'):
            invoice_id = qr_result
            break
    return {
        'invoice_id': invoice_id,  # 发票代码
        'invoice_date': invoice_date,  # 开票时间
        'buyer_id': buyer_id[0],  # 购买方代码
        'seller_id': seller_id[0],  # 销售方代码
        'username': username,  # 开票人
        'reimbursement_type': reimbursement_type,  # 开票类型 餐饮或者非餐饮
        'cost': cost,  # 发票上每一条的金额，逗号隔开
        'total': total,  # 金额总额
        'total_tax': total_tax  # 含税金额总额
    }


def read_image_with_chinese_path(file_path):
    image = Image.open(file_path)
    image_np = np.array(image)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return image_cv


def extract_qr_code_data(image_path):
    img = read_image_with_chinese_path(image_path)
    barcodes = pyzbar.decode(img)
    qr_data = [barcode.data.decode("utf-8") for barcode in barcodes if barcode.type == "QRCODE"]
    if qr_data:
        invoice_id = max(qr_data, key=len)
        return invoice_id
    return None


def extract_date(text):
    date_pattern = r'\d{4}年\d{2}月\d{2}日'
    matches = re.findall(date_pattern, text)
    if matches:
        date_str = matches[-1]
        # 转换为标准日期格式 "YYYY-MM-DD"
        year = date_str[:4]
        month = date_str[5:7]
        day = date_str[8:10]
        invoice_date = f"{year}-{month}-{day}"
        return invoice_date
    return None


def extract_chinese_characters(filename):
    return ''.join(re.findall(r'[\u4e00-\u9fff]+', filename))


def format_price(price):
    return '{:,.2f}'.format(price)


def detect_text(image_path):
    img = read_image_with_chinese_path(image_path)
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    return text


def find_combinations(nums, target):
    results = []
    nums.sort()

    def backtrack(start, path, target_):
        if target_ == 0:
            results.append(path[:])
            return
        if target_ < 0:
            return
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            backtrack(i + 1, path, target_ - nums[i])
            path.pop()
    backtrack(0, [], target)
    return results
