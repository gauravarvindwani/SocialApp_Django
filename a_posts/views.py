from django.shortcuts import get_object_or_404, render, redirect 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from .models import *
from .forms import *
from bs4 import BeautifulSoup
import requests
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.
def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
    
    paginator = Paginator(posts, 3)
    page = int(request.GET.get('page', 1))
    try:
        posts = paginator.page(page)
    except:
        return HttpResponse('')


    context = {
        'posts' : posts,
        'tag' : tag,
        'page' : page
    }
    
    if request.htmx:
        return render(request, 'snippets/loop_home_posts.html', context )
    
    # print('Hello')
    # print(request)
    # # print(request.META)
    # print('Request Method', request.method)
    # if request.method == 'POST':  // this will not work because out method is GET
    #     print('Bye Bye')
    
    
    return render(request, 'a_posts/home.html', context)

@login_required
def post_create_view(request):
    form = PostCreateForm()
    
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            #### webcrawler 
            post = form.save(commit=False)
            
            website = requests.get(form.data['url'])            
            sourcecode = BeautifulSoup(website.text, 'html.parser')

            find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            image = find_image[0]['content']
            post.image = image
            
            find_title = sourcecode.select('h1.photo-title')
            title = find_title[0].text.strip()
            post.title = title

            find_artist = sourcecode.select('a.owner-name')
            artist = find_artist[0].text.strip()
            post.artist = artist
            
            post.author = request.user
            
            post.save()
            form.save_m2m()
            return redirect('home')
    
    return render(request, 'a_posts/post_create.html', {'form': form})

@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author = request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')
    
    return render(request, 'a_posts/post_delete.html', {'post' : post})

@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author = request.user)
    form = PostEditForm(instance=post)
    
    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, 'Post updated')
            return redirect('home')
    
    context = {
        'post' : post,
        'form' : form
    }
    return render(request, 'a_posts/post_edit.html', context)

def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    commentform = CommentCreateForm()
    replyform = ReplyCreateForm()
    
    
    if request.htmx:
        if 'top' in request.GET:
            # comments = post.comments.filter(likes__isnull=False).distinct()
            comments = post.comments.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
        else:
            comments= post.comments.all()
            
        return render(request, 'snippets/loop_postpage_comments.html', {'comments': comments, 'replyform':replyform})

    context = {
        'post' : post,
        'commentform' : commentform,
        'replyform': replyform,
        

    }
    
    return render(request, 'a_posts/post_page.html', context)


@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    replyform = ReplyCreateForm()
    
    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()
    
    context = {
        'reply' : post,
        'comment' : comment,
        'replyform' : replyform
    }

    return render(request, 'snippets/add_comment.html', context)


@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    replyform = ReplyCreateForm()
    
    if request.method == "POST":
        form = ReplyCreateForm(request.POST)
        if form.is_valid:
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment
            reply.save()
    
    context = {
        'reply' : reply,
        'comment' : comment,
        'replyform' : replyform
    }

    return render(request, 'snippets/add_reply.html', context)


@login_required
def comment_delete_view(request, pk):
    post = get_object_or_404(Comment, id=pk, author = request.user)
    
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Comment deleted')
        return redirect('post', post.parent_post.id )
    
    return render(request, 'a_posts/comment_delete.html', {'comment' : post})


@login_required
def reply_delete_view(request, pk):
    reply = get_object_or_404(Reply, id=pk, author = request.user)
    
    if request.method == "POST":
        reply.delete()
        messages.success(request, 'Reply deleted')
        return redirect('post', reply.parent_comment.parent_post.id )
    
    return render(request, 'a_posts/reply_delete.html', {'reply' : reply})

def like_toggle(model):
    def inner_func(func):
        def wrapper(request, *args, **kwargs):
            post = get_object_or_404(model, id=kwargs.get('pk'))
            user_exist = post.likes.filter(username=request.user.username).exists()

            if post.author != request.user:
                if user_exist:
                    post.likes.remove(request.user)
                else:
                    post.likes.add(request.user)
            return func(request, post)
        return wrapper
    return inner_func


@login_required
@like_toggle(Post)
def like_post(request, post):
    return render(request, 'snippets/likes.html', {'post' : post })


@login_required
@like_toggle(Comment)
def like_comment(request, post):
    return render(request, 'snippets/likes_comment.html', {'comment' : post })

@login_required
@like_toggle(Reply)
def like_reply(request, post):
    return render(request, 'snippets/likes_reply.html', {'reply' : post })