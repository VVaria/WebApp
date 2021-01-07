from app.models import Author, Tag


def right_column(request):
    return {
        "popular_tags": Tag.objects.popular_tags(),
        "popular_members": Author.objects.popular_users()
    }
