from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from VoteSimple import settings
from VoteWebCore import views, error_views
from VoteWebCore.api_views import APIViews

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
      path('login', views.LoginView.as_view()),
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
      path('api/get-question/<int:question_id>', APIViews.Question.Get.as_view()),
      path('api/save-question', APIViews.Question.Save.as_view()),
      path('api/upload/<str:upload_as>', APIViews.Upload.as_view()),
      path('api/favourites/<str:action>/<int:voting_id>', APIViews.Favourites.as_view()),
      path('api/remove/<str:model>/<int:model_id>', APIViews.Remove.as_view()),

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

