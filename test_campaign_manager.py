import unittest
import json
import yaml
from unittest.mock import MagicMock, patch
from campaign_manager import LandingPageAgent, sync_crm, generate_content, deploy_page  # Import tools/functions to test

class TestRadiantLaunchAgent(unittest.TestCase):
    def setUp(self):
        # Mock config
        self.mock_config = {
            'enable_mcp': False,
            'custom_templates': {'services': {'features': ['Whitening', 'Aligners'], 'cta': 'Book Now'}},
            'grok_prompt_override': 'Test override'
        }
        # Mock leads
        self.mock_leads = [{"email": "test@clinic.com", "name": "Test Lead"}]

    def test_sync_crm_pull_success(self):
        """Test CRM pull with filter."""
        result = sync_crm("pull", {"filter": "clinic"})
        self.assertIn("Pulled 1 leads", result)
        self.assertIsInstance(result, str)

    def test_sync_crm_push_success(self):
        """Test CRM push adds lead."""
        initial_len = len(self.mock_leads)
        result = sync_crm("push", {"email": "new@test.com", "name": "New Lead"})
        self.assertIn("Lead pushed: new@test.com", result)
        self.assertEqual(len(self.mock_leads), initial_len + 1)

    def test_generate_content_fallback(self):
        """Test content gen with mock Grok fallback."""
        inputs = {}
        with patch('langchain_groq.ChatGroq') as mock_llm:
            mock_llm.invoke.return_value = MagicMock(content='{"description": "Test desc", "features": ["Test 1"], "cta_text": "Test CTA"}')
            result = generate_content(inputs)
        self.assertIn('<h1 class="display-4 fw-bold">Test Service</h1>', result)  # Checks HTML output
        self.assertIsInstance(result, str)

    def test_deploy_page_netlify(self):
        """Test deploy generates URL."""
        result = deploy_page("mock_html", "Netlify")
        self.assertIn("Deployed to Netlify: https", result)
        self.assertIn("radiant_launch", result)

    def test_error_handling_in_sync_crm(self):
        """Test CRM error fallback."""
        with self.assertLogs(logger, level='ERROR'):
            result = sync_crm("invalid", {})
        self.assertIn("fallback mock", result)

if __name__ == '__main__':
    unittest.main()