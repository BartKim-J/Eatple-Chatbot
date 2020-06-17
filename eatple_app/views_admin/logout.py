from django.contrib.auth import logout
from django.shortcuts import render, redirect

def POST_AdminLogout(request):
    logout(request)
    return redirect('index')
