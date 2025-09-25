from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, Permission
from django.test import RequestFactory, TestCase
from django.urls import reverse, reverse_lazy

from app.choices import BasicScienceGroupChoices, SpeciesChoices
from app.factories import (
    BasicScienceBoxFactory,
    BasicScienceSampleTypeFactory,
    ExperimentalIDFactory,
    TissueTypeFactory,
)
from app.models import BasicScienceBox, ExperimentalID
from app.views.box_views import (
    BasicScienceBoxCreateView,
    BasicScienceBoxDeleteView,
    BasicScienceBoxDetailView,
    BasicScienceBoxListView,
    BasicScienceBoxUpdateView,
    ExperimentalIdCreateView,
    ExperimentalIdDeleteView,
    ExperimentalIdDetailView,
    ExperimentalIdListView,
    ExperimentalIdUpdateView,
)
from users.factories import UserFactory


class PermissionHelperMixin:
    def grant_permission(self, codename: str) -> None:
        permission = Permission.objects.get(codename=codename, content_type__app_label="app")
        self.user.user_permissions.add(permission)  # type: ignore


class BasicScienceBoxDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.box = BasicScienceBoxFactory()
        self.url = reverse("boxes:detail", kwargs={"pk": self.box.pk})

    def test_view_requires_login(self):
        """Test that the view requires authentication"""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = BasicScienceBoxDetailView.as_view()(request, pk=self.box.pk)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_requires_permission(self):
        """Test that the view requires the correct permission"""
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user

        # Create view instance
        view = BasicScienceBoxDetailView()
        view.request = request

        # User doesn't have the required permission - should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            view.dispatch(request, pk=self.box.pk)

    def test_view_with_permission(self):
        """Test that the view works correctly with proper permission"""
        # Add the required permission to the user
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        request = self.factory.get(self.url)
        request.user = self.user

        response = BasicScienceBoxDetailView.as_view()(request, pk=self.box.pk)

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client for template testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check template used
        self.assertTemplateUsed(response, "boxes/box_detail.html")

    def test_view_context_contains_box(self):
        """Test that the view context contains the box object"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client for context testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check context
        self.assertIn("box", response.context)
        self.assertEqual(response.context["box"], self.box)

    def test_view_context_contains_changes(self):
        """Test that the view context contains historical changes"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client for context testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check that changes and first are in context
        self.assertIn("changes", response.context)
        self.assertIn("first", response.context)

        # Changes should be a list (even if empty for new objects)
        self.assertIsInstance(response.context["changes"], list)

    def test_view_with_nonexistent_box(self):
        """Test that the view handles non-existent boxes properly"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:detail", kwargs={"pk": 99999}))

        # Should return 404
        self.assertEqual(response.status_code, 404)

    def test_context_object_name(self):
        """Test that the context object name is correctly set"""
        view = BasicScienceBoxDetailView()
        self.assertEqual(view.context_object_name, "box")

    def test_model_attribute(self):
        """Test that the view uses the correct model"""
        view = BasicScienceBoxDetailView()
        self.assertEqual(view.model, BasicScienceBox)

    def test_permission_required_attribute(self):
        """Test that the view has the correct permission requirement"""
        view = BasicScienceBoxDetailView()
        self.assertEqual(view.permission_required, "app.view_basicsciencebox")

    @patch.object(BasicScienceBoxDetailView, "get_object")
    def test_get_context_data_method(self, mock_get_object):
        """Test the get_context_data method specifically"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Mock get_object to return our box
        mock_get_object.return_value = self.box

        # Create a view instance
        view = BasicScienceBoxDetailView()
        view.request = self.factory.get(self.url)
        view.request.user = self.user
        view.object = self.box  # type:ignore

        # Call get_context_data
        context = view.get_context_data()

        # Check that all expected keys are present
        self.assertIn("box", context)
        self.assertIn("changes", context)
        self.assertIn("first", context)
        self.assertEqual(context["box"], self.box)
        self.assertIsInstance(context["changes"], list)

    def test_distinct_sample_and_tissue_labels_helpers(self):
        """Ensure helper methods aggregate experiment tags correctly"""
        sample_type = BasicScienceSampleTypeFactory()
        tissue_type = TissueTypeFactory()
        experimental = ExperimentalIDFactory()
        experimental.sample_types.add(sample_type)
        experimental.tissue_types.add(tissue_type)
        box = BasicScienceBoxFactory(experimental_ids=[experimental])

        self.assertIn(sample_type.label or sample_type.name, box.get_sample_type_labels())
        self.assertIn(tissue_type.label or tissue_type.name, box.get_tissue_type_labels())


class BasicScienceBoxListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.url = reverse("boxes:list")
        # Create some test boxes
        self.box1 = BasicScienceBoxFactory(is_used=False)
        self.box2 = BasicScienceBoxFactory(is_used=False)
        self.box3 = BasicScienceBoxFactory(is_used=True)  # Should be excluded

    def test_view_requires_login(self):
        """Test that the view requires authentication"""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = BasicScienceBoxListView.as_view()(request)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_requires_permission(self):
        """Test that the view requires the correct permission"""
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user

        # Create view instance
        view = BasicScienceBoxListView()
        view.request = request

        # User doesn't have the required permission - should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_view_with_permission(self):
        """Test that the view works correctly with proper permission"""
        # Add the required permission to the user
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        request = self.factory.get(self.url)
        request.user = self.user

        response = BasicScienceBoxListView.as_view()(request)

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client for template testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check template used
        self.assertTemplateUsed(response, "boxes/box_list.html")

    def test_view_context_contains_boxes(self):
        """Test that the view context contains the boxes queryset"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        # Use Django's test client for context testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check context
        self.assertIn("boxes", response.context)
        # Should contain box1 and box2, but not box3 (is_used=True)
        boxes = list(response.context["boxes"])
        self.assertIn(self.box1, boxes)
        self.assertIn(self.box2, boxes)
        self.assertNotIn(self.box3, boxes)

    def test_queryset_excludes_used_boxes(self):
        """Test that get_queryset excludes boxes where is_used=True"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )

        request = self.factory.get(self.url)
        request.user = self.user

        view = BasicScienceBoxListView()
        view.request = request
        queryset = view.get_queryset()

        # Should not include box3
        self.assertNotIn(self.box3, queryset)
        self.assertIn(self.box1, queryset)
        self.assertIn(self.box2, queryset)

    def test_context_object_name(self):
        """Test that the context object name is correctly set"""
        view = BasicScienceBoxListView()
        self.assertEqual(view.context_object_name, "boxes")

    def test_model_attribute(self):
        """Test that the view uses the correct model"""
        view = BasicScienceBoxListView()
        self.assertEqual(view.model, BasicScienceBox)

    def test_permission_required_attribute(self):
        """Test that the view has the correct permission requirement"""
        view = BasicScienceBoxListView()
        self.assertEqual(view.permission_required, "app.view_basicsciencebox")


class BasicScienceBoxCreateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.url = reverse("boxes:create")
        self.valid_data = {
            "box_id": "TEST001",
            "box_type": "basic_science_samples",
            "location": "sii_freezer_1",
        }

    def test_view_requires_login(self):
        """Test that the view requires authentication"""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = BasicScienceBoxCreateView.as_view()(request)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_requires_permission(self):
        """Test that the view requires the correct permission"""
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user

        # Create view instance
        view = BasicScienceBoxCreateView()
        view.request = request

        # User doesn't have the required permission - should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_view_with_permission_get(self):
        """Test that the view works correctly with proper permission for GET"""
        # Add the required permission to the user
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        request = self.factory.get(self.url)
        request.user = self.user

        response = BasicScienceBoxCreateView.as_view()(request)

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        # Use Django's test client for template testing
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # Check template used
        self.assertTemplateUsed(response, "boxes/box_form.html")

    def test_form_valid_creates_box(self):
        """Test that valid form submission creates a new box"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        initial_count = BasicScienceBox.objects.count()

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_data)

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BasicScienceBox.objects.count(), initial_count + 1)

    def test_form_valid_sets_created_by(self):
        """Test that form_valid sets created_by to the current user"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        self.client.post(self.url, self.valid_data)

        # Check that the created box has created_by set
        box = BasicScienceBox.objects.get(box_id="TEST001")
        self.assertEqual(box.created_by, self.user)

    def test_form_valid_sets_last_modified_by(self):
        """Test that form_valid sets last_modified_by to the current user"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        self.client.post(self.url, self.valid_data)

        # Check that the created box has last_modified_by set
        box = BasicScienceBox.objects.get(box_id="TEST001")
        self.assertEqual(box.last_modified_by, self.user)

    def test_form_valid_success_message(self):
        """Test that form_valid shows success message"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_data, follow=True)

        # Check that success message is in the response
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Box registered successfully.")

    def test_form_valid_redirects_to_list(self):
        """Test that form_valid redirects to the list view"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_data)

        # Should redirect to boxes:list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("boxes:list"))

    def test_form_invalid(self):
        """Test that invalid form submission doesn't create box and shows errors"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="add_basicsciencebox", defaults={"name": "Can add basic science box"}
            )[0]
        )

        initial_count = BasicScienceBox.objects.count()

        # Submit invalid data (missing required fields)
        invalid_data = {"box_id": "TEST001"}  # Missing required fields

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, invalid_data)

        # Should return 200 with form errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BasicScienceBox.objects.count(), initial_count)
        self.assertTrue(response.context["form"].errors)

    def test_model_attribute(self):
        """Test that the view uses the correct model"""
        view = BasicScienceBoxCreateView()
        self.assertEqual(view.model, BasicScienceBox)

    def test_form_class_attribute(self):
        """Test that the view uses the correct form class"""
        from app.forms import BasicScienceBoxForm

        view = BasicScienceBoxCreateView()
        self.assertEqual(view.form_class, BasicScienceBoxForm)

    def test_success_url_attribute(self):
        """Test that the view has the correct success URL"""
        view = BasicScienceBoxCreateView()
        self.assertEqual(view.success_url, reverse_lazy("boxes:list"))

    def test_permission_required_attribute(self):
        """Test that the view has the correct permission requirement"""
        view = BasicScienceBoxCreateView()
        self.assertEqual(view.permission_required, "app.add_basicsciencebox")


class BasicScienceBoxUpdateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.box = BasicScienceBoxFactory()
        self.url = reverse("boxes:edit", kwargs={"pk": self.box.pk})
        self.valid_data = {
            "box_id": "UPDATED001",
            "box_type": "basic_science_samples",
            "location": "sii_freezer_1",
        }

    def test_view_requires_login(self):
        """Test that the view requires authentication"""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = BasicScienceBoxUpdateView.as_view()(request, pk=self.box.pk)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_requires_permission(self):
        """Test that the view requires the correct permission"""
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user

        # Create view instance
        view = BasicScienceBoxUpdateView()
        view.request = request

        # User doesn't have the required permission - should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            view.dispatch(request, pk=self.box.pk)

    def test_view_with_permission_get(self):
        """Test that the view works correctly with proper permission for GET"""
        # Add the required permission to the user
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="change_basicsciencebox", defaults={"name": "Can change basic science box"}
            )[0]
        )

        request = self.factory.get(self.url)
        request.user = self.user

        response = BasicScienceBoxUpdateView.as_view()(request, pk=self.box.pk)

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_form_valid_updates_box(self):
        """Test that valid form submission updates the box"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="change_basicsciencebox", defaults={"name": "Can change basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_data)

        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        self.box.refresh_from_db()
        self.assertEqual(self.box.box_id, "UPDATED001")

    def test_form_valid_sets_last_modified_by(self):
        """Test that form_valid sets last_modified_by to the current user"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="change_basicsciencebox", defaults={"name": "Can change basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        self.client.post(self.url, self.valid_data)

        # Check that the updated box has last_modified_by set
        self.box.refresh_from_db()
        self.assertEqual(self.box.last_modified_by, self.user)


class BasicScienceBoxDeleteViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.box = BasicScienceBoxFactory(is_used=False)
        self.url = reverse("boxes:delete", kwargs={"pk": self.box.pk})

    def test_view_requires_login(self):
        """Test that the view requires authentication"""
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = BasicScienceBoxDeleteView.as_view()(request, pk=self.box.pk)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_requires_permission(self):
        """Test that the view requires the correct permission"""
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user

        # Create view instance
        view = BasicScienceBoxDeleteView()
        view.request = request

        # User doesn't have the required permission - should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            view.dispatch(request, pk=self.box.pk)

    def test_post_marks_as_used(self):
        """Test that POST marks the box as used (soft delete)"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="delete_basicsciencebox", defaults={"name": "Can delete basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.box.refresh_from_db()
        self.assertTrue(self.box.is_used)

    def test_post_sets_last_modified_by(self):
        """Test that POST sets last_modified_by to the current user"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="delete_basicsciencebox", defaults={"name": "Can delete basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        self.client.post(self.url)

        # Check that the box has last_modified_by set
        self.box.refresh_from_db()
        self.assertEqual(self.box.last_modified_by, self.user)

    def test_post_success_message(self):
        """Test that POST shows success message"""
        # Add permission
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="delete_basicsciencebox", defaults={"name": "Can delete basic science box"}
            )[0]
        )

        # Use Django's test client for form submission
        self.client.force_login(self.user)
        response = self.client.post(self.url, follow=True)

        # Check that success message is in the response
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Box deleted successfully.")


class FunctionBasedViewsTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.box = BasicScienceBoxFactory()
        self.used_box = BasicScienceBoxFactory(is_used=True)
        self.group_experimental_id = ExperimentalIDFactory(basic_science_group=BasicScienceGroupChoices.BAIN)
        self.group_box = BasicScienceBoxFactory(experimental_ids=[self.group_experimental_id])

    def _grant_permission(self, codename: str) -> None:
        permission = Permission.objects.get(codename=codename, content_type__app_label="app")
        self.user.user_permissions.add(permission)

    def test_box_search_with_query(self):
        """Test box_search with a valid query"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:search"), {"q": self.box.box_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.box, response.context["boxes"])
        self.assertIn("box_count", response.context)
        self.assertGreaterEqual(response.context["box_count"], 1)

    def test_box_search_matches_basic_science_group(self):
        """Test box_search matches queries against experiment groups"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:search"), {"q": BasicScienceGroupChoices.BAIN.value})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.group_box, response.context["boxes"])

    def test_box_search_no_query(self):
        """Test box_search without query"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:search"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Null")
        self.assertIn("box_count", response.context)

    def test_box_search_with_include_used_boxes(self):
        """Test box_search with include_used_boxes parameter"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:search"), {"q": self.used_box.box_id, "include_used_boxes": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.used_box, response.context["boxes"])
        self.assertIn("box_count", response.context)

    def test_export_boxes_csv_with_query(self):
        """Test export_boxes_csv with query"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:export_csv"), {"q": self.box.box_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_export_boxes_csv_no_query(self):
        """Test export_boxes_csv without query"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:export_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_export_boxes_csv_with_include_used_boxes(self):
        """Test export_boxes_csv with include_used_boxes parameter"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:export_csv"), {"q": self.used_box.box_id, "include_used_boxes": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_box_filter(self):
        """Test box_filter view"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:filter"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("box_filter", response.context)

    def test_box_filter_filters_by_basic_science_group(self):
        """Test box_filter respects the experiment group filter"""
        other_exp = ExperimentalIDFactory(basic_science_group=BasicScienceGroupChoices.JONES)
        other_box = BasicScienceBoxFactory(experimental_ids=[other_exp])
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("boxes:filter"), {"basic_science_group": BasicScienceGroupChoices.BAIN.value}
        )
        self.assertEqual(response.status_code, 200)
        page = response.context["box_list"]
        self.assertIn(self.group_box, list(page))
        self.assertNotIn(other_box, list(page))

    def test_box_filter_pagination(self):
        """Test box_filter with pagination"""
        # Create enough boxes for pagination
        for _ in range(30):
            BasicScienceBoxFactory(created_by=self.user, last_modified_by=self.user)
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:filter"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        # Check that pagination is working (page 2 should have boxes)
        self.assertTrue(len(response.context["box_list"]) > 0)

    def test_box_filter_export_csv(self):
        """Test box_filter_export_csv"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("boxes:filter_export_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_create_experimental_id_requires_login(self):
        url = reverse("boxes:create_experimental_id")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_create_experimental_id_requires_permission(self):
        url = reverse("boxes:create_experimental_id")
        self.client.force_login(self.user)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 403)

    def test_create_experimental_id_success_returns_serialized_payload(self):
        url = reverse("boxes:create_experimental_id")
        sample_type = BasicScienceSampleTypeFactory()
        tissue_type = TissueTypeFactory()
        self.client.force_login(self.user)
        self._grant_permission("view_basicsciencebox")
        self._grant_permission("add_experimentalid")
        payload = {
            "basic_science_group": BasicScienceGroupChoices.BAIN.value,
            "name": "EXP-TEST-001",
            "description": "Test experiment",
            "date": "2024-01-01",
            "sample_types": [sample_type.pk],
            "tissue_types": [tissue_type.pk],
            "species": SpeciesChoices.HUMAN.value,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        experimental_id = data["experimental_id"]
        self.assertEqual(experimental_id["name"], payload["name"])
        self.assertEqual(experimental_id["basic_science_group"], payload["basic_science_group"])
        self.assertIn(sample_type.pk, experimental_id["sample_type_ids"])
        self.assertEqual(experimental_id["created_by"], self.user.email)
        saved_experiment = ExperimentalID.objects.get(name=payload["name"])
        self.assertEqual(saved_experiment.created_by, self.user)
        self.assertTrue(saved_experiment.sample_types.filter(pk=sample_type.pk).exists())
        self.assertTrue(saved_experiment.tissue_types.filter(pk=tissue_type.pk).exists())

    def test_create_experimental_id_invalid_returns_errors(self):
        url = reverse("boxes:create_experimental_id")
        self.client.force_login(self.user)
        self._grant_permission("view_basicsciencebox")
        initial_count = ExperimentalID.objects.count()
        response = self.client.post(
            url,
            {"basic_science_group": BasicScienceGroupChoices.BAIN.value, "species": SpeciesChoices.HUMAN.value},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("errors", data)
        self.assertIn("name", data["errors"])
        self.assertEqual(ExperimentalID.objects.count(), initial_count)


class ExperimentalIdListViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.url = reverse("boxes:experimental_id_list")
        self.active_experiment = ExperimentalIDFactory()
        self.deleted_experiment = ExperimentalIDFactory()
        self.deleted_experiment.is_deleted = True
        self.deleted_experiment.save()

    def test_view_requires_login(self):
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = ExperimentalIdListView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_lists_only_active_experiments(self):
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        experiments = list(response.context["experimental_ids"])
        self.assertIn(self.active_experiment, experiments)
        self.assertNotIn(self.deleted_experiment, experiments)


class ExperimentalIdCreateViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.url = reverse("boxes:experimental_id_create")
        self.sample_type = BasicScienceSampleTypeFactory()
        self.tissue_type = TissueTypeFactory()
        self.valid_data = {
            "basic_science_group": BasicScienceGroupChoices.BAIN.value,
            "name": "EXP-CREATE-001",
            "description": "Created via test",
            "date": "2024-01-01",
            "sample_types": [self.sample_type.pk],
            "tissue_types": [self.tissue_type.pk],
            "species": SpeciesChoices.HUMAN.value,
        }

    def test_view_requires_permission(self):
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user
        view = ExperimentalIdCreateView()
        view.request = request

        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_valid_post_creates_experiment(self):
        self.client.force_login(self.user)
        self.grant_permission("add_basicsciencebox")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        experiment = ExperimentalID.objects.get(name=self.valid_data["name"])
        self.assertEqual(experiment.created_by, self.user)
        self.assertTrue(experiment.sample_types.filter(pk=self.sample_type.pk).exists())
        self.assertTrue(experiment.tissue_types.filter(pk=self.tissue_type.pk).exists())

    def test_invalid_post_returns_errors(self):
        self.client.force_login(self.user)
        self.grant_permission("add_basicsciencebox")

        response = self.client.post(
            self.url,
            {"basic_science_group": BasicScienceGroupChoices.BAIN.value, "species": SpeciesChoices.HUMAN.value},
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("name", form.errors)
        self.assertIn("This field is required.", form.errors["name"])


class ExperimentalIdDetailViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.experimental_id = ExperimentalIDFactory()
        self.url = reverse("boxes:experimental_id_detail", kwargs={"pk": self.experimental_id.pk})

    def test_view_requires_login(self):
        request = self.factory.get(self.url)
        request.user = AnonymousUser()

        response = ExperimentalIdDetailView.as_view()(request, pk=self.experimental_id.pk)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_view_with_permission_returns_experiment(self):
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["experimental_id"], self.experimental_id)
        self.assertIn("changes", response.context)


class ExperimentalIdUpdateViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.experimental_id = ExperimentalIDFactory(name="EXP-ORIGINAL")
        self.sample_type = BasicScienceSampleTypeFactory()
        self.url = reverse("boxes:experimental_id_edit", kwargs={"pk": self.experimental_id.pk})
        date_value = self.experimental_id.date.strftime("%Y-%m-%d") if self.experimental_id.date else "2024-01-01"
        self.valid_data = {
            "basic_science_group": self.experimental_id.basic_science_group,
            "name": "EXP-UPDATED",
            "description": "Updated description",
            "date": date_value,
            "sample_types": [self.sample_type.pk],
            "tissue_types": [],
            "species": self.experimental_id.species,
        }

    def test_view_requires_permission(self):
        from django.core.exceptions import PermissionDenied

        request = self.factory.get(self.url)
        request.user = self.user
        view = ExperimentalIdUpdateView()
        view.request = request

        with self.assertRaises(PermissionDenied):
            view.dispatch(request, pk=self.experimental_id.pk)

    def test_valid_post_updates_experiment(self):
        self.client.force_login(self.user)
        self.grant_permission("change_basicsciencebox")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.experimental_id.refresh_from_db()
        self.assertEqual(self.experimental_id.name, "EXP-UPDATED")
        self.assertEqual(self.experimental_id.last_modified_by, self.user)


class ExperimentalIdDeleteViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.experimental_id = ExperimentalIDFactory(is_deleted=False)
        self.url = reverse("boxes:experimental_id_delete", kwargs={"pk": self.experimental_id.pk})

    def test_view_requires_login(self):
        request = self.factory.post(self.url)
        request.user = AnonymousUser()

        response = ExperimentalIdDeleteView.as_view()(request, pk=self.experimental_id.pk)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_post_requires_permission(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_post_marks_experiment_deleted(self):
        self.client.force_login(self.user)
        self.grant_permission("delete_basicsciencebox")

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.experimental_id.refresh_from_db()
        self.assertTrue(self.experimental_id.is_deleted)
        self.assertEqual(self.experimental_id.last_modified_by, self.user)


class ExperimentalIdRestoreViewTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.experimental_id = ExperimentalIDFactory(is_deleted=True)
        self.url = reverse("boxes:experimental_id_restore", kwargs={"pk": self.experimental_id.pk})

    def test_post_requires_permission(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_post_restores_experiment(self):
        self.client.force_login(self.user)
        self.grant_permission("delete_basicsciencebox")

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.experimental_id.refresh_from_db()
        self.assertFalse(self.experimental_id.is_deleted)
        self.assertEqual(self.experimental_id.last_modified_by, self.user)


class ExperimentalIdFunctionViewsTest(PermissionHelperMixin, TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.experiment = ExperimentalIDFactory(name="Search Target", description="Interesting experiment")
        self.other_experiment = ExperimentalIDFactory(name="Background", description="Other")

    def test_experiment_search_requires_login(self):
        url = reverse("boxes:experimental_id_search")

        response = self.client.get(url, {"q": "Search"})

        self.assertEqual(response.status_code, 302)

    def test_experiment_search_returns_matches(self):
        url = reverse("boxes:experimental_id_search")
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(url, {"q": "Search"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.experiment, response.context["experimental_ids"])

    def test_export_experiments_csv_returns_csv(self):
        url = reverse("boxes:experimental_id_export_csv")
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(url, {"q": self.experiment.name})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_experiment_filter_requires_permission(self):
        url = reverse("boxes:experimental_id_filter")
        self.client.force_login(self.user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_experiment_filter_returns_context(self):
        url = reverse("boxes:experimental_id_filter")
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("experimental_id_filter", response.context)

    def test_experimental_id_filter_export_csv_returns_csv(self):
        url = reverse("boxes:experimental_id_filter_export_csv")
        self.client.force_login(self.user)
        self.grant_permission("view_basicsciencebox")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
