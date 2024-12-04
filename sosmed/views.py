from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
# Create your views here.
from .  forms import RegisterUserForm


def register_user(request):
    register = RegisterUserForm(request.POST or None)
    if request.method == 'POST':
        if register.is_valid():
            register.save()
            messages.success(request,'Register success')
            return redirect('sosmed:login')
        else:
            messages.error(request, 'Register failed')
            redirect('sosmed:register')
    else:
        register = RegisterUserForm()
    return render(request,"sosmed/register.html",context={
        'title':'Register',
        'heading':'Register',
        'form':register,
    })



def index(request):
    return render(request,"sosmed/index.html",context={
        'title':'Learn Sosmed',
        'heading':'Learn Sosmed',
    })
def login_user(request):
    if request.user.is_authenticated:
        return redirect('sosmed:index')
    if request.method == 'POST':
            username_input = request.POST['username']
            password_input = request.POST['password']
            user = authenticate(request,username=username_input,password=password_input)
            if user is not None:
                login(request,user)
                # return render(request,'sosmed/index.html',context={
                #     'title':'Learn Sosmed',
                #     'heading':'Learn Sosmed',
                # })
                messages.success(request,'Login success')
                return redirect('sosmed:index')
            else:
                messages.error(request,'Login failed')
                return redirect('sosmed:login')
    # username_user = 'korteks'
    # password_user = 'korteks'
    # user = authenticate(username=username_user,password=password_user)
    # login(request,user)
    return render(request,'sosmed/login.html',context={
        'title':'Login',
    })

def logout_user(request):
    if request.method == 'POST':  # Pastikan hanya mengizinkan POST
        if request.POST.get('logout') == 'logout':
            logout(request)
            return redirect('sosmed:login')
    return render(request, 'sosmed/logout.html', context={
        'title': 'Logout',
    })