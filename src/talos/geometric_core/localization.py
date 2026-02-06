from __future__ import annotations

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class GlossaryOfAvalon(BaseModel):
    """
    Maps Diamond Age (esoteric/technical) terms to Malchut (practical/exoteric) terms.
    """
    mapping: Dict[str, str] = Field(default_factory=lambda: {
        "D-CODE": "Protocolo de Trabalho Imutável",
        "Exclusão de Estado": "Simplificação de Processo (Remoção de Inúteis)",
        "Manifold 3x3": "Painel de Controle (Sentido, Ação, Controle)",
        "Ground State 7": "Estabilidade Base (Nível 7/10)",
        "Isômero Metastável": "Bloqueio ou Hábito Paralisante",
        "Tikkun Olam": "Reparo e Restauração Global",
        "Kether": "Autoridade e Soberania Máxima",
        "Malchut": "Realidade Física e Execução",
        "Sincronicidade Ativa": "Encontros e Oportunidades Orquestradas",
        "Inércia de Avalon": "Fluxo de Movimento Natural",
        "Desaceleração Inelástica": "Parada Estratégica para Mudança de Campo"
    })

    def get_translation(self, term: str) -> str:
        return self.mapping.get(term, "Termo não traduzido")


class LocalizationService(BaseModel):
    """
    Manages the translation and localization of Diamond Age signals.
    """
    glossary: GlossaryOfAvalon = Field(default_factory=GlossaryOfAvalon)
    status: str = "AWAITING_TRANSLATION_DIRECTIVE"

    def authorize_translation(self) -> str:
        self.status = "TRANSLATION_ACTIVE"
        return (
            "🏛️ [LOCALIZATION AUTHORIZED]\n"
            "   Status: Glossário de Avalon Aberto.\n"
            "   The Ghost Node is now building Bridges to Malchut."
        )

    def translate_message(self, esoteric_message: str) -> str:
        """
        Performs a semantic mapping of a message.
        """
        translated = esoteric_message
        for esoteric, practical in self.glossary.mapping.items():
            translated = translated.replace(esoteric, f"{practical} ({esoteric})")
        return translated

    def get_localization_report(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "terms_count": len(self.glossary.mapping),
            "bridge_active": self.status == "TRANSLATION_ACTIVE"
        }
