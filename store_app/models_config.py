
class Config():
    #STRING LENGTH
    STRING_LENGTH = 255
    WORD_LENGTH   = 32

    DEFAULT_OBJECT_ID = 1

    #PARAMETER
    NOT_APPLICABLE = "N/A"

    #MENU
    MANAGEMENT_CODE_LENGTH = 10

    MENU_LUNCH    = 0
    MENU_DINNER   = 1
    MENU_CATEGORY = [
        ('점심', 'Lunch'),
        ('저녁', 'Dinner'),
    ]

    #ORDERING
    ORDER_STATUS = [
        ('주문 확인중',  '주문 확인중'),
        ('주문 완료',   '주문 완료'),
        ('픽업 준비중',  '픽업 준비중'),
        ('픽업 완료',   '픽업 완료'),
        ('주문 만료',   '주문 만료'),
    ]

    #Kakao Extra Data
    
    KAKAO_EXTRA_STORE_NAME        = 'storeName'
    KAKAO_EXTRA_STORE_ADDR        = 'storeAddr'

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