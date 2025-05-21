from django.shortcuts import render


def login_view(request):
    return render(request, "auth_users/login.html")

def logout_view(request):
    return render(request, "auth_users/logout.html")