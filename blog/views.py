from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .models import CustomUser
from django.core.mail import EmailMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.urls import reverse
from .models import Post, Comment, Like
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from .utils import *
from .forms import PostForm, CommentForm
from django.utils.text import slugify


def index(request):
    if request.user.is_authenticated:
        return redirect('posts_list_url') 
    if request.method == 'GET':
        return render(request, 'index.html', {})
    if request.method == "POST":
        email, password = request.POST['email'], request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
        else:
            return render(request, 'index.html', {'err': 'User does not exist'})
        return redirect('posts_list_url')

def logout_view(request):
	if request.user.is_authenticated:
		logout(request)
	return redirect('index')


def signup(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			mail_subject = 'Activate your blog account'
			message = render_to_string('acc_active_email.html', {
					'user': user,
					'domain': current_site.domain,
					'uid': urlsafe_base64_encode(force_bytes(user.pk)),
					'token': account_activation_token.make_token(user),
				})
			to_email = form.cleaned_data.get('email')
			email = EmailMessage(
				mail_subject, message, to=[to_email]
			)
			email.send()
			return HttpResponse('Please confirm your email address to complete the registration')
	else:
		form = CustomUserCreationForm()
	return render(request, 'signup.html', {'form': form})

def activate(request, uid64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uid64))
		user = CustomUser.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		#login(request, user)
		return redirect('index')
	else:
		return HttpResponse('Activation link is invalid!')



def posts_list(request):
	if request.user.is_authenticated:
	    search_query = request.GET.get('search', '')

	    if search_query:
	        posts = Post.objects.filter(Q(title__icontains=search_query) | Q(body__icontains=search_query))
	    else:
	        posts = Post.objects.all()
	    results = []
	    for post in posts:
	    	likes = len(Like.objects.filter(post_id=post.id, is_liked=True))
	    	results.append((post, likes))
	    paginator = Paginator(posts, 2)

	    page_number = request.GET.get('page', 1)
	    page = paginator.get_page(page_number)

	    is_paginated = page.has_other_pages()

	    if page.has_previous():
	        prev_url = '?page={}'.format(page.previous_page_number())
	    else:
	        prev_url = ''

	    if page.has_next():
	        next_url = '?page={}'.format(page.next_page_number())
	    else:
	        next_url = ''

	    context = {
	        'page_object': page,
	        'is_paginated': is_paginated,
	        'next_url': next_url,
	        'prev_url': prev_url,
	        'likes': results,
	    }

	    return render(request, 'blog/index.html', context=context)
	else:
		return redirect('index')


def addlike(request, slug):
	postid = Post.objects.get(slug__iexact=slug).id
	try:
		like = Like.objects.get(post_id=postid, author_id=request.user.id)
		if like.is_liked:
			like.is_liked = False
			like.save()
			return redirect(request.META['HTTP_REFERER'])
		else:
			like.is_liked = True
			like.save()
			return redirect(request.META['HTTP_REFERER'])
	except Exception:
		like = Like.objects.create(post_id=postid, author_id=request.user.id, is_liked=True)
		like.save()
		return redirect(request.META['HTTP_REFERER'])



class PostDetail(LoginRequiredMixin, ObjectDetailMixin, View):
    model = Post
    model1 = Comment
    model2 = Like
    model_form = CommentForm
    permission_required = 'is_staff'
    template = 'blog/post_detail.html'


class PostCreate(PermissionRequiredMixin, LogoutIfNotStaffMixin, ObjectCreateMixin, View):
   model_form = PostForm
   template = 'blog/post_create_form.html'
   permission_required = 'is_staff'
   raise_exception = True


class PostUpdate(PermissionRequiredMixin, LogoutIfNotStaffMixin, ObjectUpdateMixin, View):
    model = Post
    model_form = PostForm
    template = 'blog/post_update_form.html'
    permission_required = 'is_staff'
    raise_exception = True


class PostDelete(PermissionRequiredMixin, LogoutIfNotStaffMixin, ObjectDeleteMixin, View):
    model = Post
    template = 'blog/post_delete_form.html'
    redirect_url = 'posts_list_url'
    permission_required = 'is_staff'
    raise_exception = True



