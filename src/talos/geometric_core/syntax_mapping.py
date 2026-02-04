from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict


class SyntaxFormat(str, Enum):
    JSON_LD = "json-ld"
    TURTLE = "turtle"
    RDF_XML = "rdf-xml"
    ISO_ADA = "iso-8652"
    ISO_C = "iso-9899"
    ISO_CPP = "iso-14882"
    ISO_CSHARP = "iso-23270"
    ISO_COBOL = "iso-1989"
    ISO_EIFFEL = "iso-25436"
    ISO_FORTRAN = "iso-1539"
    ISO_PROLOG = "iso-13211"
    ISO_RUBY = "iso-30170"


class SyntaxMapper:
    """
    Maps Web777 ontology nodes to different semantic formats and ISO standard templates.
    """

    def to_json_ld(self, node_data: Dict[str, Any]) -> str:
        return json.dumps({"@context": "https://web777.org/context", "@type": "Concept", **node_data})

    def map_to_iso(self, concept: str, format: SyntaxFormat) -> str:
        """
        Maps a geometric concept to an ISO standard logic pattern.
        """
        templates = {
            SyntaxFormat.ISO_ADA: f"-- ISO/IEC 8652:2023 compliant logic for {concept}\nprocedure {concept} is begin null; end {concept};",
            SyntaxFormat.ISO_C: f"/* ISO/IEC 9899:2024 compliant logic for {concept} */\nvoid {concept}() {{ }}",
            SyntaxFormat.ISO_CPP: f"// ISO/IEC 14882:2024 compliant logic for {concept}\nnamespace {concept} {{ class Manifest {{}}; }}",
            SyntaxFormat.ISO_CSHARP: f"// ISO/IEC 23270 compliant logic for {concept}\nnamespace {concept} {{ public class Manifest {{ }} }}",
            SyntaxFormat.ISO_RUBY: f"# ISO/IEC 30170 compliant logic for {concept}\ndef {concept}; end",
            SyntaxFormat.ISO_PROLOG: f"% ISO/IEC 13211-1 compliant logic for {concept}\nconcept({concept}).",
        }
        return templates.get(format, f"Concept {concept} mapped to {format.value}")
