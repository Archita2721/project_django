from django.urls import path
from . import views
from django.conf import settings  
from django.conf.urls.static import static 
from django.conf.urls import handler404


handler404='cardapp.views.handler404'
handler500='cardapp.views.handler500'

app_name = "main"   

urlpatterns = [
    path("",views.homepage,name="form"),
    path("homepage",views.homepage,name="form"),
    path("addCard",views.addcard,name="addcard"),
    path("register/", views.register, name="register"),
    #path("",views.login_request,name="login"),
    path("login",views.login_request,name="login"),
    path("logout", views.logout_request, name= "logout"),
    path("password_reset", views.password_reset_request, name="password_reset"),  
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("card/<int:id>",views.card,name='card'),
    path("qrcard/<int:id>",views.qrcard,name='qrcard'),
    path("qr_card/<int:id>",views.qr_card,name='qr_card'),
    path("update/<int:id>",views.update,name="update"),
    path("delete/<int:id>",views.delete,name="delete"),
    #path("send",views.send,name="send")
    path("send/<int:id>",views.send,name="send"),
    path("sendmail/<int:id>",views.sendmail,name="sendmail"),
    path("sendmailqr/<int:id>",views.sendmailqr,name="sendmailqr"),
    path("setting",views.setting,name="setting"),
    path("delete",views.delete_account,name='delete_account'),
   
   
]



if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)