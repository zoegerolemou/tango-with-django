from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]	
	context_dict = {'categories': category_list, 'pages': page_list}
	visits = request.session.get('visits')
	
	if not visits:
		visits = 1

	reset_last_visit_time = False
	last_visit = request.session.get('last_visit')
	
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).days > 0:
			visits = visits + 1
			reset_last_visit_time = True

	else:
		reset_last_visit_time = True
	
	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits

	context_dict['visits'] = visits	
	response = render(request, 'rango/index.html', context_dict)

	return response

def about(request):
	context_dict = {'boldmessage': "I am bold font from the context"}

	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0

	return render(request, 'rango/about.html', {'visits': count})

def category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug = category_name_slug)
		context_dict['category_name'] = category.name
		pages = Page.objects.filter(category = category)
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_slug'] = category_name_slug
	except Category.DoesNotExist:
		pass

	return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
	
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	
	else:
		form = CategoryForm()

	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug = category_name_slug)
	except:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit = False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	context_dict = {'form': form, 'category': cat}

	return render(request, 'rango/add_page.html', context_dict)

@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})



