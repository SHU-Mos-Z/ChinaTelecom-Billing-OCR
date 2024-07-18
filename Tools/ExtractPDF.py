import fitz
import re
from typing import List


def process_saved_pdf(file_dir):
    if file_dir.endswith(".pdf"):
        pdf_document = fitz.open(file_dir)
        username = extract_chinese_characters(file_dir)
        invoice_id = ''
        invoice_date = ''
        buyer_id = ''
        seller_id = ''
        reimbursement_type = ''
        cost = ''
        tax = ''
        total = 0.0
        total_tax = 0.0
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text()
            phrases = extract_phrases(list(page_text.strip()))  # 扫描的文字结果提取为短语列表
            print(phrases)
            service_money = extract_percent_with_nearby_numbers(data=phrases)  # 找出全部百分比字符串附近的数字
            service_text = extract_percent_with_nearby_text(data=phrases)  # 找出距离百分比字符串最近的非数字的字符串
            for phrase in phrases:
                if phrase.startswith('243') or phrase.startswith('031'):
                    invoice_id = phrase
            for money_list, text_near_percentage in zip(service_money, service_text):
                if '餐' in text_near_percentage:
                    reimbursement_type += '餐饮,'
                else:
                    reimbursement_type += '非餐饮,'
                cost += (max(money_list) + ',')
                tax += (min(money_list) + ',')
                total += float(max(money_list))
                total_tax += (float(max(money_list)) + float(min(money_list)))
            date = extract_date(page_text)
            if date and date is not None:
                invoice_date = date
            ids = re.findall(r'\b9\w{17}\b', page_text)
            for i, id_ in enumerate(ids):
                if i == 0:
                    buyer_id = id_
                else:
                    seller_id = id_
        return {
            'invoice_id': invoice_id,  # 发票代码
            'invoice_date': invoice_date,  # 开票时间
            'buyer_id': buyer_id,  # 购买方代码
            'seller_id': seller_id,  # 销售方代码
            'username': username,  # 开票人
            'reimbursement_type': reimbursement_type,  # 开票类型 餐饮或者非餐饮
            'cost': cost,  # 发票上每一条的金额，逗号隔开
            'total': total,  # 金额总额
            'total_tax': total_tax  # 含税金额总额
        }

    else:
        return {
            'invoice_id': None,
            'invoice_date': None,
            'buyer_id': None,
            'seller_id': None,
            'username': None,
            'reimbursement_type': None,
            'cost': None,
            'total': None,
            'total_tax': None
        }


def extract_percent_with_nearby_numbers(data):
    result = []
    i = 0
    n = len(data)
    while i < n:
        if '%' in data[i]:
            nearby_numbers = []
            j = i - 1
            while j >= 0 and '.' in data[j]:
                if float(data[j]).is_integer() and float(data[j]) <= 10:
                    j -= 1
                    continue
                nearby_numbers.insert(0, data[j])
                print(data[j])
                j -= 1
            k = i + 1
            while k < n and '.' in data[k]:
                if float(data[k]).is_integer() and float(data[k]) <= 10:
                    k += 1
                    continue
                nearby_numbers.append(data[k])
                print(data[k])
                k += 1
            result.append(nearby_numbers)
        i += 1
    return result


def extract_percent_with_nearby_text(data):
    result = []
    n = len(data)
    for i in range(n):
        if '%' in data[i]:
            front_idx = i - 1
            back_idx = i + 1
            while front_idx > 0:
                if '.' in data[front_idx] or any(c.isdigit() for c in data[front_idx]):
                    front_idx -= 1
                else:
                    break
            while back_idx < n - 1:
                if '.' in data[front_idx] or any(c.isdigit() for c in data[front_idx]):
                    back_idx += 1
                else:
                    break
            if i - front_idx > back_idx - i:
                if not ('.' in data[back_idx] or any(c.isdigit() for c in data[back_idx])):
                    result.append(data[back_idx])
                else:
                    result.append(data[front_idx])
            else:
                if not ('.' in data[front_idx] or any(c.isdigit() for c in data[front_idx])):
                    result.append(data[front_idx])
                else:
                    result.append(data[back_idx])
    return result


def extract_phrases(data: List[str]):
    result = []
    current_number = []
    for element in data:
        if element.isdigit() or element == '.' or element.isalpha() or element == '%' or element == '-':
            current_number.append(element)
        else:
            if current_number:
                result.append(''.join(current_number))
                current_number = []
    if current_number:
        result.append(''.join(current_number))
    return result


# def extract_around_percentage_context(data: List[str], context_length=5):
#     result = []
#     percentage_indices = [i for i, element in enumerate(data) if '%' in element]
#     last_idx = None
#     for idx in percentage_indices:
#         idx_ = idx - 1
#         while '.' in data[idx_] and idx_ > idx - 3:
#             idx_ -= 1
#         if not any(char.isdigit() for char in data[idx_]):
#             idx_ += 1
#         if last_idx is None:
#             context = data[max(0, idx - context_length, idx_ - 1): idx + 2]
#         else:
#             context = data[max(last_idx + 2, idx - context_length, idx_ - 1): idx + 2]
#         result.append(context)
#         last_idx = idx
#
#     return result


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
