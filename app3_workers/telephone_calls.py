import random


def register_call(bitrix_token, user_id, quant):
    """ Регистрирует quant случайных звонков """

    while quant > 0:
        phone_number = '+79999999999'
        call_type = random.randint(1, 2)
        duration = random.randint(30, 150)
        add_call = bitrix_token.call_api_method('telephony.externalcall.register', {
            'USER_ID': user_id,
            'PHONE_NUMBER': phone_number,
            'TYPE': call_type
        })
        end_call = bitrix_token.call_api_method('telephony.externalcall.finish', {
            'CALL_ID': add_call['result']['CALL_ID'],
            'USER_ID': user_id,
            'DURATION': duration
        })
        quant -= 1