from django.urls import path
from tasks.views import CreateTask, ViewProject, TaskDetail, UpdateTask, ManagerDashboardView, EmployeeDashboard, DeleteTask, dashboard

urlpatterns = [
    path('manager-dashboard/', ManagerDashboardView.as_view(),
         name="manager-dashboard"),
    path('user-dashboard/', EmployeeDashboard.as_view(), name='user-dashboard'),
    path('create-task/', CreateTask.as_view(), name='create-task'),
    path('view_task/', ViewProject.as_view(), name='view-task'),
    path('task/<int:task_id>/details/',
         TaskDetail.as_view(), name='task-details'),
    path('update-task/<int:id>/', UpdateTask.as_view(), name='update-task'),
    path('delete-task/<int:id>/', DeleteTask.as_view(), name='delete-task'),
    path('dashboard/', dashboard, name='dashboard'),
]
