from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf.urls import url
from django.urls import reverse
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .forms import GeneralPostCreateAlterForm, GeneralPostDeleteForm
from .models import GeneralPost, Tag, FilterTagRelation

@require_http_methods(["GET","POST"])
def user_post_list_view(request):
	if request.method == "GET":
		user=request.user
		saved_posts = GeneralPost.objects.filter(author_id=user.id,published=False)
		paginator = Paginator(saved_posts, 6)
		page = request.GET.get('page')
		try: 
			user_saved_posts = paginator.page(page)
		except PageNotAnInteger:
			user_saved_posts = paginator.page(1)
		except EmptyPage:
			user_saved_posts = paginator.page(paginator.num_pages)
		published_posts= GeneralPost.objects.filter(author_id=user.id,published=True)
		paginator = Paginator(published_posts, 6)
		page = request.GET.get('page')
		try: 
			user_published_posts = paginator.page(page)
		except PageNotAnInteger:
			user_published_posts = paginator.page(1)
		except EmptyPage:
			user_published_posts = paginator.page(paginator.num_pages)			
		context = {'user_published_posts': user_published_posts,
				   'user_saved_posts':user_saved_posts}
		return render(request,'post/user_post_list.html',context)
	else:
		raise Http403


def post_list_view(request):
		post_list = GeneralPost.objects.filter(published=True)
		paginator = Paginator(post_list, 6)
		page = request.GET.get('page')
		try: 
			posts = paginator.page(page)
		except PageNotAnInteger:
			posts = paginator.page(1)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)
		context = {'posts':posts}
		return render(request,"post/list.html",context)


def post_detail_view(request, post_id):
		if request.method == "POST":
			return HttpResponse(status=400)
		else:
			post = get_object_or_404(GeneralPost,id=post_id)	
			tags = FilterTagRelation.objects.filter(general_post_id=post_id)
			delete_form = GeneralPostDeleteForm()
			context = {
				"delete_form": delete_form,
				"post" : post,
				"tags": tags	
			}			
		return render (request,"post/detail.html", context) 
	
@login_required
def post_create_view(request):
	if request.method == "POST":
		form = GeneralPostCreateAlterForm(request.POST)
		if form.is_valid():
			post = GeneralPost(
				author = request.user,
				title = form.cleaned_data['title'],
				content = form.cleaned_data['content'],
				)
			if "publish" in request.POST:
				post.published = True
			elif "save" in request.POST:
				post.published = False
			post.save()
			for tag in form.cleaned_data['tag']:
				tag_obj, created = Tag.objects.get_or_create(name=tag[1:],slug=tag[1:])
				FilterTagRelation.objects.get_or_create(filter_tag_id=tag_obj.id,general_post_id=post.id)
				return redirect(reverse_lazy('posts:detail', kwargs={"post_id":post.id}))
		else:
			messages.warning(request, 'The form is not vaild')
	else:
		form = GeneralPostCreateAlterForm()
	return render(request,'post/create.html', {'form': form})

@login_required
def post_edit_view(request, post_id):
	if request.method == "POST":
		edit_post = get_object_or_404(GeneralPost, id=post_id)
		edit_form = GeneralPostCreateAlterForm()
	else:
		edit_post = get_object_or_404(GeneralPost, id=post_id)
		filtered_edit_post= FilterTagRelation.objects.filter(general_post_id=edit_post.id)
		tags = str()
		for tag in filtered_edit_post:
			tag = tag.filter_tag.name
			tags = tags + '#' + tag + ' '
		tags = tags[:-1]
		edit_form = GeneralPostCreateAlterForm(
			initial={'title':edit_post.title,'content':edit_post.content, 'tag': tags})
		edit_post.save()
	context = {
				"edit_post" : edit_post, 
				"edit_form" : edit_form
			}
	return render(request, 'post/edit.html', context)

	
@login_required
def post_save_edited_view(request, post_id):
	if request.method == "POST":
		edit_post = get_object_or_404(GeneralPost, id=post_id)
		edit_form = GeneralPostCreateAlterForm(request.POST, instance=edit_post)
		context = {'edit_post' : edit_post, 
				   'edit_form' : edit_form
				}
		print('POST')
		if edit_form.is_valid():
			print('VALID')
			edited_post = edit_form.save()
			after_tags = {tag[1:] for tag in edit_form.cleaned_data['tag']}
			before_filter = FilterTagRelation.objects.select_related('filter_tag').filter(general_post_id=post_id)
			before_tags = {tag.filter_tag.name for tag in before_filter}
			for tag in after_tags.difference(before_tags):
				tag_obj, created = Tag.objects.get_or_create(name=tag, slug=tag)
				FilterTagRelation.objects.get_or_create(filter_tag_id=tag_obj.id, general_post_id=edited_post.id)
			for tag in before_tags.difference(after_tags):
				tag_obj, created = Tag.objects.get_or_create(name=tag, slug=tag)
				FilterTagRelation.objects.filter(filter_tag_id=tag_obj.id, general_post_id=edited_post.id).delete()
			return redirect(reverse_lazy('posts:detail', kwargs={"post_id":edited_post.id}))
		else:
			raise forms.ValidationError('The form is not valid')
	else:
		return redirect(reverse_lazy('posts:detail', kwargs={"post_id":edited_post.id}))

@login_required
def post_delete_view(request, post_id):
	if request.method == "POST":
		delete_form = GeneralPostDeleteForm(request.POST)
		if delete_form.is_valid():
			del_post = get_object_or_404(GeneralPost, id=post_id)
			if del_post.author_id == request.user.id:
				del_post.delete()
			else:
				return HttpResponse(status=403)
		else:
			return HttpResponse(status=400)
	else:
		delete_form = GeneralPostDeleteForm()
	context = {'delete_form':delete_form}
	return redirect('/posts/user_post_list')


def tag_related_post_list_view(request,tag_slug):
		if request.method == "POST":
			return HttpResponse(status=400)
		else:
			tag_model = get_object_or_404(Tag, slug=tag_slug)
			related = FilterTagRelation.objects.filter(filter_tag_id=tag_model.id).values_list('general_post_id')
			generalpost = GeneralPost.objects.filter(published=True).values_list('id')
			generalpost = generalpost.intersection(related)
			generalpost = GeneralPost.objects.filter(id__in=generalpost)
			paginator = Paginator(generalpost, 6)
			# print(paginator)
			page = request.GET.get('page')
			try:
				related_published_post = paginator.page(page)
			except PageNotAnInteger:
				related_published_post = paginator.page(1)
			except EmptyPage:
				related_published_post = paginator.page(paginator.num_pages)
			context = {
						'generalpost':generalpost,
						'related': related,
						'related_published_post' : related_published_post
					}
			return render (request,"post/tag_related_post_list.html", context)

User = get_user_model()
def author_post_list_view(request, author_slugname):
		if request.method == "GET":
			author =get_object_or_404(User, slug_name_for_url = author_slugname)
			post_list = GeneralPost.objects.filter(author_id=author.id,published=True)
			paginator = Paginator(post_list, 6)
			page = request.GET.get('page')
			try:
				author_posts = paginator.page(page)
			except PageNotAnInteger:
				author_posts = paginator.page(1)
			except EmptyPage:
				author_posts = paginator.page(paginator.num_pages)
			context = {'author_posts':author_posts}		
			return render(request,'post/author_post_list.html',context)
		else:
			raise Http403




