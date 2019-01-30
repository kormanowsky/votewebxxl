"""VoteSimple URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from VoteWebCore import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('quiz_list', views.quiz_list),
    path('quiz_task', views.quiz_task),
    path('quiz_save', views.quiz_save),

    # Auth module
    path('login', auth_views.LoginView.as_view()),
    path('logout', views.logout),
    path('register', views.register),


    # Profile Page
    path('profile/<str:username>', views.profile),

    # Single quiz
    path('quiz/<int:quiz_id>', views.quiz),
    path('quiz/<int:quiz_id>/<str:action>', views.quiz)
]
