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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static

from VoteSimple import settings
from VoteWebCore import views, api_views, error_views

handler400 = error_views.error_bad_request
handler403 = error_views.error_forbidden
handler404 = error_views.error_not_found
handler500 = error_views.error_internal

urlpatterns = [
    # Index view
    path('', views.index),
    # Admin
    path('admin/', admin.site.urls),

    # Votings list & search
    path('votings', views.votings),

    # Auth module
    path('login', auth_views.LoginView.as_view()),
    path('logout', views.logout),
    path('register', views.register),
    path('remove-account', views.remove_account),

    # Profile Page
    path('profile/<str:username>', views.profile),

    # Single voting
    path('voting/<int:voting_id>', views.voting_single),
    path('voting/<int:voting_id>/<str:action>', views.voting_single),

    # Settings
    path('settings', views.settings),

    # Voting create
    path('voting/create', views.voting_create),

    # Ajax API
    path('api/get-question/<int:id>', api_views.get_question),
    path('api/save-question', api_views.save_question),
    path('api/upload/<str:upload_as>', api_views.upload),
    path('api/favourites/<str:action>/<int:voting_id>', api_views.favourites),
    path('api/remove/<str:model>/<int:id>', api_views.remove),

    # Default view
    path(r'', error_views.error_not_found)
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)