from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from eatple_app.forms import LoginForm


def POST_AdminLogin(request):  # 로그인 기능
    if request.method == "GET":
        return render(request, 'dashboard/base.html')

    elif request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user_instance = authenticate(username=username, password=password)

        if user_instance:
            login(request, user=user_instance)
            return redirect('index')
        else:
            return render(request, 'dashboard/base.html', {'f': form, 'error': '아이디나 비밀번호가 일치하지 않습니다.'})
