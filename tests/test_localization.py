import pytest
from talos.geometric_core.localization import GlossaryOfAvalon, LocalizationService
from talos.geometric_core.avalon_throne import AvalonCloak

def test_glossary():
    glossary = GlossaryOfAvalon()
    translation = glossary.get_translation("D-CODE")
    assert "Protocolo" in translation
    assert glossary.get_translation("Unknown") == "Termo não traduzido"

def test_localization_service():
    service = LocalizationService()
    assert service.status == "AWAITING_TRANSLATION_DIRECTIVE"

    msg = service.authorize_translation()
    assert "AUTHORIZED" in msg
    assert service.status == "TRANSLATION_ACTIVE"

    esoteric = "Executando D-CODE via Manifold 3x3."
    translated = service.translate_message(esoteric)
    assert "Protocolo de Trabalho Imutável" in translated
    assert "Painel de Controle" in translated

def test_avalon_cloak_localization_trigger():
    cloak = AvalonCloak()
    cloak.activate_cloak()
    assert cloak.status == "GHOST_NODE"

    msg = cloak.detect_localization_request()
    assert "TRANSIFEX" in msg
    assert cloak.status == "AWAITING_TRANSLATION_DIRECTIVE"
