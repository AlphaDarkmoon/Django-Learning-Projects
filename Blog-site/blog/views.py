from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

############################################################
#             USELESS ( REMOVABLE ) AREA START
############################################################

############################################################
#            USELESS ( REMOVABLE ) AREA END
############################################################


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name ="blog/post/list.html"

class TaggedPostListView(ListView):
    model = Post
    template_name = 'blog/post/tagged_posts.html'  # Specify your template for tagged posts
    context_object_name = 'posts'

    def get_queryset(self):
        tag_name = self.kwargs['tag_name']  # Get the tag name from the URL
        return Post.published.filter(tags__name__in=[tag_name])  # Filter posts by tag


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page=request.GET.get('page')

    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',{'page':page,
                                                  'posts':posts,
                                                  'tag':tag})


def post_details(request, year, month, day, post):
    # Create a datetime object from the provided year, month, and day
    publish_date = timezone.datetime(int(year), int(month), int(day))

    # Fetch the post using the publish date and slug
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)  # Fetch active comments

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post  # Associate the comment with the post
            new_comment.save()
            comment_form = CommentForm()  # Reset form after saving

    else:
        comment_form = CommentForm()  # Initialize form for GET requests

    # Get the IDs of the tags associated with the current post
    post_tags_ids = post.tags.values_list('id', flat=True)

    # Fetch similar posts based on shared tags, excluding the current post
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    
    # Annotate with count of same tags and order by publish date (most recent first)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,  # Pass the form to the template
        'similar_posts': similar_posts,
    })


def post_share(request, post_id):
    # Retrieve the post or return a 404 if not found or not published
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you reading \"{post.title}\""
            message = f'Read "{post.title}" at {post_url}\n\n{cd["name"]}\'s comments: {cd["comments"]}'
            
            # Send the email
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True  # Update sent status after sending email

    else:
        form = EmailPostForm()  # Initialize the form for GET request

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent
    })