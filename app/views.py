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
from .forms import SampleForm, CheckoutForm, SampleFormSet, DeleteForm, RestoreForm, ReactivateForm, FullyUsedForm
from django.contrib import messages
from django.db.models import Q
from django.forms import formset_factory
import csv
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models.functions import Trunc

@login_required(login_url="/login/")
def index(request):
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).order_by('-last_modified')
    page = request.GET.get('page', 1)
    paginator = Paginator(sample_list, 50)
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)
    context = {'sample_list': samples}
    return render(request, "index.html", context)

@login_required(login_url="/login/")
def analytics(request):
    total_samples = Sample.objects.all().filter(is_deleted=False).count()
    samples_by_month = Sample.objects.all().filter(is_deleted=False).annotate(sample_month=Trunc('sample_datetime', 'month')).values('sample_month').annotate(sample_count=Count('id')).order_by('sample_month')
    samples_by_type = Sample.objects.all().filter(is_deleted=False).values('sample_type').annotate(sample_type_count=Count('id'))
    samples_by_location = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).values('sample_location').annotate(sample_location_count=Count('id'))
    context = {
        'total_samples': total_samples,
        'samples_by_month': samples_by_month,
        'samples_by_type': samples_by_type,
        'samples_by_location': samples_by_location,
    }
    return render(request, "analytics.html", context)

@login_required(login_url="/login/")
def reference(request):
    return render(request, "reference.html")

@login_required(login_url="/login/")
def account(request):
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(last_modified_by=request.user.username).order_by('-last_modified')[:20]
    page = request.GET.get('page', 1)
    paginator = Paginator(sample_list, 50)
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)
    context = {'sample_list': samples}
    return render(request, "account.html", context)

@login_required(login_url="/login/")
def archive(request):
    sample_list = Sample.objects.all().filter(is_deleted=True).order_by('-last_modified')
    context = {'sample_list': sample_list}
    return render(request, "archive.html", context)

@login_required(login_url="/login/")
def used_samples(request):
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=True).order_by('-last_modified')
    context = {'sample_list': sample_list}
    return render(request, "used_samples.html", context)

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


def historical_changes(query):
    changes = []
    if query is not None:
        last = query.first()
        for all_changes in range(query.count()):
            new_record, old_record = last, last.prev_record
            if old_record is not None:
                delta = new_record.diff_against(old_record)
                changes.append(delta)
                last = old_record
        return changes

@login_required(login_url="/login/")
def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    sample_history = sample.history.filter(id=pk)
    changes = historical_changes(sample_history)
    first_change = sample_history.first()
    if sample.patientid[0:3] == "GID":
        gid_id = sample.patientid.split("-")[1]
    else:
        gid_id = None
    processing_time = None
    if sample.processing_datetime != None:
        time_difference = sample.processing_datetime - sample.sample_datetime
        processing_time = int(time_difference.total_seconds() / 60)
    return render(request, "sample-detail.html", {'sample': sample, 'changes': changes, 'first': first_change, 'processing_time': processing_time, 'gid_id': gid_id})
    
@login_required(login_url="/login/")
def sample_edit(request, pk):
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
            Q(sample_sublocation__icontains=query_string)|
            Q(sample_type__icontains=query_string)|
            Q(sample_comments__icontains=query_string)).filter(is_fully_used=False).filter(is_deleted=False)
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
    return render(request, 'sample-checkout.html', {'form': form})

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
def fully_used(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = FullyUsedForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample marked as fully used.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
    else:
        form = FullyUsedForm(instance=sample)
    return render(request, 'sample-fullyused.html', {'form': form})

@login_required(login_url="/login/")
def reactivate_sample(request,pk):
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = ReactivateForm(request.POST, instance=sample)
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
        form = ReactivateForm(instance=sample)
    return render(request, 'sample-reactivate.html', {'form': form})

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

#Export entire database to CSV for backup, currently not in use
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

##Excel Exports
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

@login_required(login_url="/login/")
def export_excel_all(request):
    samples_queryset = Sample.objects.all().filter(is_deleted=False)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="all_samples_%s.xlsx"' % datetime.datetime.now().strftime("%Y-%m-%d")

    workbook = Workbook()
    #Get active worksheet
    worksheet = workbook.active
    worksheet.title = 'All Samples'

    #Define the excel column names
    columns = ['Sample ID', 'Patient ID', 'Sample Location', 'Sample Sublocation', 'Sample Type', 'Sampling Datetime', 'Processing Datetime', 'Sampling to Processing Time (mins)','Sample Volume', 'Sample Volume Units', 'Freeze Thaw Count', 'Haemolysis Reference Category (100 and above unusable)', 'Sample Comments', 'Sample Fully Used?', 'Created By', 'Date Created', 'Last Modified By', 'Last Modified']
    row_num = 1

    #Write the column names in
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        #setting column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = 20

    for sample in samples_queryset:
        processing_time = None
        if sample.processing_datetime != None:
            time_difference = sample.processing_datetime - sample.sample_datetime
            processing_time = int(time_difference.total_seconds() / 60)
        row_num += 1
        row = [
            sample.musicsampleid,
            sample.patientid,
            sample.sample_location,
            sample.sample_sublocation,
            sample.sample_type,
            sample.sample_datetime,
            sample.processing_datetime,
            processing_time,
            sample.sample_volume,
            sample.sample_volume_units,
            sample.freeze_thaw_count,
            sample.haemolysis_reference,
            sample.sample_comments,
            sample.is_fully_used,
            sample.created_by,
            sample.data_first_created,
            sample.last_modified_by,
            sample.last_modified,
        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    worksheet.freeze_panes = worksheet['A2']
    workbook.save(response)
    return response

@login_required(login_url="/login/")
def export_excel(request):
    query_string=''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        samples_queryset = Sample.objects.filter(
            Q(musicsampleid__icontains=query_string)|
            Q(patientid__icontains=query_string)|
            Q(sample_location__icontains=query_string)|
            Q(sample_type__icontains=query_string)|
            Q(sample_comments__icontains=query_string))
    else:
        samples_queryset = Sample.objects.all().filter(is_deleted=False)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="samples_search_export_%s.xlsx"' % datetime.datetime.now().strftime("%Y-%m-%d")

    workbook = Workbook()
    #Get active worksheet
    worksheet = workbook.active
    worksheet.title = 'All Samples'

    #Define the excel column names
    columns = ['Sample ID', 'Patient ID', 'Sample Location', 'Sample Sublocation', 'Sample Type', 'Sampling Datetime', 'Processing Datetime', 'Sampling to Processing Time (mins)','Sample Volume', 'Sample Volume Units', 'Freeze Thaw Count', 'Haemolysis Reference Category (100 and above unusable)', 'Sample Comments', 'Sample Fully Used?', 'Created By', 'Date Created', 'Last Modified By', 'Last Modified']
    row_num = 1

    #Write the column names in
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        #setting column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = 20

    for sample in samples_queryset:
        processing_time = None
        if sample.processing_datetime != None:
            time_difference = sample.processing_datetime - sample.sample_datetime
            processing_time = int(time_difference.total_seconds() / 60)
        row_num += 1
        row = [
            sample.musicsampleid,
            sample.patientid,
            sample.sample_location,
            sample.sample_sublocation,
            sample.sample_type,
            sample.sample_datetime,
            sample.processing_datetime,
            processing_time,
            sample.sample_volume,
            sample.sample_volume_units,
            sample.freeze_thaw_count,
            sample.haemolysis_reference,
            sample.sample_comments,
            sample.is_fully_used,
            sample.created_by,
            sample.data_first_created,
            sample.last_modified_by,
            sample.last_modified,
        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    worksheet.freeze_panes = worksheet['A2']
    workbook.save(response)
    return response