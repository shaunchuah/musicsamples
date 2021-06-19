from .models import Sample, Note
from .forms import SampleForm, CheckoutForm, DeleteForm, RestoreForm
from .forms import NoteForm, NoteDeleteForm, ReactivateForm, FullyUsedForm
from django.http import JsonResponse
import datetime
# import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions
from .serializers import SampleSerializer, SampleIsFullyUsedSerializer, MultipleSampleSerializer
from taggit.models import Tag
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models.functions import Trunc
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
User = get_user_model()


@login_required(login_url="/login/")
def index(request):
    # Home Page
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).order_by('-sample_datetime')
    sample_count = sample_list.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(sample_list, 50)
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)
    context = {'sample_list': samples, 'sample_count': sample_count}
    return render(request, "index.html", context)


@login_required(login_url="/login/")
# @cache_page(60 * 60)  # Cache page for 60 minutes
def analytics(request):
    # Analytics Page

    # Get last 12 months date
    current_date = datetime.datetime.now(datetime.timezone.utc)
    months_ago = 12
    twelve_months_previous_date = current_date - datetime.timedelta(days=(months_ago * 365 / 12))

    total_samples = Sample.objects.all().filter(is_deleted=False).count()
    total_active_samples = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).count()
    samples_by_month = Sample.objects.all().filter(is_deleted=False, sample_datetime__gte=twelve_months_previous_date).annotate(sample_month=Trunc('sample_datetime', 'month')).values('sample_month').annotate(sample_count=Count('id')).order_by('sample_month')
    samples_by_type = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).values('sample_type').annotate(sample_type_count=Count('id'))
    samples_by_location = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=False).values('sample_location').annotate(sample_location_count=Count('id'))
    context = {
        'total_samples': total_samples,
        'samples_by_month': samples_by_month,
        'samples_by_type': samples_by_type,
        'samples_by_location': samples_by_location,
        'total_active_samples': total_active_samples,
    }
    return render(request, "analytics.html", context)


@login_required(login_url="/login/")
@cache_page(60 * 60)  # Cache page for 60 minutes
def gid_overview(request):
    # Analytics --> Sample Overview Table Page
    sample_categories = Sample.objects.filter(is_deleted=False).filter(is_fully_used=False).values("sample_type").distinct()
    sample_category_list = []
    for item in sample_categories:
        sample_category_list.append(item['sample_type'])
    if 'q' in request.GET:
        query = request.GET.get('q')
        sample_list = Sample.objects.filter(is_deleted=False).filter(is_fully_used=False).filter(sample_type=query).order_by("patientid")
    else:
        query = None
        sample_list = Sample.objects.none()
    context = {'sample_list': sample_list, 'sample_category_list': sample_category_list, 'query': query}
    return render(request, "gid_overview.html", context)


@login_required(login_url="/login/")
def reference(request):
    # Reference static page for publishing lab protocols
    return render(request, "reference.html")


@login_required(login_url="/login/")
def account(request):
    # User account page showing last 20 recently accessed samples
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(last_modified_by=request.user.username).order_by('-last_modified')[:20]
    context = {'sample_list': sample_list}
    return render(request, "account.html", context)


@login_required(login_url="/login/")
def sample_archive(request):
    # Deleted samples page for samples which have been soft deleted
    sample_list = Sample.objects.all().filter(is_deleted=True).order_by('-last_modified')
    context = {'sample_list': sample_list}
    return render(request, "samples/sample-archive.html", context)


@login_required(login_url="/login/")
def used_samples(request):
    # Used samples page for samples marked as being fully used
    sample_list = Sample.objects.all().filter(is_deleted=False).filter(is_fully_used=True).order_by('-last_modified')
    sample_count = sample_list.count()
    context = {'sample_list': sample_list, 'sample_count': sample_count}
    return render(request, "samples/used_samples.html", context)


@login_required(login_url="/login/")
def used_samples_search(request):
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        sample_list = Sample.objects.filter(
            Q(musicsampleid__icontains=query_string)
            | Q(patientid__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_sublocation__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)).filter(is_fully_used=True).filter(is_deleted=False)
        sample_count = sample_list.count()
        return render(request, 'samples/used_samples.html', {'query_string': query_string, 'sample_list': sample_list, 'sample_count': sample_count})
    else:
        return render(request, 'samples/used_samples.html', {'query_string': 'Null', 'sample_count': 0})


@login_required(login_url="/login/")
def sample_add(request):
    # Add mew sample page
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.created_by = request.user.username
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, 'Sample registered successfully.')
            return redirect(reverse('sample_add'))
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = SampleForm()
    return render(request, "samples/sample-add.html", {'form': form, 'page_title': 'Add New Sample'})


def historical_changes(query):
    # Historical changes function to integrate simple history into the sample detail page
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
    # Sample Detail Page - retrieves sample history and also linked notes both public and private
    sample = get_object_or_404(Sample, pk=pk)
    sample_history = sample.history.filter(id=pk)
    changes = historical_changes(sample_history)
    first_change = sample_history.first()
    related_notes = sample.note_set.filter(is_public=True)
    private_notes = sample.note_set.filter(is_public=False).filter(author=request.user)
    if sample.patientid[0:3] == "GID":
        gid_id = int(sample.patientid.split("-")[1])
    else:
        gid_id = None
    processing_time = None
    if sample.processing_datetime is not None:
        time_difference = sample.processing_datetime - sample.sample_datetime
        processing_time = int(time_difference.total_seconds() / 60)
    return render(request, "samples/sample-detail.html", {'sample': sample, 'changes': changes, 'first': first_change, 'processing_time': processing_time, 'gid_id': gid_id, 'related_notes': related_notes, 'private_notes': private_notes})


@login_required(login_url="/login/")
def sample_edit(request, pk):
    # Sample Edit Page
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
    return render(request, 'samples/sample-add.html', {'form': form, 'page_title': 'Update Sample'})


@login_required(login_url="/login/")
def sample_search(request):
    # Sample search in home page
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        sample_list = Sample.objects.filter(
            Q(musicsampleid__icontains=query_string)
            | Q(patientid__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_sublocation__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)).filter(is_fully_used=False).filter(is_deleted=False)
        sample_count = sample_list.count()
        return render(request, 'index.html', {'query_string': query_string, 'sample_list': sample_list, 'sample_count': sample_count})
    else:
        return render(request, 'index.html', {'query_string': 'Null', 'sample_count': 0})


@login_required(login_url="/login/")
def sample_checkout(request, pk):
    # Sample Checkout - Quick update of sample location from home page
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
    return render(request, 'samples/sample-checkout.html', {'form': form})


@login_required(login_url="/login/")
def sample_delete(request, pk):
    # Soft deletion method for samples
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
    return render(request, 'samples/sample-delete.html', {'form': form})


@login_required(login_url="/login/")
def sample_restore(request, pk):
    # Restore soft-deleted sample
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
    return render(request, 'samples/sample-restore.html', {'form': form})


@login_required(login_url="/login/")
def sample_fully_used(request, pk):
    # Mark sample as fully used
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
    return render(request, 'samples/sample-fullyused.html', {'form': form})


@login_required(login_url="/login/")
def reactivate_sample(request, pk):
    # Reactive sample which has been marked as fully used
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
    return render(request, 'samples/sample-reactivate.html', {'form': form})


# @login_required(login_url="/login/")
# def export_csv(request):
#     # Export entire database to CSV for backup, currently not in use
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="music_samples_%s.csv"' % datetime.datetime.now().strftime("%Y-%m-%d")
#     writer = csv.writer(response)
#     writer.writerow(['MUSIC Sample ID', 'Patient ID', 'Sample Location', 'Sample Type', 'Sample Datetime', 'Sample Comments', 'Created By', 'Date First Created', 'Last Modified By', 'Last Modified'])
#     samples = Sample.objects.all().filter(is_deleted=False).values_list('musicsampleid', 'patientid', 'sample_location', 'sample_type', 'sample_datetime', 'sample_comments', 'created_by', 'data_first_created', 'last_modified_by', 'last_modified')
#     for sample in samples:
#         writer.writerow(sample)
#     return response

# Excel Exports


@login_required(login_url="/login/")
def export_excel(request):
    # Exports custom views depending on the search string otherwise exports entire database
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        samples_queryset = Sample.objects.filter(
            Q(musicsampleid__icontains=query_string)
            | Q(patientid__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string))
    else:
        samples_queryset = Sample.objects.all().filter(is_deleted=False)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="samples_export_%s.xlsx"' % datetime.datetime.now().strftime("%Y-%m-%d")

    workbook = Workbook()
    # Get active worksheet
    worksheet = workbook.active
    worksheet.title = 'All Samples'

    # Define the excel column names
    columns = [
        'Sample ID',
        'Patient ID',
        'Sample Location',
        'Sample Sublocation',
        'Sample Type',
        'Sampling Datetime',
        'Processing Datetime',
        'Sampling to Processing Time (mins)',
        'Sample Volume',
        'Sample Volume Units',
        'Freeze Thaw Count',
        'Haemolysis Reference Category (100 and above unusable)',
        'Biopsy Location',
        'Biopsy Inflamed Status',
        'Sample Comments',
        'Sample Fully Used?',
        'Created By',
        'Date Created',
        'Last Modified By',
        'Last Modified'
    ]
    row_num = 1

    # Write the column names in
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        # Setting a uniform column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = 20

    for sample in samples_queryset:
        processing_time = None
        if sample.processing_datetime is not None:
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
            sample.biopsy_location,
            sample.biopsy_inflamed_status,
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

############################################################################
# NOTES SECTION ############################################################
############################################################################
# Notes is set up much like a blogging system with the usual blogging tags
# The main unique point is the ability to tag the ID of relevant samples
# to allow quick access both from the notes side as well as from the
# sample-detail side
#
# SHARING
# The default option is for notes to be shared to every user of the system
# to promote a collaborative lab environment. There is an option to mark
# notes as 'private'.
# The logic controlling access to private notes is found here.
# Do note that every note is still viewable by the administrator
#
# FILE UPLOADS/ATTACHMENTS - **IMPORTANT** - THESE FILES ARE
# PUBLICLY AVAILABLE OVER THE INTERNET IF YOU KNOW THE URL
# File uploads are supported via CKEditor but will require
# configuring some sort of S3 backend to work properly
# See Django's documentation on handling media uploads - there are a
# few customisation options you can consider


@login_required(login_url="/login/")
def notes(request):
    # Shared Lab Notes - Find all shared notes between all the users
    notes = Note.objects.all().filter(is_public=True).filter(is_deleted=False)
    page = request.GET.get('page', 1)
    paginator = Paginator(notes, 10)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    all_tags = Note.tags.all()
    users = User.objects.all()
    context = {'notes': notes, 'page_title': 'Shared Notes', 'all_tags': all_tags, 'users': users}
    return render(request, "notes/notes-main.html", context)


@login_required(login_url="/login/")
def note_personal(request):
    # My Notebook - Show all notes belonging to the logged in user
    notes = Note.objects.all().filter(is_deleted=False).filter(author=request.user)
    page = request.GET.get('page', 1)
    paginator = Paginator(notes, 10)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    all_tags = Note.tags.all()
    users = User.objects.all()
    context = {'notes': notes, 'page_title': 'My Notebook', 'all_tags': all_tags, 'users': users, 'next_url': reverse('note_personal')}
    return render(request, "notes/notes-main.html", context)


@login_required(login_url="/login/")
def note_tags(request, slug):
    # Find all shared notes by tags and private notes depending on the
    # logged in user
    tag = get_object_or_404(Tag, slug=slug)

    # Get all public notes with the requested tag
    public_notes = Note.objects.filter(is_public=True).filter(is_deleted=False).filter(tags=tag)

    # Get all the private notes with the requested tag if the author and
    # logged in user is the same
    private_notes = Note.objects.filter(is_public=False).filter(is_deleted=False).filter(author__id=request.user.id).filter(tags=tag)

    notes = public_notes | private_notes
    page = request.GET.get('page', 1)
    paginator = Paginator(notes, 10)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    all_tags = Note.tags.all()
    users = User.objects.all()
    context = {'notes': notes, 'page_title': 'Tag Results: #' + slug, 'all_tags': all_tags, 'users': users}
    return render(request, "notes/notes-main.html", context)


@login_required(login_url="/login/")
def note_authors(request, pk):
    # See all the shared notes by specific authors
    user = get_object_or_404(User, pk=pk)
    notes = Note.objects.filter(is_public=True).filter(is_deleted=False).filter(author=pk)
    page = request.GET.get('page', 1)
    paginator = Paginator(notes, 10)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    all_tags = Note.tags.all()
    users = User.objects.all()
    context = {'notes': notes, 'page_title': 'Notes by ' + user.first_name + ' ' + user.last_name, 'all_tags': all_tags, 'users': users}
    return render(request, "notes/notes-main.html", context)


@login_required(login_url="/login/")
def note_detail(request, pk):
    # See single note
    note = get_object_or_404(Note, pk=pk)
    if note.is_public:
        secured_note = note
    else:
        if request.user.id == note.author.id:
            secured_note = note
        else:
            messages.error(request, 'This note is private. Access denied')
            return redirect('/notes/personal')
    note_history = note.history.filter(id=pk)
    changes = historical_changes(note_history)
    context = {'note': secured_note, 'changes': changes}
    return render(request, "notes/notes-detail.html", context)


@login_required(login_url="/login/")
def note_add(request):
    # Adding a new note
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            form.save_m2m()
            messages.success(request, 'Note saved successfully.')
            return redirect('/notes/personal/')
        else:
            messages.error(request, 'There are some errors.')
    else:
        form = NoteForm()
    return render(request, "notes/notes-add.html", {'form': form})


@login_required(login_url="/login/")
def note_edit(request, pk):
    # Editing an existing note
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)

        # Check user authorisation
        if form.is_valid() and request.user.id == note.author.id:
            form.save()
            messages.success(request, 'Note updated successfully.')
            next_url = request.GET.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/notes/personal/')
        else:
            messages.error(request, 'Unable to edit note.')
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/notes-edit.html", {'form': form, 'note': note})


@login_required(login_url="/login/")
def note_delete(request, pk):
    # Soft deleting a note
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteDeleteForm(request.POST, instance=note)

        # Check user authorisation
        if form.is_valid() and request.user.id == note.author.id:
            form.save()
            messages.success(request, 'Note deleted successfully.')
            next_url = request.GET.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/notes/personal/')
        else:
            messages.error(request, 'Unable to delete note.')
    else:
        form = NoteDeleteForm(instance=note)
    return render(request, "notes/notes-delete.html", {'form': form, 'note': note})


@login_required(login_url="/login/")
def note_search(request):
    # Search Notes
    all_tags = Note.tags.all()
    users = User.objects.all()
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        notes = Note.objects.filter(Q(title__icontains=query_string) | Q(sample_tags__musicsampleid__icontains=query_string) | Q(content__icontains=query_string)).filter(is_deleted=False)
        context = {'notes': notes, 'page_title': 'Search Results for: ' + query_string, 'all_tags': all_tags, 'users': users}
        return render(request, 'notes/notes-main.html', context)
    else:
        if "HTTP_REFERER" in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect(reverse('notes'))


#############################################################################
# AUTOCOMPLETE/AJAX SECTION #################################################
#############################################################################


@login_required(login_url="/login/")
def autocomplete_locations(request):
    # Helps speed up sample adding by autocompleting already existing locations
    if 'term' in request.GET:
        qs = Sample.objects.filter(is_deleted=False).filter(sample_location__icontains=request.GET.get('term')).values('sample_location').distinct()
    else:
        qs = Sample.objects.filter(is_deleted=False).values('sample_location').distinct()
    locations = list()
    for sample in qs:
        locations.append(sample['sample_location'])
    return JsonResponse(locations, safe=False)


@login_required(login_url="/login/")
def autocomplete_patient_id(request):
    # Helps speed up sample adding by locating existing patient IDs
    if 'term' in request.GET:
        qs = Sample.objects.filter(is_deleted=False).filter(patientid__icontains=request.GET.get('term')).values('patientid').distinct()
    else:
        qs = Sample.objects.filter(is_deleted=False).values('patientid').distinct()
    patients = list()
    for sample in qs:
        patients.append(sample['patientid'])
    return JsonResponse(patients, safe=False)


@login_required(login_url="/login/")
def autocomplete_tags(request):
    # Helps keep tags consistent by promoting autocompletion against
    # existing tags in the database
    if 'term' in request.GET:
        tags = Tag.objects.filter(name__icontains=request.GET.get('term')).values('name').distinct()
    else:
        tags = Tag.objects.values('name').distinct()
    tag_list = list()
    for tag in tags:
        tag_list.append(tag['name'])
    return JsonResponse(tag_list, safe=False)


##############################################################################
# REST FRAMEWORK/BARCODE APIS ################################################
##############################################################################
# The bulk QR scanning capability is dependent on using JavaScript - jQuery in
# this instance - in the frontend and Django Rest Framework in the backend.
#
# Barcode readers typically terminate the scan with either the 'enter' or
# 'tab' key.
#
# The barcode scanning page listens for both enter and tab keys
#
# When these keys are heard an ajax query is sent to the API /api/<Sample ID>/
# This attempts to match the scanned label against an existing sample and
# if so updates the sample's location.
# If it does not succeed it returns an error response - Object not found.
# A warning message is then displayed.
#
# This allows you to install physical hardpoints - eg arrival and departure
# from sites and if you scan every sample that goes through you can begin to
# track all their locations.


class SampleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows samples to be viewed and edited
    Lookup field set to the barcode ID instead of the default Django
    autoincrementing id system
    """
    queryset = Sample.objects.filter(is_deleted=False)
    serializer_class = SampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'musicsampleid'
    filterset_fields = ['sample_type']


class SampleIsFullyUsedViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.filter(is_deleted=False)
    serializer_class = SampleIsFullyUsedSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'musicsampleid'


class MultipleSampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.filter(is_deleted=False)
    serializer_class = MultipleSampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'musicsampleid'


@login_required(login_url="/login/")
def barcode(request):
    # Returns the page - frontend logic is in the barcode.html template file
    return render(request, "barcode.html")


@login_required(login_url="/login/")
def barcode_samples_used(request):
    return render(request, "barcode-markused.html")


@login_required(login_url="/login/")
def barcode_add_multiple(request):
    return render(request, "barcode-addmultiple.html")
