VALUE_NOT_APPLICABLE = 'N/A'

# Eatplus App Global Defines
STRING_32 = 31
STRING_256 = 255

###########################################################################################

NOT_APPLICABLE = VALUE_NOT_APPLICABLE


# USER LENGTH
USER_NICKNAME_LENGTH = STRING_32
USER_ID_LENGTH = STRING_32
USER_ID_CODE_LENGTH = STRING_256

# PARTNER LENGTH
PARTNER_ID_CODE_LENGTH = STRING_256

# STRING LENGTH
STRING_LENGTH = STRING_256
WORD_LENGTH = STRING_32

# MENU
MANAGEMENT_CODE_DEFAULT = VALUE_NOT_APPLICABLE
MANAGEMENT_CODE_LENGTH = STRING_256

SELLING_TIME_LUNCH = 'lunch'
SELLING_TIME_DINNER = 'dinner'
SELLING_TIME_CATEGORY = [
    (SELLING_TIME_LUNCH, '점심'),
    (SELLING_TIME_DINNER, '저녁'),
]

# IAMPORT
IAMPORT_ORDER_STATUS_PAID = 'paid'
IAMPORT_ORDER_STATUS_CANCELLED = 'cancelled'
IAMPORT_ORDER_STATUS_FAILED = 'failed'
IAMPORT_ORDER_STATUS_READY = 'ready'

IAMPORT_ORDER_STATUS_NOT_PUSHED = 'not_pushed'

IAMPORT_ORDER_STATUS = [
    (IAMPORT_ORDER_STATUS_READY, '미결제'),
    (IAMPORT_ORDER_STATUS_PAID, '결제완료'),
    (IAMPORT_ORDER_STATUS_CANCELLED, '환불/취소'),
    (IAMPORT_ORDER_STATUS_FAILED, '결제실패'),

    (IAMPORT_ORDER_STATUS_NOT_PUSHED, '메뉴 선택중'),
]

# ORDERING
ORDER_STATUS_PAYMENT_CHECK = 0
ORDER_STATUS_ORDER_CONFIRM_WAIT = 1
ORDER_STATUS_ORDER_CONFIRMED = 2
ORDER_STATUS_ORDER_EXPIRED = 3
ORDER_STATUS_ORDER_CANCELED = 4
ORDER_STATUS_PICKUP_PREPARE = 5
ORDER_STATUS_PICKUP_WAIT = 6
ORDER_STATUS_PICKUP_COMPLETED = 7

ORDER_STATUS_ORDER_FAILED = 100
ORDER_STATUS_MENU_CHOCIED = 101

ORDER_STATUS = [
    (ORDER_STATUS_PAYMENT_CHECK, '결제 확인중'),
    (ORDER_STATUS_ORDER_CONFIRM_WAIT, '주문 대기중'),
    (ORDER_STATUS_ORDER_CONFIRMED, '주문 완료'),
    (ORDER_STATUS_ORDER_EXPIRED, '주문 만료'),
    (ORDER_STATUS_ORDER_CANCELED, '주문 취소'),
    (ORDER_STATUS_PICKUP_PREPARE,  '픽업 준비중'),
    (ORDER_STATUS_PICKUP_WAIT,  '픽업 대기중'),
    (ORDER_STATUS_PICKUP_COMPLETED, '픽업 완료'),


    (ORDER_STATUS_ORDER_FAILED, '주문실패'),
    (ORDER_STATUS_MENU_CHOCIED, '메뉴 선택'),
]

# ORDER RECORD
ORDER_RECORD_GET_MENU = 0
ORDER_RECORD_SET_PICKUP_TIEM = 1
ORDER_RECORD_ORDERSHEET_CHECK = 2

ORDER_RECORD_PAYMENT_CONFIRM = 3
ORDER_RECORD_PAYMENT_COMPLETED = 4
ORDER_RECORD_PAYMENT_FAILED = 5
ORDER_RECORD_PAYMENT_CANCELED = 6

ORDER_RECORD_PICKUP_COMPLETED = 7
ORDER_RECORD_TIMEOUT = 10

ORDER_RECORD = [
    (ORDER_RECORD_GET_MENU, '메뉴보기'),
    (ORDER_RECORD_SET_PICKUP_TIEM, '픽업시간 설정'),
    (ORDER_RECORD_ORDERSHEET_CHECK, '주문 확인'),

    (ORDER_RECORD_PAYMENT_CONFIRM, '결제확인'),
    (ORDER_RECORD_PAYMENT_COMPLETED, '결제 완료'),
    (ORDER_RECORD_PAYMENT_FAILED, '결제 실패'),
    (ORDER_RECORD_PAYMENT_CANCELED, '결제 취소'),

    (ORDER_RECORD_PICKUP_COMPLETED, '픽업 완료'),

    (ORDER_RECORD_TIMEOUT, '주문 시간 초과'),
]

# PICKUP TIME
LUNCH_PICKUP_TIME = [
    (0, '11:30'), (1, '11:45'), (2, '12:00'), (3, '12:15'),
    (4, '12:30'), (5, '12:45'), (6, '13:00'), (7, '13:15'), (8, '13:30')
]

DINNER_PICKUP_TIME = [
    (0, '17:30'), (1, '18:00'), (2, '18:30'),
    (3, '19:00'), (4, '19:30'), (5, '20:00'), (6, '20:30'), (7, '21:00')
]

# OPEN & CLOSE
OC_OPEN = 'open'
OC_CLOSE = 'close'
OC_STATUS = [
    (OC_OPEN, '열림'),
    (OC_CLOSE, '닫힘'),
]

# STORE OPEN & CLOSE
STORE_OC_OPEN = 'open'
STORE_OC_CLOSE = 'close'
STORE_OC_VACATION = 'vacation'
STORE_OC_STATUS = [
    (STORE_OC_OPEN, '열림'),
    (STORE_OC_CLOSE, '닫힘'),
    (STORE_OC_VACATION, '휴무'),

]

# STORE_TYPE
STORE_TYPE_NORMAL = 'normal'
STORE_TYPE_B2B = 'B2B'
STORE_TYPE_B2B_AND_NORMAL = 'B2BAndNormal'
STORE_TYPE_PROMOTION = 'promotion'
STORE_TYPE = [
    (STORE_TYPE_NORMAL, '일반'),
    (STORE_TYPE_B2B, 'B2B'),
    (STORE_TYPE_B2B_AND_NORMAL, 'B2B&일반'),
    (STORE_TYPE_PROMOTION, '프로모션'),
]

#  TYPE
ORDER_TYPE_NORMAL = 'normal'
ORDER_TYPE_B2B = 'B2B'
ORDER_TYPE_PROMOTION = 'promotion'
ORDER_TYPE = [
    (ORDER_TYPE_NORMAL, '일반'),
    (ORDER_TYPE_B2B, 'B2B'),
    (ORDER_TYPE_PROMOTION, '프로모션'),
]


# USER_TYPE
USER_TYPE_NORMAL = 'normal'
USER_TYPE_B2B = 'b2b'
USER_TYPE = [
    (USER_TYPE_NORMAL, '일반'),
    (USER_TYPE_B2B, 'B2B'),
]

# PARTNER_TYPE
PARTNER_TYPE_NORMAL = 'normal'
PARTNER_TYPE_MANAGER = 'manager'
PARTNER_TYPE_OWNER = 'owner'
PARTNER_TYPE = [
    (PARTNER_TYPE_NORMAL, '일반'),
    (PARTNER_TYPE_MANAGER, '매니저'),
    (PARTNER_TYPE_OWNER, '점주'),
]

# AREA_CODE
STORE_AREA_A_1 = 'A1'
STORE_AREA_A_2 = 'A2'
STORE_AREA_A_3 = 'A3'
STORE_AREA_A_4 = 'A4'

STORE_AREA_B_1 = 'B1'
STORE_AREA_B_2 = 'B2'

STORE_AREA_C_1 = 'C1'
STORE_AREA_C_2 = 'C2'
STORE_AREA_C_3 = 'C3'
STORE_AREA_C_4 = 'C4'

STORE_AREA_Z_1 = 'Z1'

STORE_AREA = [
    (STORE_AREA_A_1, '강남 1호점'),
    (STORE_AREA_A_2, '강남 2호점'),
    (STORE_AREA_A_3, '강남 3호점'),
    (STORE_AREA_A_4, '강남 4호점'),

    (STORE_AREA_B_1, '역삼 1호점'),
    (STORE_AREA_B_2, '역삼 2호점'),

    (STORE_AREA_C_1, '강남역'),
    (STORE_AREA_C_2, '역삼역'),
    (STORE_AREA_C_3, '삼성역'),
    (STORE_AREA_C_4, '선릉역'),

    (STORE_AREA_Z_1, '기타 지역'),
]

###########################################################################################
# Default Value
# Location

LOCATION_DEFAULT_ADDR = '강남 사거리'
LOCATION_DEFAULT_LAT = 37.497907
LOCATION_DEFAULT_LNG = 127.027635
