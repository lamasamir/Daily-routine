# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Q
from .models import Task
from .forms import TaskForm, CustomUserCreationForm, CustomAuthenticationForm

# Authentication Views
def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Daily Routine Tracker.')
            return redirect('task_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'tasks/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('task_list')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'tasks/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    tasks_count = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, is_done=True).count()
    
    context = {
        'user': user,
        'tasks_count': tasks_count,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'tasks/profile.html', context)

# Task Views
@login_required
def task_list(request):
    user = request.user
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get tasks for different categories for the logged-in user
    tasks_today = Task.objects.filter(user=user, date=today).order_by('is_done', 'created_at')
    tasks_tomorrow = Task.objects.filter(user=user, date=tomorrow).order_by('is_done', 'created_at')
    tasks_upcoming = Task.objects.filter(user=user, date__gt=tomorrow).order_by('date', 'is_done', 'created_at')
    
    context = {
        'tasks_today': tasks_today,
        'tasks_tomorrow': tasks_tomorrow,
        'tasks_upcoming': tasks_upcoming,
        'today': today,
        'tomorrow': tomorrow,
        'user': user,
    }
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task added successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Add Task'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    return render(request, 'tasks/task_form.html', {'task': task, 'title': 'Delete Task'})

@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_done = not task.is_done
    task.save()
    
    status = "completed" if task.is_done else "marked as incomplete"
    messages.success(request, f'Task "{task.title}" {status}!')
    return redirect('task_list')

@login_required
def monthly_stats(request):
    user = request.user
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Get tasks for current month for the logged-in user
    tasks_this_month = Task.objects.filter(
        user=user,
        created_at__year=today.year,
        created_at__month=today.month
    )
    
    total_tasks = tasks_this_month.count()
    completed_tasks = tasks_this_month.filter(is_done=True).count()
    
    percentage_completed = 0
    if total_tasks > 0:
        percentage_completed = round((completed_tasks / total_tasks) * 100, 1)
    
    # Get recent activities
    recent_tasks = Task.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'percentage_completed': percentage_completed,
        'current_month': today.strftime('%B %Y'),
        'recent_tasks': recent_tasks,
        'user': user,
    }
    
    return render(request, 'tasks/monthly_stats.html', context)