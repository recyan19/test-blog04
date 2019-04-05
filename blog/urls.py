from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout_view'),
    url(r'^activate/(?P<uid64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('blog/', views.posts_list, name='posts_list_url'),
    path('post/create/', views.PostCreate.as_view(), name='post_create_url'),
    path('post/<str:slug>/addlike/', views.addlike, name='post_like_url'), 
    path('post/<str:slug>/', views.PostDetail.as_view(), name='post_detail_url'),
    path('post/<str:slug>/update/', views.PostUpdate.as_view(), name='post_update_url'),
    path('post/<str:slug>/delete/', views.PostDelete.as_view(), name='post_delete_url'),
]