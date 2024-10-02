from django.urls import re_path, path
from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    # re_path(r'^$', views.PostListView.as_view(), name='post_list'),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$', 
            views.post_details, 
            name='post_detail'),
    re_path(r'^(?P<post_id>\d+)/share/$', views.post_share, name='post_share'),
    re_path(r'^tag/(?P<tag_name>[-\w]+)/$', views.TaggedPostListView.as_view(), name='tagged'),  # New URL for tags
    re_path(r'^$',views.post_list, name='post_list'),
    re_path(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_by_tag'),
    re_path(r'^feed/$', LatestPostsFeed(), name='post_feed'),
]