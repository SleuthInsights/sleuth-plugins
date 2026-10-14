---
type: regex
target: mock_calls
pattern: '\b(get_health|list_projects|get_project|create_project|send_message|wait_for_update|get_messages|list_datasets|get_dataset|list_dataset_versions|download_dataset_csv|export_project|list_artifacts|get_artifact)\b'
match: not_contains
arm: with-only
---
