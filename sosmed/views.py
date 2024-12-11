import uuid

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .  forms import RegisterUserForm,PostForm,CommentForm
from .models import Post, User, Comments, Category, Follow
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.http import JsonResponse
from .models import Post
from sosmed.tasks import resize_video_task, compress_image_task
import logging
from .models import Follow, User
from django.views.decorators.http import require_POST
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


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
        path = default_storage.save('uploads/' + image.name, ContentFile(image.read()))
        output_filename = 'compressed_' + image.name
        compress_image_task.delay(path, 'uploads/', output_filename)
        linkedin = request.POST.get('linkedin', user_profile.linkedin)

        # Update user fields
        if image and image != user_profile.profile_picture:
            user_profile.profile_picture = os.path.join('uploads/', output_filename)
        user_profile.linkedin = linkedin
        user_profile.bio = bio
        user_profile.save()

        return redirect('sosmed:detail_profile', user_id=user_profile.id)
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
    followers_count = Follow.objects.filter(followed=user_profile).count()
    following_count = Follow.objects.filter(follower=user_profile).count()
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            followed=user_profile
        ).exists()

    # Ambil 3 followers terakhir (opsional)
    recent_followers = Follow.objects.filter(
        followed=user_profile
    ).select_related('follower')[:3]

    context = {
        'title': 'Detail Profile',
        'heading': 'Detail Profile',
        'posts': iterate_post(posts),
        'profile': user_profile,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'recent_followers': recent_followers,
    }

    return render(request, "sosmed/detailprofile.html", context)


@login_required
@require_POST
def follow_user(request):
    user_to_follow_id = request.POST.get('user_id')
    try:
        user_to_follow = get_object_or_404(User, id=user_to_follow_id)
        if user_to_follow == request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot follow yourself'
            }, status=400)
        existing_follow = Follow.objects.filter(
            follower=request.user,
            followed=user_to_follow
        ).exists()

        if existing_follow:
            # Unfollow
            Follow.objects.filter(
                follower=request.user,
                followed=user_to_follow
            ).delete()
            is_following = False
        else:
            # Follow
            Follow.objects.create(
                follower=request.user,
                followed=user_to_follow
            )
            is_following = True
        follower_count = Follow.objects.filter(followed=user_to_follow).count()

        return JsonResponse({
            'status': 'success',
            'is_following': is_following,
            'follower_count': follower_count
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)


@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    followers = Follow.objects.filter(followed=user).select_related('follower')
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('followed_id', flat=True)

    context = {
        'user': user,
        'followers': followers,
        'following_ids': following_ids
    }

    return render(request, 'sosmed/followers_list.html', context)


@login_required
def following_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    following = Follow.objects.filter(follower=user).select_related('followed')
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('followed_id', flat=True)

    context = {
        'user': user,
        'following': following,
        'following_ids': following_ids
    }

    return render(request, 'sosmed/following_list.html', context)


def get_follow_status(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    try:
        user_to_check = get_object_or_404(User, id=user_id)

        is_following = Follow.objects.filter(
            follower=request.user,
            followed=user_to_check
        ).exists()
        follower_count = Follow.objects.filter(followed=user_to_check).count()
        following_count = Follow.objects.filter(follower=user_to_check).count()

        return JsonResponse({
            'status': 'success',
            'is_following': is_following,
            'follower_count': follower_count,
            'following_count': following_count
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)



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
    try:
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
    post_by_id = get_object_or_404(Post, id=post_id)
    comments_all = Comments.objects.filter(post=post_by_id)
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
                    resize_video_task.delay(path, 'uploads/', output_filename)

                    post.video.name = os.path.join('uploads/', output_filename)
                elif 'image' in request.FILES:
                    image_file = request.FILES['image']
                    path = default_storage.save('uploads/' + image_file.name, ContentFile(image_file.read()))
                    output_filename = 'compressed_' + image_file.name
                    compress_image_task.delay(path, 'uploads/', output_filename)

                    post.image.name = os.path.join('uploads/', output_filename)
                post.save()
                return redirect('sosmed:detail_post', post_by_id.id)
    else:
        form = CommentForm()
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


@login_required(login_url='sosmed:login')
def following_posts(request):
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('followed_id', flat=True)
    following_ids = list(following_ids) + [request.user.id]
    posts = Post.objects.filter(
        creator__id__in=following_ids
    ).order_by('-created_at')

    context = {
        'title': 'Posts from Following',
        'heading': 'Posts from People You Follow',
        'posts': iterate_post(posts),
        'total_posts': posts.count()
    }
    return render(request, 'sosmed/postbyfollowing.html', context)