# catalog/tests/test_views.py

import datetime
import uuid
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType



from catalog.models import Author, Book, BookInstance, Genre, Language

User = get_user_model()

# ============================================================
# 1️⃣ בדיקות לתצוגת רשימת סופרים (AuthorListView)
# ============================================================

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # יצירת 13 סופרים לבדיקה של עימוד
        for author_id in range(13):
            Author.objects.create(
                first_name=f"Dominique {author_id}",
                last_name=f"Surname {author_id}"
            )

    def test_url_exists(self):
        """בודקת שהעמוד נגיש ישירות לפי הכתובת"""
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_url_by_name(self):
        """בודקת שהעמוד נגיש לפי שם הנתיב"""
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        """בודקת שהתבנית הנכונה מוצגת"""
        response = self.client.get(reverse('authors'))
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        """בודקת שעימוד תקין – 10 פריטים בעמוד הראשון"""
        response = self.client.get(reverse('authors'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['author_list']), 10)

    def test_second_page_has_remaining(self):
        """בודקת שהעמוד השני מציג את 3 הסופרים הנותרים"""
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(len(response.context['author_list']), 3)


# ============================================================
# 2️⃣ בדיקות לתצוגת ספרים לפי משתמש מחובר (LoanedBooksByUserListView)
# ============================================================

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # יוצרים שני משתמשים
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

        # יוצרים ספר בסיסי
        author = Author.objects.create(first_name='John', last_name='Writer')
        genre = Genre.objects.create(name='Fantasy')
        language = Language.objects.create(name='English')
        book = Book.objects.create(
            title='Book Title',
            summary='Summary text',
            isbn='ABCDEFG',
            author=author,
            language=language,
        )
        book.genre.set([genre])

        # יוצרים 30 עותקים של הספר (BookInstance)
        for i in range(30):
            borrower = self.user1 if i % 2 else self.user2
            BookInstance.objects.create(
                book=book,
                imprint='Imprint 2025',
                due_back=timezone.localtime() + datetime.timedelta(days=i % 5),
                borrower=borrower,
                status='m'  # Maintenance
            )

    def test_redirect_if_not_logged_in(self):
        """בודקת שמשתמש לא מחובר מופנה לעמוד התחברות"""
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_correct_template(self):
        """בודקת שמשתמש מחובר רואה את הדף הנכון"""
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        """בודקת שרק ספרים במצב 'on loan' מוצגים"""
        self.client.login(username='user1', password='pass1')
        # בהתחלה כולם ב-maintenance → אין ספרים ברשימה
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # משנים 10 ספרים ל'on loan'
        for book in BookInstance.objects.all()[:10]:
            book.status = 'o'
            book.save()

        response = self.client.get(reverse('my-borrowed'))
        for item in response.context['bookinstance_list']:
            self.assertEqual(item.status, 'o')
            self.assertEqual(item.borrower, response.context['user'])

    def test_books_ordered_by_due_date(self):
        """בודקת שהספרים ממוינים לפי תאריך החזרה"""
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('my-borrowed'))

        last_date = None
        for book in response.context['bookinstance_list']:
            if last_date:
                self.assertTrue(last_date <= book.due_back)
            last_date = book.due_back


# ============================================================
# 3️⃣ בדיקות לתצוגת חידוש ספר (renew_book_librarian)
# ============================================================

class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # שני משתמשים
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

        # מתן הרשאה ל-user2 לחדש ספרים
        permission = Permission.objects.get(name='Set book as returned')
        self.user2.user_permissions.add(permission)

        # יצירת ספר
        author = Author.objects.create(first_name='John', last_name='Writer')
        genre = Genre.objects.create(name='Drama')
        language = Language.objects.create(name='English')
        book = Book.objects.create(
            title='Book Title',
            summary='Summary',
            isbn='ABCDEFG',
            author=author,
            language=language
        )
        book.genre.set([genre])

        # שני עותקים – אחד לכל משתמש
        date = datetime.date.today() + datetime.timedelta(days=5)
        self.instance1 = BookInstance.objects.create(
            book=book, imprint='Imprint', due_back=date,
            borrower=self.user1, status='o'
        )
        self.instance2 = BookInstance.objects.create(
            book=book, imprint='Imprint', due_back=date,
            borrower=self.user2, status='o'
        )

    def test_redirect_if_not_logged_in(self):
        """לא מחובר → מופנה לעמוד התחברות"""
        response = self.client.get(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_no_permission(self):
        """מחובר בלי הרשאה → 403"""
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_access_with_permission(self):
        """מחובר עם הרשאה → גישה מותרת"""
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('renew-book-librarian',
                kwargs={'pk': self.instance2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_invalid_pk_returns_404(self):
        """pk לא קיים → 404"""
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('renew-book-librarian',
                kwargs={'pk': uuid.uuid4()}))
        self.assertEqual(response.status_code, 404)

    def test_form_initial_date_is_3_weeks(self):
        """הטופס נפתח עם תאריך עתידי של 3 שבועות"""
        self.client.login(username='user2', password='pass2')
        response = self.client.get(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}))
        date_expected = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_expected)

    def test_valid_post_redirects(self):
        """שליחה תקינה של טופס → מפנה לעמוד borrowed"""
        self.client.login(username='user2', password='pass2')
        valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}),
                {'renewal_date': valid_date}, follow=True)
        self.assertRedirects(response, '/catalog/')

    def test_invalid_date_past(self):
        """תאריך בעבר → שגיאה בטופס"""
        self.client.login(username='user2', password='pass2')
        past_date = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}),
                {'renewal_date': past_date})
        self.assertFormError(response.context['form'], 'renewal_date',
                             'Invalid date - renewal in past')

    def test_invalid_date_future(self):
        """תאריך רחוק מדי בעתיד → שגיאה בטופס"""
        self.client.login(username='user2', password='pass2')
        invalid_date = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian',
                kwargs={'pk': self.instance1.pk}),
                {'renewal_date': invalid_date})
        self.assertFormError(response.context['form'], 'renewal_date',
                             'Invalid date - renewal more than 4 weeks ahead')
        

# ============================================================
# 3️⃣ בדיקות ליצירת סופר חדש (create auther)
# ============================================================
class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username='test_user1', password='some_password1')
        test_user2 = User.objects.create_user(
            username='test_user2', password='some_password2')

        content_typeAuthor = ContentType.objects.get_for_model(Author)
        permAddAuthor = Permission.objects.get(
            codename="add_author",
            content_type=content_typeAuthor,
        )

        test_user1.user_permissions.add(permAddAuthor)
        test_user1.save()
        test_user2.save()

    def test_forbidden_if_no_permission(self):
        """מחובר בלי הרשאה → 403"""
        self.client.login(username='test_user2', password='some_password2')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_access_with_permission(self):
        """מחובר עם הרשאה → גישה מותרת"""
        self.client.login(username='test_user1', password='some_password1')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_correct_template(self):
        """בודקת שמשתמש מחובר רואה את הדף הנכון"""
        self.client.login(username='test_user1', password='some_password1')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_form_initial_date_of_death_is_11_11_2023(self):
        """הטופס נפתח עם תאריך החל מ11.11.23"""
        self.client.login(username='test_user1', password='some_password1')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.context['form'].initial['date_of_death'], '11/11/2023')


    def test_valid_post_redirects(self):
        """שליחה תקינה של טופס → מפנה לעמוד author_detail"""
        self.client.login(username='test_user1', password='some_password1')
        response = self.client.post(resverse('author-create'),
        {'first_name': 'John', 'last_name': 'Doe', 'date_of_birth': '2000-01-01'})
        self.assertRedirects(response, reverse('author-detail', args=[1]))



