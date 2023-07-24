from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.index, name='Home'),
    path('<slug:url>/', views.checkUrl),
    path('Auth/login/', views.login, name='Login'),
    path('Auth/register/', views.register, name='Register'),
    path('verify/<slug:link>/', views.verify),
    path('Auth/forgotemail/', views.forgot_email, name='Forgotemail'),
    path('resetpassword/<slug:link>/', views.Resetpassword, name='Resetpassword'),

    # User dash board Routes....
    path('User/dashboard', views.dashboard, name='Dashboard'),
    path('User/logout', views.logout, name='Logout'),
    path('User/urls/', views.Urls, name='Urls'),
    path('User/create/url', views.create_url, name='Create_url'),
    path('User/delete/url/<slug:surl>', views.delete_url, name='Delete_url'),
    path('User/edit/<str:surl>', views.edit_url, name='Edit_url'),
    path('User/update/<str:surl>', views.update_url, name='Update_url'),
    path('User/settings', views.user_settings, name='Settings'),
    path('User/qrcodes', views.qrcodes, name='Qrcodes'),
    path('User/changepassword', views.change_password, name='Change_password'),
    path('User/createqr/<slug:surl>', views.create_qr, name='Create_qr')

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
