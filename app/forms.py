from django import forms
from django.db.models import F
from app.models import Author, Answer, Question, LikeAnswer, LikeQuestion, Tag
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    first_name = forms.CharField(label="Nickname")
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password1', 'password2', 'avatar']
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }

    def save(self, commit=False):
        user = super().save(commit=True)
        photo = self.files.get('avatar')
        print(photo)
        if photo:
            Author.objects.create(user=user, name=self.cleaned_data.get('first_name'), avatar=photo)
        else:
            Author.objects.create(user=user, name=self.cleaned_data.get('first_name'))
        if commit:
            user.save()
        return user


class AskQuestion(forms.ModelForm):
    tags = forms.CharField()

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6})
        }

    def __init__(self, author, *args, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author
        Author.objects.filter(id=question.author_id).update(count=F('count') + 1)

        if commit:
            question.save()
            for tag in self.cleaned_data['tags'].split(' '):
                try:
                    idtag = Tag.objects.get(tag=tag).id
                    Tag.objects.filter(id=idtag).update(count=F('count') + 1)
                except Tag.DoesNotExist:
                    idtag = Tag.objects.create(name=tag).id
                question.tags.add(idtag)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, question, author, *args, **kwargs):
        self.question = question
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.question = self.question
        answer.author = self.author
        Author.objects.filter(id=answer.author_id).update(count=F('count') + 1)

        if commit:
            answer.save()

        return answer


class SettingsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    first_name = forms.CharField(label="Nickname")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'avatar']

    def save(self, commit=False):
        user = super().save(commit=True)
        photo = self.files.get('avatar')
        if photo:
            author = Author.objects.get(user_id=user.id)
            author.avatar = self.files.get('avatar')
            author.save()

        if commit:
            user.save()

        return user