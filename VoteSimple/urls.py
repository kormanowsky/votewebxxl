from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from VoteSimple import settings
from VoteWebCore import views
from VoteWebCore.views import main, auth, error, api

handler400 = error.error_bad_request
handler403 = error.error_forbidden
handler404 = error.error_not_found
handler500 = error.error_internal

urlpatterns = [
      # Index view
      path('', main.index),
      # Admin
      path('admin/', admin.site.urls),

      # Votings list & search
      path('votings', main.votings),

      # Auth module
      path('login', auth.login),
      path('logout', auth.logout),
      path('register', auth.register),
      path('remove-account', auth.remove_account),

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
      path('api/get-question/<int:question_id>', api.get_question),
      path('api/save-question', api.save_question),
      path('api/upload/<str:upload_as>', api.upload),
      path('api/favourites/<str:action>/<int:voting_id>', api.favourites),
      path('api/remove/<str:model>/<int:model_id>', api.remove),

      # Error 418 view )))
      path('418', error.error_not_a_teapot),

      # Media
      re_path(r'^uploads/(?P<path>.*)$', serve, {
          'document_root': settings.MEDIA_ROOT,
      }),
      re_path(r'^static/(?P<path>.*)$', serve, {
          'document_root': settings.STATIC_ROOT,
      }),
    ]

