from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin
from django.utils.text import slugify
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email,name, password):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email),name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password,name):
        user = self.create_user(email=email, password=password,name=name)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser,PermissionsMixin):
    username = None
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True,verbose_name='email address')
    profile_picture = models.ImageField(blank=True,default='profile.png',upload_to='profile_picture/')
    bio = models.TextField(max_length=500, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True
    def get_short_name(self):
        return self.name.split('@')[0]

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.CharField(max_length=200)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(blank=True,default='profile.png',upload_to='profile_picture/')

    def __str__(self):
        return f'{self.user.name} Profile'

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption =  models.TextField(max_length=140, blank=True)
    image = models.ImageField(blank=True,default='profile.png',upload_to='posts/')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, editable=False)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    liker = models.ManyToManyField(User, blank=True, related_name='likes')
    savers = models.ManyToManyField(User, blank=True, related_name='saved')
    comment_count = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.creator}-{self.id}")
        super(Post,self).save(*args,**kwargs)
    def __str__(self):
        return  f"Post ID: {self.id} (creater: {self.creator})"

    def img_url(self):
        return self.image.url

    def append(self, name, value):
        self.name = value


