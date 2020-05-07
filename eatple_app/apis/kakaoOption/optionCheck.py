# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *


@csrf_exempt
def GET_KAKAO_OPTION_OptionCheck(request):
    print(request)
    try:
        id = request.GET.get('id')
        print(id)
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, 'message': ''})

    try:
        data = {
            "id": "101:10013529",
            "name": "윈터펠테스트11",
            "price": 0,
            "option_groups": [
                {
                    "id": "사이즈2",
                    "name": "사이즈2",
                    "option_sub_groups": [
                        {
                            "id": "사이즈2",
                            "options": [
                                {
                                    "id": "S12",
                                    "value": "S12",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "색상2",
                                            "sub_group_id": "S12:색상2"
                                        }
                                    ]
                                },
                                {
                                    "id": "S",
                                    "value": "S",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "색상2",
                                            "sub_group_id": "S:색상2"
                                        }
                                    ]
                                },
                                {
                                    "id": "M",
                                    "value": "M",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "색상2",
                                            "sub_group_id": "M:색상2"
                                        }
                                    ]
                                },
                                {
                                    "id": "L",
                                    "value": "L",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "색상2",
                                            "sub_group_id": "L:색상2"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "description": "사이즈을 선택해 주세요.",
                    "type": "SELECT"
                },
                {
                    "id": "색상2",
                    "name": "색상2",
                    "option_sub_groups": [
                        {
                            "id": "S12:색상2",
                            "options": [
                                {
                                    "id": "R23",
                                    "value": "R23",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "S12:R23:추가옵션"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "S:색상2",
                            "options": [
                                {
                                    "id": "G",
                                    "value": "G",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "S:G:추가옵션"
                                        }
                                    ]
                                },
                                {
                                    "id": "B",
                                    "value": "B",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "S:B:추가옵션"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "M:색상2",
                            "options": [
                                {
                                    "id": "R",
                                    "value": "R",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "M:R:추가옵션"
                                        }
                                    ]
                                },
                                {
                                    "id": "G",
                                    "value": "G",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "M:G:추가옵션"
                                        }
                                    ]
                                },
                                {
                                    "id": "B",
                                    "value": "B",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "M:B:추가옵션"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "L:색상2",
                            "options": [
                                {
                                    "id": "R",
                                    "value": "R",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "L:R:추가옵션"
                                        }
                                    ]
                                },
                                {
                                    "id": "G",
                                    "value": "G",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "L:G:추가옵션"
                                        }
                                    ]
                                },
                                {
                                    "id": "B",
                                    "value": "B",
                                    "relate_option_groups": [
                                        {
                                            "group_id": "추가옵션",
                                            "sub_group_id": "L:B:추가옵션"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "description": "색상을 선택해 주세요.",
                    "type": "SELECT"
                },
                {
                    "id": "추가옵션",
                    "name": "추가옵션",
                    "option_sub_groups": [
                        {
                            "id": "S12:R23:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 99,
                                    "extra": "12848",
                                    "stock": 99
                                }
                            ]
                        },
                        {
                            "id": "S:G:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 100,
                                    "max_quantity": 99,
                                    "extra": "12849",
                                    "stock": 99
                                }
                            ]
                        },
                        {
                            "id": "S:B:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 200,
                                    "max_quantity": 100,
                                    "extra": "12850",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "M:R:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 300,
                                    "max_quantity": 100,
                                    "extra": "12851",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "M:G:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 100,
                                    "extra": "12852",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "M:B:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 100,
                                    "extra": "12853",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "L:R:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 100,
                                    "extra": "12854",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "L:G:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 100,
                                    "extra": "12855",
                                    "stock": 100
                                }
                            ]
                        },
                        {
                            "id": "L:B:추가옵션",
                            "options": [
                                {
                                    "id": "A",
                                    "value": "A",
                                    "add_price": 0,
                                    "max_quantity": 100,
                                    "extra": "12856",
                                    "stock": 100
                                }
                            ]
                        }
                    ],
                    "description": "추가 옵션을 선택해 주세요.",
                    "type": "SELECT"
                }
            ]
        }

    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 300, 'message': ''})

    payload = {
        'status': 200,
        'data': data,
        'message': ''
    }

    return JsonResponse(payload, status=200)
