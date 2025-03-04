from django.urls import path
from . import views
urlpatterns = [
    # -------AUTH-------
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # ------HOME-------
    path('', views.homepage, name='homepage'),
    path('create_profile/', views.create_profile, name='create_profile'),
    # -------CHAT--------
    path('create_chatroom/', views.create_chatroom, name='create_chatroom'),
    path('join_chatroom/', views.join_chatroom, name='join_chatroom'),
    # -----------MESSAGE------------
    path('chat/<int:chat_id>', views.view_chat, name='view_chat' )
]
