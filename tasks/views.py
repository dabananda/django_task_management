from django.shortcuts import render, redirect
from tasks.forms import TaskModelForm, TaskDetailModelForm
from tasks.models import Task, Project
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from users.views import is_admin
from django.urls import reverse_lazy


view_project_decorators = [login_required, permission_required(
    "projects.view_project", login_url='no-permission')]


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()


@method_decorator(user_passes_test(is_manager, login_url='no-permission'), name='dispatch')
class ManagerDashboardView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "dashboard/manager-dashboard.html"
    context_object_name = 'tasks'

    def get_queryset(self):
        type = self.request.GET.get('type', 'all')
        base_query = Task.objects.select_related(
            'details').prefetch_related('assigned_to')

        filter_map = {
            'completed': Q(status='COMPLETED'),
            'in-progress': Q(status='IN_PROGRESS'),
            'pending': Q(status='PENDING'),
        }

        return base_query.filter(filter_map.get(type, Q())) if type in filter_map else base_query.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["counts"] = Task.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            pending=Count('id', filter=Q(status='PENDING')),
        )
        context["role"] = "manager"
        return context


@method_decorator(user_passes_test(is_employee, login_url='no-permission'), name='dispatch')
class EmployeeDashboard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "dashboard/user-dashboard.html")


class CreateTask(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'tasks.add_task'
    login_url = 'sign-in'
    template_name = 'task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form', TaskModelForm())
        context['task_detail_form'] = kwargs.get(
            'task_detail_form', TaskDetailModelForm())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            context = self.get_context_data(
                task_form=task_form, task_detail_form=task_detail_form)
            return render(request, self.template_name, context)


class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(
                instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)

        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', self.object.id)
        return redirect('update-task', self.object.id)


class DeleteTask(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = 'tasks.delete_task'
    login_url = 'no-permission'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('manager-dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Task Deleted Successfully')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception:
            messages.error(request, 'Something went wrong')
            return redirect('manager-dashboard')


@method_decorator(view_project_decorators, name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_task.html'

    def get_queryset(self):
        queryset = Project.objects.annotate(
            num_task=Count('task')).order_by('num_task')
        return queryset


class TaskDetail(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')

    return redirect('no-permission')
