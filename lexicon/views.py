from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from .forms import RegistrationForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register/complete')
    else:
        form = RegistrationForm(request.GET)
    return render(request, 'registration/registration_form.html', {'form': form})


def registration_complete(request):
    return render_to_response('registration/registration_complete.html')