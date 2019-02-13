from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from VoteSimple import settings
from VoteWebCore import views
from VoteWebCore.views import main, auth, error, api, voting

handler400 = error.error_bad_request
handler403 = error.error_forbidden
handler404 = error.error_not_found
handler500 = error.error_internal

urlpatterns = [

      # Admin module
      path('admin/', admin.site.urls),

      # Main module
      path('', main.index),
      path('votings', main.votings),
      path('profile/<str:username>', main.profile),
      path('settings', main.settings),
      path('418', error.error_not_a_teapot),

      # Ajax API module
      path('api/get-question/<int:question_id>', api.get_question),
      path('api/save-question', api.save_question),
      path('api/upload/<str:upload_as>', api.upload),
      path('api/favourites/<str:action>/<int:voting_id>', api.favourites),
      path('api/remove/<str:model>/<int:model_id>', api.remove),

      # Auth module
      path('login', auth.login),
      path('logout', auth.logout),
      path('register', auth.register),
      path('remove-account', auth.remove_account),

      # Voting module
      path('voting/<int:voting_id>', voting.view),
      path('voting/<int:voting_id>/<str:action>', voting.view),
      path('voting/create', voting.create),

      # Media & static module
      re_path(r'^uploads/(?P<path>.*)$', serve, {
          'document_root': settings.MEDIA_ROOT,
      }),
      re_path(r'^static/(?P<path>.*)$', serve, {
          'document_root': settings.STATIC_ROOT,
      }),
    ]

