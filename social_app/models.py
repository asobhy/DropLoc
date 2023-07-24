from django.db import models
from account.models import Account

# Create your models here.


class Post(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, related_name='author')
    user_post = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    date_post = models.DateTimeField(auto_now_add=True)
    date_post_update = models.DateTimeField(auto_now=True)
    user_like_post = models.ManyToManyField(Account, blank=True)

    def __str__(self):
        return f"Post By {self.pk}"


class Comment(models.Model):
    user = user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, related_name='commenter')
    post_id = models.ForeignKey(
        Post, on_delete=models.CASCADE, blank=True, null=True, related_name='post')
    comment = models.TextField(null=True, blank=True)
    date_comment = models.DateTimeField(auto_now_add=True)
    date_comment_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post Commented by {self.comment}'
