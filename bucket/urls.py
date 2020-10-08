from django.urls import path
from . import views

app_name = 'bucket'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    # path('delete/<bucket>', views.DeleteBucket.as_view(), name='delete_bucket'),
    # path('<bucket>/show', views.ShowBucket.as_view(), name='show_bucket'),
    path('dowload/', views.DownloadFile.as_view(), name='download_file'),
    path('delete/<bucket>/<file>', views.DeleteFile.as_view(), name='delete_file'),
    # path('upload-file/', views.UploadFile.as_view(), name='upload_file'),
    path('file/analyze', views.RekognitionImage.as_view(), name='rekognition-file'),

]
