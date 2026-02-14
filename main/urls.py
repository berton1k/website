from django.urls import path
from . import views
from .views import list_curators, stats_page, api_stats
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.index, name="index"),

    # LOGIN
    path("login/", views.login, name="login"),          # GET (страница)
    path("login/api/", views.login_view, name="login_api"),  # POST (AJAX)

    path("logout/", views.logout_view, name="logout"),

    # API
    path("api/curator/sync/", views.sync_curator),
    path("api/curator/remove/", views.remove_curator),
    path("api/curator/list/", list_curators),
    path("api/curator/delete/<str:discord_id>/", views.delete_curator),

    # DISCORD
    path("login/discord/", views.discord_login, name="discord_login"),
    path("login/discord/callback/", views.discord_callback, name="discord_callback"),
    path("login/clear-error/", views.clear_login_error, name="clear_login_error"),
    path("login/clear-success/", views.clear_login_success),
    
    # pages
    path("settings/", views.settings_view, name="settings"),
    path("suggestions/", views.suggestions, name="suggestions"),
    path("viewed/", views.viewed, name="viewed"),
    path("move/<int:pk>/", views.move_post, name="move_post"),
    path("music/", TemplateView.as_view(template_name="main/music.html"), name="music"),
    
    # stats
    path('stats/', stats_page, name='stats'),
	path('api/stats/', api_stats, name='api_stats'),
    path('api/servers/', views.api_servers),
    path("api/backups/", views.api_backups),
	path('api/backup/create/', views.api_backup_create),
	path('api/backup/restore/', views.api_backup_restore),
	path('api/mass-status/', views.api_mass_status),
	path("api/server/sync/", views.api_server_sync),
    path("api/backup/finish/", views.api_backup_finish),
    path("api/backup/status/", views.api_backup_status),
    path("api/servers/sync/", views.api_servers_sync),
    path("api/clear/", views.api_clear_server),
    
    # clear
    path("clear/", views.clear_page, name="clear"),
    path("api/clear/", views.api_clear_server),
]
