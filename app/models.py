from django.db import models
from django.contrib.auth.models import User


def upload_avatar(instance, filename):
    return 'avatars/{}/{}'.format(instance.user.id, filename)


class AuthorManager(models.Manager):
    def popular_users(self):
        return self.order_by('-count')[:5]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ID зарегистрированного пользователя')
    name = models.CharField(max_length=50, verbose_name='Имя')
    avatar = models.ImageField(default='static/img/user.png', blank=True, upload_to=upload_avatar, verbose_name='Аватар')
    count = models.IntegerField(default=0, verbose_name='Количество вопросов и ответов у автора')

    objects = AuthorManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class TagManager(models.Manager):
    def popular_tags(self):
        return self.order_by('-count')[:10]


class Tag(models.Model):
    tag = models.CharField(max_length=25, unique=True, verbose_name='Тег')
    count = models.IntegerField(default=0, verbose_name='Количество вопросов по тегу')

    objects = TagManager()

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-date')

    def hot(self):
        return self.order_by('-rating')

    def tag(self, tag):
        return self.filter(tags__tag=tag)

    def author(self, author_id):
        return self.filter(author__user_id=author_id).order_by('-rating')

    def one_question(self, pk):
        return self.filter(id=pk)


class Question(models.Model):
    title = models.CharField(max_length=1024, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def answers_count(self):
        return Answer.objects.answers_count(self.id)

    def all_tags(self):
        return self.tags.all()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class AnswerManager(models.Manager):
    def answers(self, question_id):
        return self.filter(question__id=question_id).order_by('-rating')

    def answers_count(self, question_id):
        return self.filter(question__id=question_id).count()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_correct = models.BooleanField(default=False, verbose_name='Корректность ответа')

    objects = AnswerManager()

    def __str__(self):
        return 'Ответ на вопрос: {}'.format(self.question.title)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class LikeQuestion(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Пользователь, который поставил реакцию')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    state = models.BooleanField(null=True, verbose_name='Какая реакция')

    def __str__(self):
        return 'Реакция на вопрос: {}'.format(self.question.title)

    class Meta:
        verbose_name = 'Реакция на вопрос'
        verbose_name_plural = 'Реакции на вопросы'


class LikeAnswer(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Пользователь, который поставил реакцию')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')
    state = models.BooleanField(null=True, verbose_name='Какая реакция')

    def __str__(self):
        return 'Реакция на ответ к вопросу: {}'.format(self.answer.question.title)

    class Meta:
        verbose_name = 'Реакция на ответ'
        verbose_name_plural = 'Реакции на ответы'
