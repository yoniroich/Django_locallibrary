from django.contrib import admin

# Register your models here.
from .models import Genre, Author, Book, BookInstance, Language

# admin.site.register(Book)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display=('title', 'author', 'disply_genre')
    def disply_genre(self,obj):
        return ','.join(genre.name for genre in obj.genre.all()[:3])
        disply_genre=short.description = 'genre'
# admin.site.register(Author)
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display=('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields=['last_name', 'first_name', ('date_of_birth', 'date_of_death')]
admin.site.register(Genre)
# admin.site.register(BookInstance)
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display=('book', 'status')
admin.site.register(Language)


