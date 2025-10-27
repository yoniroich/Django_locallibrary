from django.contrib import admin

# Register your models here.
from .models import Genre, Author, Book, BookInstance, Language
from import_export.admin import ImportExportModelAdmin


# class for Inline

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra=1
    fields=('book', 'status', 'due_back', 'id')

class BookInline(admin.TabularInline):
    model=Book
    extra=0
    fields=('title','summary')

# admin.site.register(Book)
@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    list_display=('id','title', 'author', 'display_genre')
    list_filter=('author',)
    inlines= [BooksInstanceInline]

    def display_genre(self,obj):
        return ','.join(genre.name for genre in obj.genre.all()[:3])
        disply_genre=short.description = 'genre'

  # admin.site.register(Author)
@admin.register(Author)
class AuthorAdmin(ImportExportModelAdmin):
    list_display=('id', 'last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields=['last_name', 'first_name', ('date_of_birth', 'date_of_death')]
    inlines= [BookInline]

admin.site.register(Genre)

@admin.register(BookInstance)
class BookInstanceAdmin(ImportExportModelAdmin):
    list_display = ('book', 'status')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'id')}),
        ('זמינות', {'fields': ('status', 'due_back')}),
    )

    def process_import(self, request, *args, **kwargs):
        """עוקף באג של import_export כשאין request.user"""
        try:
            return super().process_import(request, *args, **kwargs)
        except TypeError:
            import traceback
            traceback.print_exc()
            return super(ImportExportModelAdmin, self).process_import(request, *args, **kwargs)

admin.site.register(Language)







