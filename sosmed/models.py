from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
# Create your models here.

# class User(AbstractUser):
#     profile_pic = models.ImageField(upload_to='profile_pic/')
#     bio = models.TextField(max_length=160, blank=True, null=True)
#
#     def __str__(self):
#         return self.username
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             "username": self.username,
#             "profile_pic": self.profile_pic.url,
#             "first_name": self.first_name,
#             "last_name": self.last_name
#         }


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Post(models.Model):
    # creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    username = models.CharField(max_length=200)
    caption =  models.TextField(max_length=140, blank=True)
    image = models.ImageField(blank=True,default='profile.png')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, editable=False)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    # liker = models.ManyToManyField(User, blank=True, related_name='likes')
    # savers = models.ManyToManyField(User, blank=True, related_name='saved')
    # comment_count = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.username}-{self.id}")
        super(Post,self).save(*args,**kwargs)
    def __str__(self):
        return  f"Post ID: {self.id} (creater: {self.username})"

    def img_url(self):
        return self.image.url
#
#
# class Comment(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
#     commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenters')
#     comment_content = models.TextField(max_length=90)
#     comment_time = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Post: {self.post} | Commenter: {self.commenter}"
#
#     def serialize(self):
#         return {
#             "id": self.id,
#             "commenter": self.commenter.serialize(),
#             "body": self.comment_content,
#             "timestamp": self.comment_time.strftime("%b %d %Y, %I:%M %p")
#         }
#
#
# class Follower(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
#     followers = models.ManyToManyField(User, blank=True, related_name='following')
#
#     def __str__(self):
#         return f"User: {self.user}"
#
