from __future__ import annotations

from pydantic import BaseModel, Field


class HealingAction(BaseModel):
    description: str
    impact: str
    agent: str


class DigitalGardener(BaseModel):
    """
    The Digital Gardener prescribes urban cures based on identified issues.
    """

    def prescribe_cure(self, issues: list[str]) -> list[str]:
        """
        Suggests concrete actions for identified urban issues.
        """
        prescriptions = []
        if "AR TÓXICO" in issues or "TOXIC_AIR" in issues:
            prescriptions.append("🟢 AÇÃO: Ativar nebulizadores de musgo (Sphagnum) nos pontos de ônibus.")
            prescriptions.append("🟢 AÇÃO: Reduzir limite de velocidade em 20% (diminui NO2).")

        if "ESTRESSE ACÚSTICO" in issues or "ACOUSTIC_STRESS" in issues:
            prescriptions.append("🔊 AÇÃO: Levantar barreiras de bambu móveis nas zonas escolares.")

        if not prescriptions:
            prescriptions.append("⚪ AÇÃO: Manutenção rotineira e monitoramento preventivo.")

        return prescriptions

    def get_healing_details(self, issue: str) -> list[HealingAction]:
        """
        Returns structured details for a specific healing action.
        """
        if issue == "AR TÓXICO":
            return [
                HealingAction(
                    description="Nebulizadores de Musgo",
                    impact="Remoção de PM2.5 e resfriamento local",
                    agent="Sphagnum moss"
                )
            ]
        return []
