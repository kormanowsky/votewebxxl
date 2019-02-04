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
    path('vote_list', views.vote_list),
    path('vote_task', views.vote_task),
    path('vote_save', views.vote_save),

    # Auth module
    path('login', auth_views.LoginView.as_view()),
    path('logout', views.logout),
    path('register', views.register),


    # Profile Page
    path('profile/<str:username>', views.profile),

    # Single vote
    path('vote/<int:vote_id>', views.vote),
    path('vote/<int:vote_id>/<str:action>', views.vote),

    # Settings
    path('settings', views.settings),

    # Test form
    path('test-form', views.test_form)
]
