# Refactor To-Do List

Blocker templates/boxes/includes/experimental_id_table.html:52 / templates/boxes/includes/experimental_id_table.html:55 – the “Edit” and “Delete” actions still point at the box edit/delete routes. That will either 404 or try to mutate a completely different model when someone clicks them.

Blocker templates/boxes/experimental_id_list.html:47 – “Add New Experiment ID” links to boxes:create, which is the box form. There’s no path here to create an experimental ID any more, so the new page can’t add records.

Blocker templates/boxes/experimental_id_list.html:16-33 – the search form submits to boxes:search, which renders the box list and ignores experimental IDs. On the new page the search bar effectively breaks navigation by dumping you back to boxes.

Blocker templates/boxes/box_form.html:146-169 together with app/forms.py:252-269 – the modal still posts to create_experimental_id, but the form no longer renders a species input even though the model form now requires it. Every create attempt from the box modal will fail validation with a missing species error.

High app/filters.py:199-211 – the new ExperimentalIDFilter wires species up to SampleTypeChoices. That shows the wrong options and can’t match saved species values.

High templates/boxes/experimental_id_list.html:48-53 – the export button calls the box CSV endpoint, so exporting from the experimental-ID page returns box data instead of the table you’re looking at.

Medium templates/boxes/includes/experimental_id_table.html:60 – the empty-state row spans 11 columns, but the table has 12 headers. The layout collapses when the list is empty.

Testing gap app/tests/test_box_views.py:525-700 – we dropped the AJAX create/update/delete coverage for experimental IDs, but the modal and create_experimental_id view are still active. That leaves the newly required species field and the JSON contract untested.
