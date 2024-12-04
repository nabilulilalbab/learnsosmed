from django.urls import path
from .views import index, register_user, login_user, logout_user,setting,add_post

app_name = "sosmed"

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("register/",register_user, name="register"),
    path("profile/", index, name="profile"),
    path('settings/', setting, name='settings'),
    path('add_post/', add_post, name='add_post'),
]
