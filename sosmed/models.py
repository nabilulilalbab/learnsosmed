from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin
from django.utils.text import slugify

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
    linkedin = models.URLField(blank=True,default='https://www.linkedin.com/in/')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.id} {self.email}'
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True
    def get_short_name(self):
        return self.name.split('@')[0]

    def img_url(self):
        return self.profile_picture.url

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.name} Profile'

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'



class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True)
    image = models.ImageField(blank=True, upload_to='posts/')
    video = models.FileField(blank=True, upload_to='posts/', null=True,
                             validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])])
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, editable=False)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    liker = models.ManyToManyField(User, blank=True, related_name='likes')
    like_count = models.IntegerField(default=0)
    savers = models.ManyToManyField(User, blank=True, related_name='saved')
    comment_count = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        if not self.pk:  # If the object is new (hasn't been saved yet)
            super().save(*args, **kwargs)  # Save to generate an ID
        if not self.slug:  # Only set the slug if it hasn't been set yet
            self.slug = slugify(f"{self.creator.id}-{self.id}")
            super().save(update_fields=['slug'])  # Update only the slug field

    def __str__(self):
        return f"Post ID: {self.id} (creator: {self.creator})"

    def img_url(self):
        if self.image:
            return self.image.url
        return None

class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(blank=True)
    image = models.ImageField(blank=True, upload_to='posts/')
    video = models.FileField(blank=True, upload_to='posts/', null=True,
                             validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"commoe ID: {self.id} (creator: {self.user})"

    def img_url(self):
        if self.image:
            return self.image.url
        return None


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.name} follows {self.followed.name}"




