from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

# Create your views here.
def index(request):
    num_books = Book.objects.all().count()
    num_instence= BookInstance.objects.all().cuont()
    num_instence_available=BookInstance.objects.filter(status__exact='a').cuont()
    num_auther= Author.objects.all().count()

    context = {
        'num_books': num_books,
        'num_instence': num_instence,
        'num_instence_available': num_instence_available,
        'num_auther': num_auther,
    }
    return render(request,'index.html', context=context)

