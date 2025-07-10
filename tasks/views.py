from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, Application
from .forms import TaskForm
from django.http import HttpResponseForbidden
from collections import defaultdict

# 🟢 Register View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})


# 📋 Task List View
@login_required
def task_list(request):
    tasks = Task.objects.all().order_by('-id')

    # Collect applications to pass to template
    task_applications = defaultdict(list)
    applied_task_ids = []

    applications = Application.objects.select_related('task', 'applicant')

    for app in applications:
        task_applications[app.task.id].append(app)
        if app.applicant == request.user:
            applied_task_ids.append(app.task.id)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'applications': task_applications,
        'applied_task_ids': applied_task_ids
    })


# ➕ Add Task
@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


# ✏️ Edit Task
@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


# ❌ Delete Task
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


# ✋ Apply to Task
@login_required
def apply_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.user == task.user:
        messages.warning(request, "You cannot apply to your own task.")
        return redirect('task_list')

    if request.method == 'POST':
        # Prevent duplicate applications
        already_applied = Application.objects.filter(task=task, applicant=request.user).exists()
        if already_applied:
            messages.info(request, "You have already applied to this task.")
            return redirect('task_list')

        message = request.POST.get('message')
        Application.objects.create(task=task, applicant=request.user, message=message)
        messages.success(request, "Applied to the task successfully.")

    return redirect('task_list')


# ✅ Confirm/Assign Task as "In Progress"
@login_required
def mark_in_progress(request, task_id, applicant_id):
    task = get_object_or_404(Task, id=task_id)

    if request.user != task.user:
        return HttpResponseForbidden("Only the task owner can update status.")

    if request.method == 'POST':
        task.status = 'in_progress'
        task.save()
        messages.success(request, "Task status updated to In Progress.")
        return redirect('task_list')
