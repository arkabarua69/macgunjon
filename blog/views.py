from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, Tag


def blog_list(request):
    posts = BlogPost.objects.filter(published=True).order_by('-created_at')

    tag_slug = request.GET.get('tag')
    current_tag = None
    if tag_slug:
        current_tag = get_object_or_create_tag(tag_slug)
        if current_tag:
            posts = posts.filter(tags=current_tag)

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tags = Tag.objects.all()

    return render(request, 'blog/blog_list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'tags': tags,
        'current_tag': current_tag,
        'tag_slug': tag_slug,
    })


def get_object_or_create_tag(slug):
    try:
        return Tag.objects.get(slug=slug)
    except Tag.DoesNotExist:
        return None


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    recent = BlogPost.objects.filter(published=True).exclude(id=post.id).order_by('-created_at')[:3]

    related_by_tag = BlogPost.objects.filter(
        published=True, tags__in=post.tags.all()
    ).exclude(id=post.id).distinct().order_by('-created_at')[:3]

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'recent': recent,
        'related_by_tag': related_by_tag,
    })
