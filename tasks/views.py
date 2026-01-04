from django.shortcuts import render

# Create your views here.
# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Q
from .models import Task
from .forms import TaskForm

def task_list(request):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get tasks for different categories
    tasks_today = Task.objects.filter(date=today).order_by('is_done', 'created_at')
    tasks_tomorrow = Task.objects.filter(date=tomorrow).order_by('is_done', 'created_at')
    tasks_upcoming = Task.objects.filter(date__gt=tomorrow).order_by('date', 'is_done', 'created_at')
    
    context = {
        'tasks_today': tasks_today,
        'tasks_tomorrow': tasks_tomorrow,
        'tasks_upcoming': tasks_upcoming,
        'today': today,
        'tomorrow': tomorrow,
    }
    return render(request, 'tasks/task_list.html', context)

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Add Task'})

def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task'})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_form.html', {'task': task, 'title': 'Delete Task'})

def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_done = not task.is_done
    task.save()
    return redirect('task_list')

def monthly_stats(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Get tasks for current month
    tasks_this_month = Task.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    )
    
    total_tasks = tasks_this_month.count()
    completed_tasks = tasks_this_month.filter(is_done=True).count()
    
    percentage_completed = 0
    if total_tasks > 0:
        percentage_completed = round((completed_tasks / total_tasks) * 100, 1)
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'percentage_completed': percentage_completed,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'tasks/monthly_stats.html', context)