from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *


from django.http import HttpResponse

# def test_session(request):
#     request.session['test_key'] = 'Session is working'
#     return HttpResponse(request.session.get('test_key', 'Session failed'))


def test_session(request):
    request.session['test_key'] = 'Redis session working'
    return HttpResponse(request.session.get('test_key', 'Session failed'))



def register(request):
    return HttpResponseForbidden("Public registration is disabled. Please contact the administrator.")

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
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        if form.is_valid():
            if 'license_image' not in request.FILES:
                form.cleaned_data['license_image'] = profile.license_image
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('pilot_profile')
        else:
            messages.error(request, "There was an error updating your profile.")
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
            return redirect('pilot_profile')
        else:
            messages.error(request, "Could not save training record.")
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
