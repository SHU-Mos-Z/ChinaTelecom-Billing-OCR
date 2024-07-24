import cv2
import numpy as np
import fitz  # PyMuPDF


def detect_seal_in_pdf(pdf_path_: str) -> bool:
    """
    检测PDF文件中的公章是否存在。

    :param pdf_path_: PDF文件路径
    :return: 是否存在公章（True/False）
    """
    # 将PDF转换为图像
    doc = fitz.open(pdf_path_)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # 处理RGBA图像
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        images.append(img)

    # 检查每一页是否有公章
    for img in images:
        if detect_ellipse(img):
            return True
    return False


def detect_ellipse(image: np.ndarray) -> bool:
    """
    检测图像中是否有椭圆形区域（公章）。

    :param image: 输入图像（RGB）
    :return: 是否存在椭圆形区域（True/False）
    """
    # 把印刷文字过滤掉了
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((5, 5), np.uint8)
    morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    # 检测边缘
    edges = cv2.Canny(morph, 50, 150)

    # 显示边缘检测后的图像，调试用的，注释掉就行
    # cv2.imshow("边缘", edges)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 检测椭圆形状的轮廓
    for cnt in contours:
        if len(cnt) >= 5:
            ellipse = cv2.fitEllipse(cnt)
            (center, axes, orientation) = ellipse
            major_axis_length = max(axes)
            minor_axis_length = min(axes)
            aspect_ratio = major_axis_length / minor_axis_length
            if 1.2 <= aspect_ratio <= 2.5:
                return True
    return False


# 接口供其他脚本调用
def check_seal_in_invoice(pdf_path_: str) -> bool:
    """
    检查PDF电子发票中是否有公章。

    :param pdf_path_: PDF文件路径
    :return: 是否存在公章（True/False）
    """
    return detect_seal_in_pdf(pdf_path_)


if __name__ == "__main__":
    pdf_path = "F:/Test/ocr-request1/test-pdf/付致宁-69.00-2.pdf"
    result = check_seal_in_invoice(pdf_path)
    print("是否存在公章:", result)
