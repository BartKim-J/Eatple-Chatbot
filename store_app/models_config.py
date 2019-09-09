class Config():
    #SYSTEM
    NOT_APPLICABLE = "N/A"
    DEFAULT_OBJECT_ID = 1

    #USER LENGTH
    USER_NICKNAME_LENGTH = 18
    USER_ID_LENGTH       = 18
    USER_SERIAL_LENGTH   = 12

    #STRING LENGTH
    STRING_LENGTH = 255
    WORD_LENGTH   = 32

    #MENU
    MANAGEMENT_CODE_DEFAULT = "ABCDEF123456"
    MANAGEMENT_CODE_LENGTH  = 12

    MENU_LUNCH    = 0
    MENU_DINNER   = 1
    MENU_CATEGORY_DICT = {'점심': MENU_LUNCH, '저녁': MENU_DINNER}
    MENU_CATEGORY = [
        ('점심', '점심'),
        ('저녁', '저녁'),
    ]

    #ORDERING
    ORDER_STATUS_DICT = {'주문 확인중': 0, '주문완료': 1, '픽업 준비중': 2, '픽업 완료': 3, '주문 만료': 4, '주문 취소': 5}
    ORDER_STATUS = [
        ('주문 확인중',  '주문 확인중'),
        ('주문 완료',   '주문 완료'),
        ('픽업 준비중',  '픽업 준비중'),
        ('픽업 완료',   '픽업 완료'),
        ('주문 만료',   '주문 만료'),
        ('주문 취소',   '주문 취소'),
    ]

    #Kakao Param Data
    KAKAO_PARAM_ORDER_ID          = 'orderID'
    KAKAO_PARAM_USER_ID           = 'userID'
    KAKAO_PARAM_STORE_ID          = 'storeID'
    KAKAO_PARAM_MENU_ID           = 'menuID'

    KAKAO_PARAM_MENU_CATEGORY     = 'menuCategory'
    KAKAO_PARAM_SELLING_TIME      = 'sellingTime'
    KAKAO_PARAM_PICKUP_TIME       = 'pickupTime'

    KAKAO_PARAM_STATUS            = 'status'
    KAKAO_PARAM_STATUS_OK         = True
    KAKAO_PARAM_STATUS_NOT_OK     = False