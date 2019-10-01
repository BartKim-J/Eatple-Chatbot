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
    
    GET_ORDER_LIST_TOTAL_COMMAND    = "주문 조회"
    GET_ORDER_LIST_DETAIL_COMMAND   = "주문 조회"
    GET_CALCULATE_CHECK_COMMAND     = "정산 조회"
    STORE_MANUAL_COMMAND            = "사용방법"

    ## WORDING TESTS
    HOME_TITLE_TEXT                 = "잇플 파트너 홈 화면입니다."
    HOME_DESCRIPT_TEXT              = "아래 명령어 중에 골라주세요!"
    
    GET_ORDER_LIST_EMPTY_TEXT = "아직 들어온 주문이 없습니다."