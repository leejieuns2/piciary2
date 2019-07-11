from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .models import Blog 
from .forms import BlogForm

@login_required(login_url='login/')
def index(request):
    # blogs = Blog.objects.filter(title=request.GET.get('q'))
    # if(blog.writer == "")
    #     blog.writer = null
    blogs = Blog.objects.filter(writer__contains=request.user.username)
    
    # 검색 기능 구현
    if request.GET.get('q'):
        variable_column = request.GET.get('fd_name')
        search_type = 'contains'
        filter = variable_column + '__' + search_type
        search_blogs = Blog.objects.filter(writer__contains=request.user.username).filter(**{ filter: request.GET.get('q') })
        blog_list = search_blogs
    else :
        blog_list = blogs

    paginator = Paginator(blog_list, 3)
    page = request.GET.get('page')

    try: 
        posts = paginator.get_page(page)
    except PageNotAnInteger:
        posts = page.get_page(1)
    except EmptyPage :
        posts = paginator.get_page(paginator.num_pages)

    return render(request, 'index.html', {'blogs' : blogs, 'posts' : posts})

def new (request):
    # 1. 입력된 내용 처리 : POST
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid(): 
            blog = form.save(commit=False)
            blog.date = timezone.now()
            blog.writer = User.objects.get(username = request.user.get_username())
            blog.save()
            return redirect('/')
            
    # 2. 빈 페이지 띄워주는 기능 : GET
    else:
        form = BlogForm()
        return render(request, 'new.html', {'form': form})

def detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'detail.html', {'blog': blog})

def edit(request, blog_id):

    blog = get_object_or_404(Blog, pk = blog_id)

    if request.method == 'POST':
        form = BlogForm(request.POST, instance = blog)
        if form.is_valid():
            blog = form.save(commit=False)
            if request.FILES['image']:
                myfile = request.FILES['image']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                blog.image = fs.url(filename)
            blog.date = timezone.now()
            blog.save()
            return redirect('/')
    else:
        form = BlogForm(instance=blog)
        return render(request, 'edit.html', {'blog' : blog, 'form' : form})

def delete(request, blog_id):
    blog = get_object_or_404(Blog, pk = blog_id)
    blog.delete()
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        try:
            if request.POST['username'] == '' or request.POST['password'] == '':
                return render(request, 'signup.html', {'error' : '이름, 비밀번호 필수 입력'})
            # 이름이나 비밀번호를 빈칸으로 제출했을 경우
            if request.POST['password'] == request.POST['con_password']:
                user = User.objects.get(username = request.POST['username'])
                return render(request, 'signup.html', { 'error' : '존재하는 아이디입니다.'})
                # 이미 존재하는 이름을 제출할 경우
                # 존재할 경우 DoesNotExist 에러가 발생하기 때문에 에러처리된다.
            else:
                return render(request, 'signup.html', {'error' : "비밀번호, 비밀번호 확인 불일치"})
                # 비밀번호와 비밀번호 확인란이 서로 일치 하지 않을 경우
        except User.DoesNotExist:
            user = User.objects.create_user(request.POST['username'], password=request.POST['password'])

            auth.login(request, user)
            return redirect('/')
    else:
        return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        pw = request.POST['password']

        user = auth.authenticate(request, username = username, password = pw)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error' : '이름, 비밀번호를 확인'})
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')