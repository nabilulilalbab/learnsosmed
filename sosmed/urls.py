from django.urls import path
from .views import index, register_user, login_user, logout_user, setting, add_post, detail_profile, like_post, \
    unlike_post, unsave_post, save_post, comments, save_all, category_posts, follow_user, followers_list, \
    following_list, get_follow_status,following_posts

app_name = "sosmed"

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("register/",register_user, name="register"),
    path("profile/<int:user_id>/", detail_profile, name="detail_profile"),
    path('settings/', setting, name='settings'),
    path('add_post/', add_post, name='add_post'),
    path('like/<int:post_id>/', like_post, name='like_post'),
    path('unlike/<int:post_id>/', unlike_post, name='unlike_post'),
    path('save/<int:post_id>/',save_post, name='save'),
    path('unsave/<int:post_id>/', unsave_post, name='unsave_post'),
    path('save_all/', save_all, name='save_all'),
    path('detail_post/<int:post_id>/', comments, name='detail_post'),
    path('category/<int:category_id>/', category_posts, name='category_posts'),
    path('follow/', follow_user, name='follow_user'),
    path('followers/<int:user_id>/', followers_list, name='followers_list'),
    path('following/<int:user_id>/', following_list, name='following_list'),
    path('follow-status/<int:user_id>/', get_follow_status, name='follow_status'),
    path('postbyfollowing/',following_posts, name='postbyfollowing'),
]
