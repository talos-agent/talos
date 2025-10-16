from __future__ import annotations

from typing import Any

from pydantic import Field

from talos.tools import WebSearchTool
from talos.tools.base import SupervisedTool


class PseudonymHelperTool(SupervisedTool):
    """A tool to help public figures publish academic work under a pseudonym."""

    name: str = "pseudonym_helper"
    description: str = "Helps with the process of publishing academic work under a pseudonym."
    action: str = Field(..., description="The action to perform: 'check', 'template', or 'checklist'.")
    pseudonym: str | None = Field(None, description="The pseudonym to check for name collisions.")

    def _run_unsupervised(self, action: str, pseudonym: str | None = None, **kwargs: Any) -> str:
        """Runs the specified action."""
        if action == "check":
            if not pseudonym:
                return "Error: A pseudonym must be provided for the 'check' action."
            return self.check_name_collision(pseudonym)
        elif action == "template":
            return self.generate_legal_template()
        elif action == "checklist":
            return self.get_submission_checklist()
        else:
            return "Error: Invalid action. Valid actions are 'check', 'template', or 'checklist'."

    def check_name_collision(self, pseudonym: str) -> str:
        """Checks for name collisions on Google Scholar and ORCID."""
        search_tool = WebSearchTool()
        google_scholar_query = f'site:scholar.google.com "{pseudonym}"'
        orcid_query = f'site:orcid.org "{pseudonym}"'

        google_scholar_results = search_tool._run(google_scholar_query)
        orcid_results = search_tool._run(orcid_query)

        response = f"Collision check for '{pseudonym}':\n\n"
        response += f"Google Scholar results:\n{google_scholar_results}\n\n"
        response += f"ORCID results:\n{orcid_results}"

        return response

    def generate_legal_template(self) -> str:
        """Generates a markdown template for the notarised declaration."""
        return """
# DECLARAÇÃO DE PSEUDÔNIMO

Eu, [Nome Completo], portador(a) do CPF nº [Número do CPF], RG nº [Número do RG], residente e domiciliado(a) em [Endereço Completo], declaro para os devidos fins que, para fins de publicação acadêmica, utilizarei o pseudônimo **[Pseudônimo]**.

Esta declaração é feita para garantir a rastreabilidade legal da minha autoria, enquanto preserva minha privacidade na publicação.

[Cidade], [Data].

_________________________
[Seu Nome Completo]
"""

    def get_submission_checklist(self) -> str:
        """Returns the submission workflow checklist."""
        return """
### Pseudonym Submission Workflow Checklist

1.  **Manuscript Preparation:**
    *   [ ] List the pseudonym on the title page.
    *   [ ] List the pseudonym in the cover letter.
    *   [ ] List the pseudonym in author contribution statements.

2.  **Cover Letter:**
    *   [ ] State clearly that the submission is under a pseudonym.
    *   [ ] Mention that a notarised declaration is attached for the editor.
    *   [ ] Provide a contact for follow-up.

3.  **Uploads:**
    *   [ ] Upload the notarised declaration in the "Additional Files for Editors Only" section.

4.  **ORCID:**
    *   [ ] Add your ORCID iD.
    *   [ ] Add the pseudonym as a non-public "also-known-as" entry.

5.  **Conflict of Interest (COI):**
    *   [ ] Disclose any COI under your real name.
"""
