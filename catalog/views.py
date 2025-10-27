from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic

# Create your views here.
def index(request):
    num_books = Book.objects.all().count()
    num_instence= BookInstance.objects.all().count()
    num_instence_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors= Author.objects.all().count()
    num_genres_drama= Genre.objects.filter(name__exact='דרמה').count()
    num_genres_action= Genre.objects.filter(name__exact='מתח').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instence,
        'num_instances_available': num_instence_available,
        'num_authors': num_authors,
        'num_genres_drama':num_genres_drama,
        'num_genres_action':num_genres_action,
    }
    return render(request,'index.html', context=context)

#view for the all books
class BookListView(generic.ListView):
    model=Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model=Book

class AuthorListView(generic.ListView):
    model=Author

class AuthorDetailView(generic.DetailView):
    model=Author


