import pandas as pd
from django.test import TestCase

from app.models import StudyIdentifier
from app.services import StudyIdentifierImportService


class TestStudyIdentifierImportService(TestCase):
    def setUp(self):
        # Create some existing identifiers for testing
        self.identifier1 = StudyIdentifier.objects.create(
            name="GID-101",
            study_name="Study A",
            study_center="Center 1",
            study_group="Group X",
            sex="M",
            age=30,
        )
        self.identifier2 = StudyIdentifier.objects.create(
            name="GID-102-P",  # Suffixed identifier
            study_name="Study B",
            study_center="Center 2",
            study_group="Group Y",
            sex="F",
            age=25,
        )
        self.identifier3 = StudyIdentifier.objects.create(
            name="GID-103-HC",  # Suffixed identifier
            study_name="Study C",
            study_center="Center 3",
            study_group="Group Z",
            sex="M",
            age=35,
        )

    def test_import_new_identifiers(self):
        """Test importing completely new study identifiers."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-201", "GID-202", "GID-203"],
                "study_name": ["Study D", "Study E", "Study F"],
                "study_center": ["Center 4", "Center 5", "Center 6"],
                "study_group": ["Group A", "Group B", "Group C"],
                "sex": ["F", "M", "F"],
                "age": [40, 45, 50],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["created"], 3)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)

        # Verify objects were created in the database
        self.assertEqual(StudyIdentifier.objects.count(), 6)  # 3 existing + 3 new
        self.assertTrue(StudyIdentifier.objects.filter(name="GID-201").exists())
        self.assertTrue(StudyIdentifier.objects.filter(name="GID-202").exists())
        self.assertTrue(StudyIdentifier.objects.filter(name="GID-203").exists())

    def test_update_existing_identifiers(self):
        """Test updating existing identifiers."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-101"],
                "study_name": ["Updated Study A"],
                "study_center": ["Updated Center 1"],
                "study_group": ["Updated Group X"],
                "sex": ["F"],  # Changed from M to F
                "age": [32],  # Changed from 30 to 32
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 0)

        # Verify the object was updated
        updated = StudyIdentifier.objects.get(name="GID-101")
        self.assertEqual(updated.study_name, "Updated Study A")
        self.assertEqual(updated.study_center, "Updated Center 1")
        self.assertEqual(updated.study_group, "Updated Group X")
        self.assertEqual(updated.sex, "F")
        self.assertEqual(updated.age, 32)

    def test_no_changes_to_existing_identifier(self):
        """Test that no updates happen when data is the same."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-101"],
                "study_name": ["Study A"],
                "study_center": ["Center 1"],
                "study_group": ["Group X"],
                "sex": ["M"],
                "age": [30],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 1)

    def test_match_base_id_with_suffixed_version(self):
        """Test importing an ID that matches the base of an existing suffixed ID."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-102"],  # Base of GID-102-P
                "study_name": ["New Study B"],
                "study_center": ["New Center 2"],
                "study_group": ["New Group Y"],
                "sex": ["M"],
                "age": [28],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 0)

        # Verify the suffixed object was updated
        updated = StudyIdentifier.objects.get(name="GID-102-P")
        self.assertEqual(updated.study_name, "New Study B")
        self.assertEqual(updated.sex, "M")
        self.assertEqual(updated.age, 28)

    def test_match_base_id_with_hc_suffixed_version(self):
        """Test importing an ID that matches the base of an existing -HC suffixed ID."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-103"],  # Base of GID-103-HC
                "study_name": ["New Study C"],
                "study_center": ["New Center 3"],
                "sex": ["F"],
                "age": [38],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 0)

        # Verify the suffixed object was updated
        updated = StudyIdentifier.objects.get(name="GID-103-HC")
        self.assertEqual(updated.study_name, "New Study C")
        self.assertEqual(updated.sex, "F")
        self.assertEqual(updated.age, 38)

    def test_mixed_operations(self):
        """Test a mix of creates, updates, and skips."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-101", "GID-301", "", "GID-102"],
                "study_name": ["Study A", "New Study", None, "Updated Study B"],
                "study_center": ["Center 1", "New Center", "Invalid", "Updated Center 2"],
                "sex": ["M", "F", None, "M"],
                "age": [30, 60, None, 29],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["created"], 1)  # GID-301
        self.assertEqual(result["updated"], 1)  # GID-102 (updates GID-102-P)
        self.assertEqual(result["skipped"], 1)  # GID-101 (no changes)
        # Empty row is not counted in any of the specific categories

    def test_empty_dataframe(self):
        """Test importing an empty dataframe."""
        df = pd.DataFrame()

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)

        # Verify no new objects were created
        self.assertEqual(StudyIdentifier.objects.count(), 3)

    def test_partial_data_fields(self):
        """Test importing data with only some fields present."""
        df = pd.DataFrame(
            {
                "study_id": ["GID-401", "GID-402"],
                "study_name": ["Partial Study A", "Partial Study B"],
                # Missing other fields
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Check the result counters
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["created"], 2)

        # Verify objects were created with partial data
        new_id1 = StudyIdentifier.objects.get(name="GID-401")
        self.assertEqual(new_id1.study_name, "Partial Study A")
        self.assertIsNone(new_id1.study_center)
        self.assertIsNone(new_id1.study_group)
        self.assertIsNone(new_id1.sex)
        self.assertIsNone(new_id1.age)

    def test_case_insensitivity(self):
        """Test that study IDs are case-insensitive."""
        df = pd.DataFrame(
            {
                "study_id": ["gid-101", "gid-501"],  # lowercase
                "study_name": ["Updated Case Study", "New Case Study"],
            }
        )

        result = StudyIdentifierImportService.import_from_dataframe(df)

        # Should update GID-101 and create GID-501 (uppercase in db)
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["updated"], 1)

        # Verify case was standardized
        self.assertTrue(StudyIdentifier.objects.filter(name="GID-101").exists())
        self.assertTrue(StudyIdentifier.objects.filter(name="GID-501").exists())
        self.assertFalse(StudyIdentifier.objects.filter(name="gid-501").exists())
