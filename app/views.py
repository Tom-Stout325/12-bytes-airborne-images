
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PilotProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('edit_pilot_profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def pilot_profile(request):
    try:
        profile = PilotProfile.objects.get(user=request.user)
    except PilotProfile.DoesNotExist:
        return redirect('edit_pilot_profile')
    return render(request, 'app/pilot_profile.html', {'profile': profile})


@login_required
def edit_pilot_profile(request):
    profile, _ = PilotProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PilotProfileForm(request.POST, request.FILES, instance=profile)

        # Update user info
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        if form.is_valid():
            # If no new file is uploaded, don't overwrite the existing image
            if 'license_image' not in request.FILES:
                form.cleaned_data['license_image'] = profile.license_image
            form.save()
            messages.success(request, "Profile updated successfully.")
            messages.error(request, "There was an error updating your profile.")
            return redirect('pilot_profile')
    else:
        form = PilotProfileForm(instance=profile)

    return render(request, 'app/pilot_profile_edit.html', {
        'profile_form': form,
        'user': request.user
    })


@login_required
def delete_pilot_profile(request):
    profile = get_object_or_404(PilotProfile, user=request.user)
    if request.method == 'POST':
        user = profile.user
        profile.delete()
        user.delete()
        messages.success(request, "Your profile and account have been deleted.")
        return redirect('login')
    return render(request, 'app/pilot_profile_delete.html', {'profile': profile})


@login_required
def add_training_record(request):
    profile = get_object_or_404(PilotProfile, user=request.user)

    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, request.FILES)
        if form.is_valid():
            training = form.save(commit=False)
            training.pilot = profile
            training.save()
            messages.success(request, "Training record added.")
            messages.error(request, "Could not save training record.")
            return redirect('pilot_profile')
    else:
        form = TrainingRecordForm()

    return render(request, 'app/training_add.html', {'form': form})


@login_required
def edit_training_record(request, pk):
    profile = get_object_or_404(PilotProfile, user=request.user)
    training = get_object_or_404(TrainingRecord, pk=pk, pilot=profile)

    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, request.FILES, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, 'Training record updated successfully.')
            return redirect('pilot_profile')
    else:
        form = TrainingRecordForm(instance=training)

    return render(request, 'app/training_edit.html', {'form': form, 'training': training})


@login_required
def delete_training_record(request, pk):
    profile = get_object_or_404(PilotProfile, user=request.user)
    training = get_object_or_404(TrainingRecord, pk=pk, pilot=profile)

    if request.method == 'POST':
        training.delete()
        messages.success(request, 'Training record deleted.')
        return redirect('pilot_profile')

    return render(request, 'app/training_delete.html', {'training': training})
