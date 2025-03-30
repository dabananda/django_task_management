from django.shortcuts import redirect, HttpResponse
from django.contrib.auth.models import Group
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, UpdateView, FormView, ListView, View
from django.utils.decorators import method_decorator


User = get_user_model()


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


class SignUp(FormView):
    template_name = 'registration/register.html'
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password1'))
        user.is_active = False
        user.save()
        messages.success(
            self.request, 'A Confirmation mail sent. Please check your email')
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('sign-in')


class ActivateUserView(View):
    def get(self, request, user_id, token):
        try:
            user = User.objects.get(id=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('sign-in')
            return HttpResponse('Invalid Id or token')
        except User.DoesNotExist:
            return HttpResponse('User not found')


class AdminDashboardView(ListView):
    template_name = 'admin/dashboard.html'
    context_object_name = 'users'

    @method_decorator(user_passes_test(is_admin, login_url='no-permission'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(),
                     to_attr='all_groups')
        ).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'
        return users


class AssignRoleView(FormView):
    template_name = 'admin/assign_role.html'
    form_class = AssignRoleForm
    success_url = reverse_lazy('admin-dashboard')

    @method_decorator(user_passes_test(is_admin, login_url='no-permission'))
    def dispatch(self, request, *args, **kwargs):
        self.user_id = kwargs.get('user_id')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(id=self.user_id)
        role = form.cleaned_data.get('role')
        user.groups.clear()  # Remove old roles
        user.groups.add(role)
        messages.success(
            self.request, f"User {user.username} has been assigned to the {role.name} role")
        return super().form_valid(form)


class CreateGroupView(FormView):
    template_name = 'admin/create_group.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('create-group')

    @method_decorator(user_passes_test(is_admin, login_url='no-permission'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        group = form.save()
        messages.success(
            self.request, f"Group {group.name} has been created successfully")
        return super().form_valid(form)


class GroupListView(ListView):
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    @method_decorator(user_passes_test(is_admin, login_url='no-permission'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Group.objects.prefetch_related('permissions').all()


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)
