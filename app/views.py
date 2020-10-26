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
from .forms import SampleForm, CheckoutForm, SampleFormSet, DeleteForm, RestoreForm
from django.contrib import messages
from django.db.models import Q
from django.forms import formset_factory
import csv
import datetime

@login_required(login_url="/login/")
def index(request):
    sample_list = Sample.objects.all().filter(is_deleted=False).order_by('-last_modified')
    context = {'sample_list': sample_list}
    return render(request, "index.html", context)

@login_required(login_url="/login/")
def analytics(request):
    #sample_list = Sample.objects.all().order_by('-last_modified')
    #context = {'sample_list': sample_list}
    return render(request, "analytics.html")

@login_required(login_url="/login/")
def archive(request):
    sample_list = Sample.objects.all().filter(is_deleted=True).order_by('-last_modified')
    context = {'sample_list': sample_list}
    return render(request, "archive.html", context)

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
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
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

@login_required(login_url="/login/")
def checkout(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = CheckoutForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample updated successfully.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
    else:
        form = CheckoutForm(instance=sample)
    return render(request, 'sample-edit.html', {'form': form})

@login_required(login_url="/login/")
def delete(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = DeleteForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample deleted.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
    else:
        form = DeleteForm(instance=sample)
    return render(request, 'sample-delete.html', {'form': form})

@login_required(login_url="/login/")
def restore(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = RestoreForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample restored.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
    else:
        form = RestoreForm(instance=sample)
    return render(request, 'sample-restore.html', {'form': form})

@login_required(login_url="/login/")
def bulkadd(request):
    if request.method == "POST":
        formset = SampleFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                sample = form.save(commit=False)
                sample.created_by = request.user.username
                sample.last_modified_by = request.user.username
                sample.save()
            messages.success(request, 'All samples registered successfully.')
            return redirect('/')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        formset = SampleFormSet()
    return render(request, "bulk-add.html", {'formset': formset})

@login_required(login_url="/login/")
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="music_samples_%s.csv"' % datetime.datetime.now().strftime("%Y-%m-%d")

    writer = csv.writer(response)
    writer.writerow(['MUSIC Sample ID','Patient ID', 'Sample Location', 'Sample Type', 'Sample Datetime', 'Sample Comments', 'Created By', 'Date First Created', 'Last Modified By', 'Last Modified'])

    samples = Sample.objects.all().filter(is_deleted=False).values_list('musicsampleid','patientid', 'sample_location', 'sample_type', 'sample_datetime', 'sample_comments', 'created_by', 'data_first_created', 'last_modified_by',  'last_modified')
    for sample in samples:
        writer.writerow(sample)
    return response

