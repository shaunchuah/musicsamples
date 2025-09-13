from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse, reverse_lazy

from app.factories import BasicScienceBoxFactory
from app.models import BasicScienceBox
from app.views.box_views import (
    BasicScienceBoxCreateView,
    BasicScienceBoxDeleteView,
    BasicScienceBoxDetailView,
    BasicScienceBoxListView,
    BasicScienceBoxUpdateView,
)
from users.factories import UserFactory


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

    def test_view_context_contains_filter(self):
        """Test that the view context contains the filter"""
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
        self.assertIn("filter", response.context)

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

    def test_paginate_by_attribute(self):
        """Test that the view has the correct pagination"""
        view = BasicScienceBoxListView()
        self.assertEqual(view.paginate_by, 25)


class BasicScienceBoxCreateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.url = reverse("boxes:create")
        self.valid_data = {
            "basic_science_group": "bain",
            "box_id": "TEST001",
            "box_type": "basic_science_samples",
            "species": "human",
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
            "basic_science_group": "bain",
            "box_id": "UPDATED001",
            "box_type": "basic_science_samples",
            "species": "human",
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

    def test_create_experimental_id_success(self):
        """Test create_experimental_id with valid data"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        data = {"name": "Test Exp", "description": "Test description"}
        response = self.client.post(reverse("boxes:create_experimental_id"), data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response["success"])

    def test_create_experimental_id_invalid(self):
        """Test create_experimental_id with invalid data"""
        self.user.user_permissions.add(
            self.user.user_permissions.model.objects.get_or_create(
                codename="view_basicsciencebox", defaults={"name": "Can view basic science box"}
            )[0]
        )
        self.client.force_login(self.user)
        data = {}  # Invalid data
        response = self.client.post(reverse("boxes:create_experimental_id"), data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response["success"])

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

    def test_box_filter_pagination(self):
        """Test box_filter with pagination"""
        # Create enough boxes for pagination
        for _ in range(30):
            BasicScienceBoxFactory()
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
