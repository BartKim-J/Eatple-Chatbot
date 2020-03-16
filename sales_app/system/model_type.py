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

###########################################################################################
# Default Value
# Location

LOCATION_DEFAULT_ADDR = '강남 사거리'
LOCATION_DEFAULT_LAT = 37.497907
LOCATION_DEFAULT_LNG = 127.027635
