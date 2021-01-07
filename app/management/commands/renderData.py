from django.core.management.base import BaseCommand
from app.models import Question, Author, Tag, Answer, LikeAnswer, LikeQuestion
from django.contrib.auth.models import User
from random import randint, choice, choices
from itertools import islice
from faker import Faker

f = Faker()

small = [100, 100, 1000, 10000, 10000, 10000]
medium = [1000, 1000, 10000, 100000, 100000, 1000000]
large = [10000, 10000, 100000, 1000000, 1000000, 10000000]


class Command(BaseCommand):
    help = 'Filling data with random values'

    def add_arguments(self, parser):
        parser.add_argument('--db_size', type=str, help="DB size: small, medium, large")
        parser.add_argument('--users', type=int, help='Users size')
        parser.add_argument('--tags', type=int, help='Tags size')
        parser.add_argument('--questions', type=int, help='Questions size')
        parser.add_argument('--answers', type=int, help='Answers size')
        parser.add_argument('--likes_questions', type=int, help='Questions likes size')
        parser.add_argument('--likes_answers', type=int, help='Answers likes size')

    def create(self, Obj, objs):
        slice_size = 500
        while True:
            slices = list(islice(objs, slice_size))
            if not slices:
                break
            Obj.objects.bulk_create(slices, slice_size)

    def fill_authors(self, cnt):
        if cnt is None:
            return False
        users = (
            User(
                username=f.unique.first_name(),
                email=f.email()
            )
            for i in range(cnt)
        )

        self.create(User, users)
        user_ids = list(User.objects.values_list('id', flat=True))
        authors = (
            Author(
                user_id=user_ids[i],
                name=f.name()
            )
            for i in range(cnt)
        )
        self.create(Author, authors)

    def fill_tags(self, cnt):
        if cnt is None:
            return False
        tags = (
            Tag(
                tag=f.unique.word()
            )
            for i in range(cnt)
        )
        self.create(Tag, tags)

    def fill_questions(self, cnt):
        author_ids = list(
            Author.objects.values_list(
                'id', flat=True
            )
        )
        authors = choices(author_ids, k=cnt)
        questions = (
            Question(
                author_id=authors[i],
                text='. '.join(f.sentences(f.random_int(min=3, max=20))),
                title=f.sentence()[:128],
                date=f.date_time_this_month()
            )
            for i in range(cnt)
        )
        self.create(Question, questions)

        tag_ids = list(Tag.objects.values_list('id', flat=True))
        tags_count = dict.fromkeys(tag_ids, 0)

        author_count = dict.fromkeys(author_ids, 0)
        for question in Question.objects.all():
            author_count[question.author.id] += 1
            for tag in set(choices(tag_ids, k=randint(0, 10))):
                tags_count[tag] += 1
                question.tags.add(tag)

        tags_list = list(Tag.objects.all())
        authors_list = list(Author.objects.all())
        for tag in tags_list:
            tag.count = tags_count[tag.pk]
        for author in authors_list:
            author.count += author_count[author.pk]
        Tag.objects.bulk_update(tags_list, ['count'])
        Author.objects.bulk_update(authors_list, ['count'])

    def fill_answers(self, cnt):
        if cnt is None:
            return False

        question_ids = list(Question.objects.values_list('id', flat=True))
        author_ids = list(Author.objects.values_list('id', flat=True))
        authors = choices(author_ids, k=cnt)
        answers = (
            Answer(
                question_id=choice(question_ids),
                author_id=authors[i],
                text='. '.join(f.sentences(f.random_int(min=2, max=5))),
            )
            for i in range(cnt)
        )
        self.create(Answer, answers)

        authors_count = dict.fromkeys(author_ids, 0)
        for i in authors:
            authors_count[i] += 1

        authors_list = list(Author.objects.all())
        for author in authors_list:
            author.count += authors_count[author.pk]
        Author.objects.bulk_update(authors_list, ['count'])

    def fill_likes_questions(self, cnt):
        if cnt is None:
            return False
        author_ids = list(Author.objects.values_list('id', flat=True))
        question_ids = list(Question.objects.values_list('id', flat=True))
        questions = choices(question_ids, k=cnt)
        reactions = choices([True, True, False, True, False, True, False, True, True, True], k=cnt)
        likes = (
            LikeQuestion(
                author_id=choice(author_ids),
                question_id=questions[i],
                state=reactions[i]
            )
            for i in range(cnt)
        )
        self.create(LikeQuestion, likes)

        questions_count = dict.fromkeys(question_ids, 0)
        for i in range(cnt):
            if reactions[i]:
                questions_count[questions[i]] += 1
            else:
                questions_count[questions[i]] -= 1

        questions_list = list(Question.objects.all())
        for question in questions_list:
            question.rating = questions_count[question.pk]
        Question.objects.bulk_update(questions_list, ['rating'])

    def fill_likes_answers(self, cnt):
        if cnt is None:
            return False
        author_ids = list(Author.objects.values_list('id', flat=True))
        answer_ids = list(Answer.objects.values_list('id', flat=True))
        answers = choices(answer_ids, k=cnt)
        reactions = choices([True, True, False, True, False, True, False, False, True, True], k=cnt)
        likes = (
            LikeAnswer(
                author_id=choice(author_ids),
                answer_id=answers[i],
                state=reactions[i]
            )
            for i in range(cnt)
        )

        self.create(LikeAnswer, likes)

        answers_count = dict.fromkeys(answer_ids, 0)
        for i in range(cnt):
            if reactions[i]:
                answers_count[answers[i]] += 1
            else:
                answers_count[answers[i]] -= 1

        answers_list = list(Answer.objects.all())
        for answer in answers_list:
            answer.rating = answers_count[answer.pk]
        Answer.objects.bulk_update(answers_list, ['rating'])

    def handle(self, *args, **options):
        data_size = [options.get('authors'),
                     options.get('tags'),
                     options.get('questions'),
                     options.get('answers'),
                     options.get('likes_questions'),
                     options.get('likes_answers')]

        if options.get('db_size') == 'small':
            data_size = small
        elif options.get('db_size') == 'medium':
            data_size = medium
        elif options.get('db_size') == 'large':
            data_size = large

        self.fill_authors(data_size[0])
        self.fill_tags(data_size[1])
        self.fill_questions(data_size[2])
        self.fill_answers(data_size[3])
        self.fill_likes_questions(data_size[4])
        self.fill_likes_answers(data_size[5])
