# models: user, permission, group, form
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms
from .models import Post,Comments
class RegisterUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'password1', 'password2']  # Sesuaikan field dengan yang ada di model

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image', 'video', 'categories']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': (
                    'appearance-none bg-gray-100 border-2 border-gray-300 '
                    'w-full py-3 px-4 text-gray-700 rounded-lg focus:outline-none '
                    'focus:ring-2 focus:ring-black transition duration-300'
                )
            })

# Ensure to define additional styles for the `<form>` and `<button>` elements in your template
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment','image','video']



