import unittest
from unittest.mock import patch

from talos.tools.pseudonym_helper import PseudonymHelperTool


class TestPseudonymHelperTool(unittest.TestCase):
    @patch("talos.tools.pseudonym_helper.WebSearchTool")
    def test_check_name_collision(self, mock_web_search_tool):
        # Arrange
        mock_search_instance = mock_web_search_tool.return_value
        mock_search_instance._run.return_value = "No results found."
        tool = PseudonymHelperTool(action="check", pseudonym="J.B. Arca")

        # Act
        result = tool._run_unsupervised(action="check", pseudonym="J.B. Arca")

        # Assert
        self.assertIn("Collision check for 'J.B. Arca'", result)
        self.assertIn("Google Scholar results:\nNo results found.", result)
        self.assertIn("ORCID results:\nNo results found.", result)
        mock_search_instance._run.assert_any_call('site:scholar.google.com "J.B. Arca"')
        mock_search_instance._run.assert_any_call('site:orcid.org "J.B. Arca"')

    def test_generate_legal_template(self):
        # Arrange
        tool = PseudonymHelperTool(action="template")

        # Act
        result = tool._run_unsupervised(action="template")

        # Assert
        self.assertIn("# DECLARAÇÃO DE PSEUDÔNIMO", result)
        self.assertIn("[Nome Completo]", result)
        self.assertIn("[Pseudônimo]", result)

    def test_get_submission_checklist(self):
        # Arrange
        tool = PseudonymHelperTool(action="checklist")

        # Act
        result = tool._run_unsupervised(action="checklist")

        # Assert
        self.assertIn("### Pseudonym Submission Workflow Checklist", result)
        self.assertIn("[ ] List the pseudonym on the title page.", result)


if __name__ == "__main__":
    unittest.main()
