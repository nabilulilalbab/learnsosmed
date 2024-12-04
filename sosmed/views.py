import profile

from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .  forms import RegisterUserForm,PostForm
from .models import Profile,Post

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
    return render(request, "sosmed/register.html", context={
            'title': 'Register',
            'heading': 'Register',
            'form': register,
        })



def index(request):
    posts = Post.objects.all().order_by('-created_at')

    return render(request,"sosmed/index.html",context={
        'title':'Learn Sosmed',
        'heading':'Learn Sosmed',
        'posts': posts
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
                messages.success(request,'Login success')
                return redirect('sosmed:index')
            else:
                messages.error(request,'Login failed')
                return redirect('sosmed:login')
    return render(request,'sosmed/login.html',context={
        'title':'Login',
    })

@login_required(login_url='sosmed:index')
def logout_user(request):
    if request.method == 'POST':
        if request.POST.get('logout') == 'logout':
            logout(request)
            return redirect('sosmed:login')
    return render(request, 'sosmed/logout.html', context={
        'title': 'Logout',
    })
@login_required(login_url='sosmed:index')
def setting(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profile_picture)
        bio = request.POST.get('bio', user_profile.bio)

        user_profile.profile_picture = image
        user_profile.bio = bio
        user_profile.save()

        return redirect('sosmed:profile')

    return render(request, 'sosmed/setting.html', context={
        'title': 'Setting',
        'heading': 'Setting',
        'user_profile': user_profile,
    })

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            return redirect('sosmed:index')
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'sosmed/add_post.html', {'form': form,
                                                 'posts': posts,})