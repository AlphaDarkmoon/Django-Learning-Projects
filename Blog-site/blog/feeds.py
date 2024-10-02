from django.contrib.syndication.views import Feed
from django.db.models.base import Model
from django.template.defaultfilters import truncatewords
from django.utils.safestring import SafeText
from .models import Post

class LatestPostsFeed(Feed):
    title = 'My Blog'
    link='/blog/'
    description = 'New Posts of my blog.'

    def items(self):
        return Post.published.all()[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self,item):
        return truncatewords(item.body, 30)