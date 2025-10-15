import qrcode, base64
from io import BytesIO

def api_goods_info(but):
    """ Возвращает справочную информацию из api """

    result = {}

    # описание полей товара
    result['goods_fields'] = but.call_list_method("crm.product.fields")
    # список товаров
    result['goods_list'] = but.call_list_method("crm.product.list")

    return result

def generate_qr_code(url):
    """ Генерирует QR-код (возвращает base64-строку) """

    qr = qrcode.make(url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
