from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm


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
    paginate_by = 10


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
    
#create forms
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

   
        if form.is_valid():

            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

    
            return HttpResponseRedirect(reverse('book-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


#create ganric class edit
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse_lazy("author-delete", kwargs={"pk": self.object.pk})
            )
        

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse_lazy("book-delete", kwargs={"pk": self.object.pk})
            )
        

class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = '__all__'
    permission_required = 'catalog.add_BookInstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    fields = ['borrower', 'status', 'due_back']
    permission_required = 'catalog.change_BookInstance'

class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_BookInstance'

    def form_valid(self, form):
        """Prevent deleting a copy if it's on loan"""
        if self.object.status == 'o':
            # redirect back to same page (no deletion)
            return HttpResponseRedirect(
                reverse_lazy("bookinstance-delete", kwargs={"pk": self.object.pk})
            )
        return super().form_valid(form)
            