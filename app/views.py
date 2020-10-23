# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from .models import Sample
from .forms import NewSampleForm, SampleForm
from django.contrib import messages
from django.db.models import Q

@login_required(login_url="/login/")
def index(request):
    sample_list = Sample.objects.all()
    context = {'sample_list': sample_list}
    return render(request, "index.html", context)

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def add(request):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.created_by = request.user.username
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample registered successfully.')
            return redirect('/add/')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = SampleForm()
    return render(request, "add.html", {'form': form})

@login_required(login_url="/login/")
def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    return render(request, "sample-detail.html", {'sample': sample})
    
@login_required(login_url="/login/")
def sample_edit(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample updated successfully.')
            return redirect('/')
    else:
        form = SampleForm(instance=sample)
    return render(request, 'sample-edit.html', {'form': form})

@login_required(login_url="/login/")
def search(request):
    query_string=''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        sample_list = Sample.objects.filter(
            Q(musicsampleid__icontains=query_string)|
            Q(patientid__icontains=query_string)|
            Q(sample_location__icontains=query_string)|
            Q(sample_type__icontains=query_string)|
            Q(sample_comments__icontains=query_string))
        return render(request, 'index.html', { 'query_string': query_string, 'sample_list': sample_list})
    else:
        return render(request, 'index.html', { 'query_string': 'Null' })