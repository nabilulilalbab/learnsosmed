from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

from .  forms import RegisterUserForm,PostForm
from .models import Post, User


from moviepy.video.io.VideoFileClip import VideoFileClip
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

def iterate_post(posts):
    post_data = []
    for post in posts:
        likes = post.liker.all()
        like_count = likes.count()
        liked_usernames = [user.name for user in likes[:3]]
        post_data.append({
            'post': post,
            'like_count': like_count,
            'liked_usernames': liked_usernames,
        })
    return post_data

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
    return render(request, "sosmed/index.html", context={
        'title': 'Learn Sosmed',
        'heading': 'Learn Sosmed',
        'posts': iterate_post(posts),
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

@login_required
def setting(request):
    # Use the logged-in user directly
    user_profile = request.user

    if request.method == 'POST':
        # Fetch new data from the form
        image = request.FILES.get('image', user_profile.profile_picture)
        bio = request.POST.get('bio', user_profile.bio)

        # Update user fields
        if image and image != user_profile.profile_picture:
            user_profile.profile_picture = image

        user_profile.bio = bio
        user_profile.save()

        return redirect('sosmed:detail_profile', user_id=user_profile.id)
    print(user_profile.profile_picture)
    return render(request, 'sosmed/setting.html', {'profile': user_profile})


@login_required(login_url='sosmed:login')
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user

            if 'video' in request.FILES:
                video_file = request.FILES['video']
                path = default_storage.save('uploads/' + video_file.name, ContentFile(video_file.read()))
                input_path = os.path.join(default_storage.location, path)
                output_filename = 'resized_' + video_file.name
                output_path = os.path.join(default_storage.location, 'uploads/', output_filename)

                # Use moviepy to resize the video
                with VideoFileClip(input_path) as video:
                    resized_video = video.resized(width=640)  # Updated method
                    resized_video.write_videofile(output_path, codec='libx264')

                # Save the resized video to the Post model
                with open(output_path, 'rb') as output_file:
                    post.video.save(output_filename, output_file)
                default_storage.delete(path)

            post.save()
            return redirect('sosmed:index')
    else:
        form = PostForm()

    return render(request, 'sosmed/add_post.html', {'form': form})
def detail_profile(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(creator=user_profile).order_by('-created_at')
    return render(request, "sosmed/detailprofile.html", context={
        'title': 'Detail Profile',
        'heading': 'Detail Profile',
        'posts': iterate_post(posts),
        'profile': user_profile,
    })

