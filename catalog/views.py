from django.shortcuts import render, redirect
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.
@login_required
def index(request):
    query = request.GET.get('q')
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query))

    num_books = Book.objects.all().count()
    num_instence= BookInstance.objects.all().count()
    num_instence_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors= Author.objects.all().count()
    num_genres_drama= Genre.objects.filter(name__exact='דרמה').count()
    num_genres_action= Genre.objects.filter(name__exact='מתח').count()
    num_visits=request.session.get('num_visits',0)
    num_visits+=1
    request.session['num_visits']=num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instence,
        'num_instances_available': num_instence_available,
        'num_authors': num_authors,
        'num_genres_drama':num_genres_drama,
        'num_genres_action':num_genres_action,
        'num_visits':num_visits,
        'books': books,
        'query': query,

    }
    return render(request,'index.html', context=context)


@property
def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

  


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
    
 #view for the borrower
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

#the disply for library staf
class LoanedBooksByStafListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_stef.html'
    context_object_name = 'bookinstance_list'
    paginate_by = 10

    def get_queryset(self):
       qs = BookInstance.objects.filter(status__exact='o').order_by('due_back')
       print(">>> FOUND:", qs)
       return qs
