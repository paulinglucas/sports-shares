from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from .forms import SignUpForm
from django.shortcuts import render, redirect
# Create your views here.

def signup_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.profile.first_name = form.cleaned_data.get('first_name')
        user.profile.last_name = form.cleaned_data.get('last_name')
        user.profile.email = form.cleaned_data.get('email')
        user.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return render(request, 'success/signup_success.html')
    else:
        form = SignUpForm()
    if request.method == 'POST':
        return render(request, 'sign_up.html', {'form': form, 'success': 'no'})
    else:
        return render(request, 'sign_up.html', {'form': form})

def login_view(request):
    return render(request, 'login.html')

def login_success_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', "")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'success/login_success.html')
    else:
        return login_view(request)



def logout_success_view(request):
    logout(request)
    return render(request, 'success/logout_success.html')
