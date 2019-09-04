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
    MANAGEMENT_CODE_DEFAULT = "ABCDE12345F"
    MANAGEMENT_CODE_LENGTH  = 12

    MENU_LUNCH    = 0
    MENU_DINNER   = 1
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

    #Kakao Extra Data
    
    KAKAO_EXTRA_STORE_ID          = 'storeID'
    KAKAO_EXTRA_STORE_NAME        = 'storeName'
    KAKAO_EXTRA_STORE_ADDR        = 'storeAddr'

    KAKAO_EXTRA_MENU_ID           = 'menuID'
    KAKAO_EXTRA_MENU_NAME         = 'menuName'
    KAKAO_EXTRA_MENU_PRICE        = 'menuPrice'
    KAKAO_EXTRA_MENU_DESCRIPTION  = 'menuDescription'
    KAKAO_EXTRA_MENU_CATEGORY     = 'menuCategory'

    KAKAO_EXTRA_SELLING_TIME      = 'sellingTime'

    KAKAO_EXTRA_PICKUP_TIME       = 'pickupTime'
    KAKAO_EXTRA_PICKUP_TIME_VALUE = 'origin'
    

    KAKAO_EXTRA_STATUS        = 'status'
    KAKAO_EXTRA_STATUS_OK     = 0
    KAKAO_EXTRA_STATUS_NOT_OK = 1