# /Users/chershiongchuah/Developer/musicsamples/core/utils/history.py
# This module handles historical changes tracking for model instances.
# It processes simple history diffs for audit and change visualization.

import dataclasses


def historical_changes(query):
    # Historical changes integrates simple history into the sample detail page
    changes = []
    if query is not None:
        last = query.first()
        for all_changes in range(query.count()):
            new_record, old_record = last, last.prev_record
            if old_record is not None:
                delta = new_record.diff_against(old_record)

                # Prepare a new list for processed changes
                processed_changes = []
                for change in delta.changes:
                    # Copy the change to avoid mutating a frozen instance
                    change_dict = change.__dict__.copy()
                    # Check if the field is 'study_id' (or any other FK field you want to handle)
                    if change.field == "study_id":
                        if change.old is not None:
                            try:
                                from app.models import StudyIdentifier

                                old_instance = StudyIdentifier.objects.get(pk=change.old)
                                change_dict["old"] = str(old_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):  # type: ignore
                                pass
                        if change.new is not None:
                            try:
                                from app.models import StudyIdentifier

                                new_instance = StudyIdentifier.objects.get(pk=change.new)
                                change_dict["new"] = str(new_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):  # type: ignore
                                pass
                    # Recreate the change object (assumes it's a dataclass)
                    processed_change = dataclasses.replace(change, **change_dict)
                    processed_changes.append(processed_change)

                # Replace delta.changes with processed_changes
                new_delta = dataclasses.replace(delta, changes=processed_changes)
                changes.append(new_delta)
                last = old_record
        return changes
