"""Exercise API request boundaries, provider failures and persisted drafts."""
import base64
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch, Mock

import requests
from PIL import Image

import language_service as service


def answer(images=False):
    return {'summary': 'A176 surface scratch reported.', 'category': 'scratch', 'priority': 'high',
            'reply_draft': 'Thank you. Please send a close-up and the LOT number for review.',
            'next_actions': ['Send a close-up'], 'reference_ids': ['known', 'invented'],
            'needs_human_review': True,
            'image_observations': [{'image_number': 1, 'location': 'upper edge',
                'observation': 'A thin surface line is visible.', 'suspected_issue': 'scratch'}] if images else []}


def response(result):
    return Mock(status_code=200, json=Mock(return_value={'id': 'response-test', 'status': 'completed',
        'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(result)}]}]}))


class LanguageTests(unittest.TestCase):
    def call(self, images=None):
        return service.generate('A176', 'Please review this surface scratch.', '', images or [],
                                {'images': []}, [{'id': 'known', 'text': 'Visual inspection reference.'}], 'en')

    def test_no_key_keeps_local_features_available(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}), patch.object(service.requests, 'post') as post:
            self.assertEqual(self.call()['status'], 'not_configured')
            post.assert_not_called()

    def test_grounded_reply_and_photo_payload(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'local-unit-test-placeholder'}), \
             patch.object(service.requests, 'post', return_value=response(answer(True))) as post:
            result = self.call([Image.new('RGB', (32, 24), 'gray')])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['reference_ids'], ['known'])
        payload = post.call_args.kwargs['json']
        self.assertFalse(payload['store'])
        self.assertTrue(payload['text']['format']['strict'])
        self.assertEqual(payload['input'][0]['content'][-1]['type'], 'input_image')
        self.assertTrue(payload['input'][0]['content'][-1]['image_url'].startswith('data:image/jpeg;base64,'))

    def test_provider_failures_do_not_return_secrets_or_provider_bodies(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'local-unit-test-placeholder'}):
            for status, expected in [(401, 'authentication_failed'), (403, 'authentication_failed'),
                                     (429, 'rate_limited'), (500, 'unavailable')]:
                with patch.object(service.requests, 'post', return_value=Mock(status_code=status)):
                    result = self.call()
                self.assertEqual(result['status'], expected)
                self.assertNotIn('local-unit-test-placeholder', json.dumps(result))
            with patch.object(service.requests, 'post', side_effect=requests.Timeout()):
                self.assertEqual(self.call()['status'], 'unavailable')

    def test_invalid_image_reference_is_rejected(self):
        result = answer(True)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'local-unit-test-placeholder'}), \
             patch.object(service.requests, 'post', return_value=response(result)):
            self.assertEqual(self.call()['status'], 'unavailable')

    def test_api_result_persists_with_complaint_and_admin_record(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'MM_DATA_DIR': tmp,
                'OPENAI_API_KEY': 'local-unit-test-placeholder', 'ADMIN_PASSWORD': 'unit-test-password'}):
            import app as module
            client = module.app.test_client()
            with patch.object(service.requests, 'post', return_value=response(answer())):
                result = client.post('/api/analyze', json={'product': 'AUTO',
                    'message': 'Please inspect the scratch on A 176.', 'language': 'en'} )
            self.assertEqual(result.status_code, 201)
            data = result.get_json()
            self.assertEqual(data['analysis']['language']['status'], 'complete')
            self.assertEqual(data['analysis']['vision']['detection_count'], 0)
            cid = data['id']
            self.assertEqual(client.post(f'/api/complaints/{cid}/confirm').status_code, 200)
            self.assertEqual(client.post('/api/admin/login', json={'username': module.ADMIN_USER,
                'password': module.ADMIN_PASSWORD}).status_code, 200)
            record = client.get('/api/admin/complaints').get_json()[0]
            self.assertEqual(record['product'], 'A176')
            self.assertEqual(record['priority'], '높음')
            self.assertEqual(record['analysis']['language']['reply_draft'], answer()['reply_draft'])


if __name__ == '__main__':
    unittest.main()
