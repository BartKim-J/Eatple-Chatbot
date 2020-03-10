"""
    -701	결제인증이 완료되지 않았는데 결제승인 API를 호출한 경우	400
    -702	이미 결제 완료된 TID로 다시 결제승인 API를 호출한 경우	400
    -703	결제승인 API 호출 시 포인트 금액이 잘못된 경우	400
    -704	결제승인 API 호출 시 원결제수단(머니/카드)의 금액이 잘못된 경우	400
    -705	결제승인 API 호출 시 지원하지 않는 결제수단으로 요청한 경우	400
    -706	결제준비 API에서 요청한 partner_order_id 와 다른 값으로 결제승인 API 호출 한 경우	400
    -707	결제준비 API에서 요청한 partner_user_id 와 다른 값으로 결제승인 API 호출 한 경우	400
    -708	잘못된 pg_token 로 결제승인 API를 호출한 경우	400
    -710	결제취소 API 호출 시 취소 요청 금액을 취소 가능액보다 큰 금액으로 요청한 경우	400
    -711	취소금액오류, 원거래 승인금액보다 취소금액이 더 큰 경우	400
    -721	TID가 존재하지 않는 경우	400
    -722	금액 정보가 잘못된 경우	400
    -723	결제 만료 시간이 지난 경우	400
    -724	단건결제금액이 잘못된 경우	400
    -725	총 결제금액이 잘못된 경우	400
    -726	주문정보가 잘못된 경우	400
    -730	가맹점 앱 정보가 잘못된 경우	400
    -731	CID 가 잘못된 경우	400
    -732	GID 가 잘못된 경우	400
    -733	CID_SECRET 이 잘못된 경우	400
    -750	SID가 존재하지 않는 경우	400
    -751	비활성화된 SID로 정기결제 API 를 호출한 경우	400
    -752	SID가 월 최대 사용 횟수를 초과한 경우	400
    -753	정기결제 API 호출시 partner_user_id가 SID를 발급받았던 최초 결제준비 API 에서 요청한 값과 다른 경우	400
    -761	입력한 전화번호가 카카오톡에 가입하지 않은 경우	400
    -780	결제승인 API 호출이 실패한 경우	400
    -781	결제취소 API 호출이 실패한 경우	400
    -782	정기결제 API 호출이 실패한 경우	400
    -783	승인요청을 할 수 없는 상태에 결제승인 API를 호출한 경우	400
    -784	취소요청을 할 수 없는 상태에 결제취소 API를 호출한 경우	400
    -785	결제/취소를 중복으로 요청한 경우	400
    -797	1회 결제 한도금액 초과일 경우	400
    -798	허용되지 않는 ip를 사용한 경우	400
"""
KAKAO_REST_701_NOT_FINISHED_AUTH = -701
KAKAO_REST_702_ALREADY_PAID = -702
KAKAO_REST_703_INVALID_APPROVE_PARAM_POINT = -703
KAKAO_REST_704_INVALID_APPROVE_PARAM_AMOUNT = -704
KAKAO_REST_705_INVALID_APPROVE_PARAM_METHOD = -705
KAKAO_REST_706_INVALID_APPROVE_PARAM_ORDER_ID = -706
KAKAO_REST_707_INVALID_APPROVE_PARAM_USER_ID = -707
KAKAO_REST_708_INVALID_APPROVE_PARAM_PG_TOKEN = -708
KAKAO_REST_710_INVALID_APPROVE_PARAM_PG_TOKEN = -710
KAKAO_REST_711_INVALID_CANCEL_PARAM_OVER_AMOUNT = -711

KAKAO_REST_721_NULL_PARAM_TID = -721
KAKAO_REST_722_INVALID_PARAM_AMOUNT_INFO = -722
KAKAO_REST_723_EXPIRED_TID = -723
KAKAO_REST_724_INVALID_PARAM_PART_AMOUNT = -724
KAKAO_REST_725_INVALID_PARAM_TOTAL_AMOUNT = -725
KAKAO_REST_726_INVALID_PARAM_ORDER_INFO = -726

KAKAO_REST_730_INVALID_PARAM_PARTNER_APP_ID = -730
KAKAO_REST_731_INVALID_PARAM_CID = -731
KAKAO_REST_732_INVALID_PARAM_GID = -732
KAKAO_REST_733_INVALID_PARAM_CID_SECRET = -733

KAKAO_REST_750_NULL_PARAM_SID = -750
KAKAO_REST_751_EXPIRED_SID = -751
KAKAO_REST_752_OVERTIME_SID = -752
KAKAO_REST_753_MISMATCH_PARAM_SID = -753

KAKAO_REST_761_INVALID_USER = -761

KAKAO_REST_780_CALL_API_ORDER_APPROVE_FAILED = -780
KAKAO_REST_781_CALL_API_ORDER_CANCEL_FAILED = -781
KAKAO_REST_782_CALL_API_SUBSCRIPTION_FAILED = -782
