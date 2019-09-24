'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Define
from eatplus_app.define import EP_define

NOT_APPLICABLE              = EP_define.NOT_APPLICABLE

SELLING_TIME_LUNCH          = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER         = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT  = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY       = EP_define.SELLING_TIME_CATEGORY

LUNCH  = SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0]
DINNER = SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0]

ORDER_STATUS                = EP_define.ORDER_STATUS
ORDER_STATUS_DICT           = EP_define.ORDER_STATUS_DICT

KAKAO_PARAM_ORDER_ID        = EP_define.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = EP_define.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = EP_define.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_MENU_CATEGORY   = EP_define.KAKAO_PARAM_MENU_CATEGORY
KAKAO_PARAM_SELLING_TIME    = EP_define.KAKAO_PARAM_SELLING_TIME
KAKAO_PARAM_PICKUP_TIME     = EP_define.KAKAO_PARAM_PICKUP_TIME

KAKAO_PARAM_STATUS          = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = EP_define.KAKAO_PARAM_STATUS_NOT_OK

KAKAO_SUPER_USER_ID         = EP_define.DEFAULT_USER_ID

class wordings():
    HOME_QUICK_REPLISE        = "홈"
    RETURN_HOME_QUICK_REPLISE = "홈으로 돌아가기"

    REFRESH_BTN               = "새로고침"
    ORDER_BTN                 = "주문하기"
    SHOW_LOCATION_BTN         = "위치보기"
    CHANGE_LOCATION_BTN       = "위치변경"
    
    ## KAKAO BLOCK COMMAND
    CHANGE_LOCATION_COMMAND                   = CHANGE_LOCATION_BTN
    GET_SELLING_TIEM_COMMAND                  = "주문시간 선택"
    GET_MENU_COMMAND                          = "메뉴보기"
    GET_PICKUP_TIME_COMMAND                   = "픽업시간 설정"
    ORDER_CONFIRM_COMMAND                     = "픽업시간 설정 완료"
    ORDER_PUSH_COMMAND                        = "결제하기"

    ORDER_CANCEL_COMMAND                      = "주문 취소하기"
    ORDER_PICKUP_TIME_CHANGE_COMMAND          = "픽업시간 변경"
    ORDER_PICKUP_TIME_CHANGE_CONFIRM_COMMAND  = "픽업시간 변경 완료"

    GET_COUPON_COMMAND                        = "잇플패스 확인"
    GET_ORDER_LIST_COMMAND                    = "최근 구매내역"
    CONFIRM_USE_COUPON_COMMAND                = "잇플패스 사용 확인"
    USE_COUPON_COMMAND                        = "잇플패스 사용"

    USER_MANUAL_COMMAND                       = "사용방법"
    

    ## WORDING TESTS
    HOME_TITLE_TEXT                                 = "잇플 홈 화면입니다."
    HOME_DESCRIPT_TEXT                              = "아래 명령어 중에 골라주세요!"

    GET_SELLING_TIME_SELECT_TITLE_TEXT              = "점심 또는 저녁을 선택해 주세요!"
    GET_SELLING_TIME_SELECT_DESCRIPT_TEXT           = "한 사람당 하루에\n점심 1회, 저녁 1회 주문이 가능해요!\n\n - 주문 가능 시간 - \n+ 점심 : 전날 16:30 ~ 당일 10:30까지\n+ 저녁 : 당일 10:30 ~ 16:30"
    GET_SELLING_TIME_LUNCH_BTN                      = "{} {}".format(LUNCH, GET_MENU_COMMAND)
    GET_SELLING_TIME_DINNER_BTN                     = "{} {}".format(DINNER, GET_MENU_COMMAND)

    GET_SELLING_TIME_LUNCH_FINISH_TEXT              = "점심 주문이 마감되었어요!\n지금은 저녁 주문시간입니다."
    GET_SELLING_TIME_DINNER_FINISH_TEXT             = "저녁 주문이 마감되었어요!\n지금은 점심 주문시간입니다."
    
    ALREADY_ORDER_LUNCH_TEXT                        = "이미 점심 주문을 해주셨네요!\n저녁시간 혹은 내일 다시 잇플과 함께해주세요."
    ALREADY_ORDER_DINNER_TEXT                       = "이미 저녁 주문을 해주셨네요!\n곧 있을 내일 점심 주문시간에 잇플과 다시 함께해주세요."
    ALREADY_ORDER_EATPLUS_TEXT                      = "오늘 하루, 잇플로 맛있는 식사를 즐겨주셔서 감사해요. 내일도 잇플과 함께 해주실거죠?"

    GET_COUPON_EMPTY_TEXT                           = "현재 조회 가능한 잇플패스가 없습니다!\n주문하시려면 아래 [{}]를 눌러주세요!".format(ORDER_BTN)
    GET_ORDER_LIST_EMPTY_TEXT                       = "주문 내역이 존재하지 않습니다!\n주문하시려면 아래 [{}]를 눌러주세요!".format(ORDER_BTN)