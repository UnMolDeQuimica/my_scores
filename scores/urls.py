from django.urls import path
from . import views

urlpatterns = [
    # Landing & Auth
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Main views
    path('viewer/', views.score_viewer, name='score_viewer'),
    path('upload/', views.upload_score, name='upload_score'),
    path('list/', views.score_list, name='score_list'),
    path('groups/', views.group_list, name='group_list'),

    # Score API
    path('api/scores/', views.api_scores, name='api_scores'),
    path('scores/<int:pk>/file/', views.score_file, name='score_file'),
    path('scores/<int:pk>/update/', views.score_update, name='score_update'),
    path('scores/<int:pk>/delete/', views.score_delete, name='score_delete'),

    # Group API
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
]
