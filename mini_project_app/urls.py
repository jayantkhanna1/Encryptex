from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
     # Index page paths
     path('', views.index,name='index'),
     path('login',views.login,name='login'),
     path('signup',views.signup,name='signup'),
     path('signup_user',views.signup_user,name='signup_user'),
     path('login_user',views.login_user,name='login_user'),
     path('otp_check',views.otpcheck,name='otp_check'),
     path('home',views.home,name='home'),
     path('newtalker',views.newtalker,name='newtalker'),
     path('send_message',views.send_message,name='send_message'),
     path('set_all_messages',views.set_all_messages,name='set_all_messages'),
     path('check_for_new_messages',views.check_for_new_messages,name='check_for_new_messages'),
     path('logout',views.logout,name='logout'),
     path('forgot_password', views.forgot_password, name='forgot_password'),
     path('email_check', views.email_check, name='email_check'),
     path('otp_check_forgot_password', views.otp_check_forgot_password, name='otp_check_forgot_password'),
     path('change_password', views.change_password, name='change_password'),
     path('encryptimage', views.encryptimage, name='encryptimage'),
     path('decrypt', views.decrypt, name='decrypt'),
     path('decryptimage', views.decryptimage, name='decryptimage'),
     path('download_decrypted_image/<str:name>', views.download_decrypted_image, name='download_decrypted_image'),


]