VALUE_NOT_APPLICABLE = 'N/A'

# Eatplus App Global Defines
STRING_32 = 31
STRING_256 = 255

###########################################################################################

NOT_APPLICABLE = VALUE_NOT_APPLICABLE

# STRING LENGTH
STRING_LENGTH = STRING_256
WORD_LENGTH = STRING_32

PROGRESS_LEVEL_S = 'S'
PROGRESS_LEVEL_A = 'A'
PROGRESS_LEVEL_B = 'B'
PROGRESS_LEVEL_C = 'C'
PROGRESS_LEVEL_D = 'D'

PROGRESS_LEVEL_N = 'N'
PROGRESS_LEVEL_TYPE = [
    (PROGRESS_LEVEL_S, '계약 완료'),
    (PROGRESS_LEVEL_A, '계약 유력(구두협의)'),
    (PROGRESS_LEVEL_B, '계약 가능성 있음'),
    (PROGRESS_LEVEL_C, '단순 제안/흥미 낮음'),
    (PROGRESS_LEVEL_D, '계약 불가 및 거절'),

    (PROGRESS_LEVEL_N, '컨택하지 못함'),
]

UP_AND_LOW_LEVEL_UPPER = 'UP'
UP_AND_LOW_LEVEL_MIDDLE = 'MID'
UP_AND_LOW_LEVEL_LOWER = 'LOW'
UP_AND_LOW_LEVEL_TYPE = [
    (UP_AND_LOW_LEVEL_UPPER, '상'),
    (UP_AND_LOW_LEVEL_MIDDLE, '중'),
    (UP_AND_LOW_LEVEL_LOWER, '하'),
]


MEMBER_LEVEL_OWNER = 'owner'
MEMBER_LEVEL_MASTER = 'master'
MEMBER_LEVEL_MANAGER = 'manager'
MEMBER_LEVEL_NORMAL = 'normal'

MEMBER_LEVEL_TYPE = [
    (MEMBER_LEVEL_OWNER, '대표'),
    (MEMBER_LEVEL_MASTER, '담당자'),
    (MEMBER_LEVEL_MANAGER, '매니저'),
    (MEMBER_LEVEL_NORMAL, '일반'),
]

PRIORITY_LEVEL_HIGH = 'high'
PRIORITY_LEVEL_MIDDLE = 'middle'
PRIORITY_LEVEL_LOW = 'low'
PRIORITY_LEVEL_PENDDING = 'pendding'

PRIORITY_LEVEL_TYPE = [
    (PRIORITY_LEVEL_HIGH, '상'),
    (PRIORITY_LEVEL_MIDDLE, '중'),
    (PRIORITY_LEVEL_LOW, '하'),
    (PRIORITY_LEVEL_PENDDING, '보류')
]
###########################################################################################
# Default Value
# Location

LOCATION_DEFAULT_ADDR = '강남 사거리'
LOCATION_DEFAULT_LAT = 37.497907
LOCATION_DEFAULT_LNG = 127.027635
