from django.urls import path
from .views import *

urlpatterns = [
    path('', inbox_view, name="inbox"),
    path('c/<conversation_id>/', inbox_view, name="inbox"),
    path('search-users/', search_users, name="inbox-searchusers"),
    path('new-message/<recipient_id>/', new_message, name="inbox-newmessage"),
    path('new-reply/<conversation_id>/', new_reply, name="inbox-newreply"),
    
]