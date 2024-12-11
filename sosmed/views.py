from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

from .  forms import RegisterUserForm,PostForm,CommentForm
from .models import Post, User,Comments,Category


from moviepy.video.io.VideoFileClip import VideoFileClip
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from django.http import JsonResponse
from .models import Post


from sosmed.tasks import resize_video_task, compress_image_task


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
                output_filename = 'resized_' + video_file.name
                resize_video_task.delay(path, 'uploads/', output_filename)  # Celery task dipanggil di sini

                post.video.name = os.path.join('uploads/', output_filename)  # Simpan nama file
            elif 'image' in request.FILES:
                image_file = request.FILES['image']
                path = default_storage.save('uploads/' + image_file.name, ContentFile(image_file.read()))
                output_filename = 'compressed_' + image_file.name

                # Memanggil task Celery untuk kompresi gambar
                compress_image_task.delay(path, 'uploads/', output_filename)

                post.image.name = os.path.join('uploads/', output_filename)
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




@login_required(login_url='sosmed:login')
def like_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        post.liker.add(request.user)
        post.save()
        like_count = post.liker.count()

        return JsonResponse({'like_count': like_count})

@login_required(login_url='sosmed:login')
def unlike_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        post.liker.remove(request.user)
        post.save()
        like_count = post.liker.count()

        return JsonResponse({'like_count': like_count})

@login_required(login_url='sosmed:login')
def save_post(request,post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        post.savers.add(request.user)
        post.save()
        return JsonResponse({'status': 'saved'})

@login_required(login_url='sosmed:login')
def unsave_post(request,post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        post.savers.remove(request.user)
        post.save()
        return JsonResponse({'status': 'unsaved'})

@login_required(login_url='sosmed:login')
def save_all(request):
    """
    Menampilkan semua postingan yang disave oleh user
    """
    try:
        # Ambil semua post yang disave oleh user saat ini
        saved_posts = Post.objects.filter(savers=request.user).order_by('-created_at')

        context = {
            'title': 'Postingan Tersimpan',
            'heading': 'Postingan Tersimpan',
            'posts': iterate_post(saved_posts),
            'total_saved_posts': saved_posts.count()
        }

        return render(request, "sosmed/index.html", context)

    except Exception as e:
        messages.error(request, f"Error menampilkan postingan tersimpan: {str(e)}")
        return redirect('sosmed:index')

@login_required(login_url='sosmed:login')
def comments(request, post_id):
    # if request.method == 'POST':
    post_by_id = get_object_or_404(Post, id=post_id)
    comments_all = Comments.objects.filter(post=post_by_id)
    print(post_by_id)
    # comments_count = len(comments_all)
    if request.method == 'POST':
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.post = post_by_id
                post.user = request.user
                if 'video' in request.FILES:
                    video_file = request.FILES['video']
                    path = default_storage.save('uploads/' + video_file.name, ContentFile(video_file.read()))
                    output_filename = 'resized_' + video_file.name
                    resize_video_task.delay(path, 'uploads/', output_filename)  # Celery task dipanggil di sini

                    post.video.name = os.path.join('uploads/', output_filename)  # Simpan nama file
                elif 'image' in request.FILES:
                    image_file = request.FILES['image']
                    path = default_storage.save('uploads/' + image_file.name, ContentFile(image_file.read()))
                    output_filename = 'compressed_' + image_file.name

                    # Memanggil task Celery untuk kompresi gambar
                    compress_image_task.delay(path, 'uploads/', output_filename)

                    post.image.name = os.path.join('uploads/', output_filename)
                post.save()
                return redirect('sosmed:detail_post', post_by_id.id)
    else:
        form = CommentForm()



        # Comments.objects.create(post=post, user=request.user, comment=request.POST['comments'])
    return render(request, "sosmed/detail_post.html", context={
            'posts': post_by_id,
            'form': form,
            'like_count': post_by_id.liker.count(),
            'comments_all': comments_all,
        })




def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(categories=category).order_by('-created_at')
    return render(request, 'sosmed/category.html', {
        'category': category,
        'posts': iterate_post(posts),
    })