from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from app.models import Question, Answer, Author
from app.forms import LoginForm, RegisterForm, SettingsForm, AnswerForm, AskQuestion
from django.contrib import auth
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def pagination(object_list, request, per_page=10):
    p = request.GET.get('page')
    paginator = Paginator(object_list, per_page)

    try:
        content = paginator.page(p)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)

    return content


def new_questions(request):
    return render(request, "hot_questions.html", {
        'questions': pagination(Question.objects.new().prefetch_related('likequestion_set'), request),
        'style': True,
        'type': 'new'
    })


def hot_questions(request):
    return render(request, "hot_questions.html", {
        'questions': pagination(Question.objects.hot().prefetch_related('likequestion_set'), request),
        'style': True,
        'type': 'hot'
    })


def tag_questions(request, tag):
    return render(request, "hot_questions.html", {
        'questions': pagination(Question.objects.tag(tag), request),
        'style': True
    })


def author_questions(request, author):
    return render(request, "hot_questions.html", {
        'questions': pagination(Question.objects.author(author).prefetch_related('likequestion_set'), request),
        'style': True
    })


@login_required
def add_question(request):
    if request.method == 'POST':
        form = AskQuestion(data=request.POST, author=request.user.author)
        if form.is_valid():
            question = form.save()
            return redirect(reverse('question', kwargs={'id': question.id}))

    else:
        form = AskQuestion(None)

    return render(request, 'add_question.html', {
        'form': form
    })


def question_answer(request, pk):
    last_id = Question.objects.latest('id').pk
    if pk > last_id:
        pk = last_id

    question = get_object_or_404(Question, id=pk)
    if request.method == 'POST':
        form = AnswerForm(data=request.POST, author=request.user.author, question=question)
        if form.is_valid():
            form.save()
            return redirect(reverse('question', kwargs={'id': pk}) + '?page=last')

    else:
        form = AnswerForm(None, None)
    return render(request, "question_answer.html", {
        'questions': Question.objects.one_question(pk),
        'style': False,
        'comments': pagination(Answer.objects.answers(pk), request, per_page=3),
        'form': form
    })


@login_required
def settings_page(request):
    if request.method == 'POST':
        form = SettingsForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()

            return redirect(reverse('settings'))

    else:
        user_data = {
            'username': request.user.username,
            'first_name': request.user.first_name,
            'email': request.user.email
        }

        form = SettingsForm(initial=user_data)

    return render(request, 'settings_page.html', {
        'form': form
    })


def login_page(request):
    if request.method == "GET":
        form = LoginForm()
        if request.GET.get('next') is not None:
            request.session['next_page'] = request.GET.get('next')
    else:
        form = LoginForm(data=request.POST)
        next_page = request.session.pop('next_page', '/')
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect(next_page)
    return render(request, "login_page.html", {'form': form})


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', '/'))


def signup_page(request):
    if request.method == 'GET':
        form = RegisterForm()
        if request.GET.get('next') is not None:
            request.session['next_page'] = request.GET.get('next')
    else:
        next_page = request.session.pop('next_page', '/')
        form = RegisterForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            auth_data = {
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password1']
            }
            user = auth.authenticate(request, **auth_data)
            if user is not None:
                auth.login(request, user)
                return redirect(next_page)
    return render(request, "signup_page.html", { 'form': form })
