from django.contrib import admin
from .models import Post, Comment
from django.db import models


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')


# Represent how the admin panel of `Blog` field will look
class PostAdmin(admin.ModelAdmin):
    list_display = ('title','slug','author','publish','status')
    list_filter = ('status','created','publish','author')
    search_fields = ('title','body')
    prepopulated_fields = { 'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status','publish']
admin.site.register(Post, PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name','email','post','created','active')
    list_filter = ('active','created','updated')
    search_fileds = ('name','email','body')
admin.site.register(Comment,CommentAdmin)