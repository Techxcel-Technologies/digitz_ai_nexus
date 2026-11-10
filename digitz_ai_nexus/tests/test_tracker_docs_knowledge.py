"""Offline checks for scope, replacement identities and current help coverage."""
import copy
import hashlib
import json
import os
import unittest
from pathlib import Path

from digitz_ai_nexus.devtools.build_tracker_docs_knowledge import (
    APP, DEFAULT_TARGET, replace_tracker, tracker_entries,
)


class TestTrackerDocsKnowledge(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DEFAULT_TARGET.read_text())
        self.entries = [e for e in self.payload['entries'] if e['app'] == APP]

    def test_all_legacy_identities_are_replaced(self):
        legacy = {'Overview', 'Key Concepts', 'Quick Start', 'Document Registration',
                  'Expiry Automation & Alerts', 'Employee Assignments',
                  'Status Tracking', 'Renewal Workflow'}
        self.assertTrue(legacy.issubset({e['topic'] for e in self.entries}))
        self.assertEqual(len(self.entries), 16)
        self.assertEqual(self.payload['count'], len(self.payload['entries']))
        self.assertEqual(len({e['title'] for e in self.payload['entries']}), self.payload['count'])
        self.assertTrue(all(e['context'] == 'DIGITZ-TRACKER' for e in self.entries))

    def test_replacement_is_idempotent_and_preserves_other_products(self):
        original = copy.deepcopy(self.payload)
        others = [e for e in original['entries'] if e['app'] != APP]
        once = replace_tracker(self.payload, self.entries)
        self.assertEqual(once, replace_tracker(once, self.entries))
        self.assertEqual(others, [e for e in once['entries'] if e['app'] != APP])
        self.assertEqual(original, self.payload)
        self.assertTrue(any(e['app'] == 'DIGITZ Service Tracker' for e in others))

    def test_orphaned_sources_and_duplicates_are_rejected(self):
        with self.assertRaises(ValueError):
            replace_tracker(self.payload, self.entries[1:])
        with self.assertRaises(ValueError):
            replace_tracker(self.payload, self.entries + self.entries[:1])

    def test_current_model_and_user_paths_are_present(self):
        content = '\n'.join(e['content'] for e in self.entries)
        for term in ('Tracked Document', 'Document Cycle', '/tracker/documents',
                     '/tracker/work', '/tracker/portal', 'Company Administrator',
                     'Register and track', 'Waiting on', 'AI Assistant'):
            self.assertIn(term, content)
        for term in ('v0_1_0.document_model_3', 'It deletes all tracker data',
                     'digitz_tracker/porting/TECHNICAL.md'):
            self.assertNotIn(term, content)

    def test_rebuild_matches_exact_recorded_inputs_when_tracker_available(self):
        source_root = os.environ.get('TRACKER_DOCS_ROOT')
        if not source_root:
            self.skipTest('Set TRACKER_DOCS_ROOT to verify against the pinned release')
        root = Path(source_root)
        self.assertEqual(self.entries, tracker_entries(root))
        for entry in self.entries:
            source = entry['source_document']
            self.assertEqual(source['sha256'], hashlib.sha256(
                (root / source['path']).read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
