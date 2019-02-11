from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.static import serve

from VoteSimple import settings
from VoteWebCore import views, api_views, error_views

handler400 = error_views.error_bad_request
handler403 = error_views.error_forbidden
handler404 = error_views.error_not_found
handler500 = error_views.error_internal

urlpatterns = [
<<<<<<< HEAD
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
      path('api/get-question/<int:question_id>', api_views.get_question),
      path('api/save-question', api_views.save_question),
      path('api/upload/<str:upload_as>', api_views.upload),
      path('api/favourites/<str:action>/<int:voting_id>', api_views.favourites),
      path('api/remove/<str:model>/<int:model_id>', api_views.remove),

      # Error 418 view )))
      path('418', error_views.error_not_a_teapot),

      # Media
      re_path(r'^uploads/(?P<path>.*)$', serve, {
          'document_root': settings.MEDIA_ROOT,
      }),
      re_path(r'^static/(?P<path>.*)$', serve, {
          'document_root': settings.STATIC_ROOT,
      }),
    ]

