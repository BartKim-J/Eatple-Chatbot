# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *


class Kakao():
    def getProfile(self, user):
        headers = {
            'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
        }

        apiURL = '{shcme}{host}{url}'.format(
            shcme='https://', host='kapi.kakao.com', url='/v2/user/me')

        data = {
            'target_id_type': 'user_id',
            'target_id': user.app_user_id
        }

        kakaoResponse = requests.post(apiURL, data=data, headers=headers)

        try:
            user.nickname = kakaoResponse.json(
            )['kakao_account']['profile']['nickname']
            user.email = kakaoResponse.json(
            )['kakao_account']['email']
            user.phone_number = kakaoResponse.json(
            )['kakao_account']['phone_number']
            user.save()
        except:
            pass

        return user


def getPFriendList(self, user):
    headers = {
        'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
    }

    apiURL = '{shcme}{host}{url}'.format(
        shcme='https://', host='kapi.kakao.com', url='/v2/user/me')

    data = {
        'target_id_type': 'user_id',
        'target_id': user.app_user_id
    }

    kakaoResponse = requests.post(apiURL, data=data, headers=headers)

    user.nickname = kakaoResponse.json(
    )['kakao_account']['profile']['nickname']
    user.email = kakaoResponse.json(
    )['kakao_account']['email']
    user.phone_number = kakaoResponse.json(
    )['kakao_account']['phone_number']
    user.save()

    return user
