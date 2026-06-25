from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


@dataclass
class Scenario:
    scenario_id: str
    data_quality_risk: float
    supervised_model_confidence: float
    image_model_status: str
    generative_quality_flag: str
    patient_facing: bool


def integrated_route(scenario: Scenario) -> dict:
    score = scenario.data_quality_risk
    score += max(0.0, 0.72 - scenario.supervised_model_confidence)
    if scenario.image_model_status == "uncertain":
        score += 0.18
    if scenario.generative_quality_flag == "outlier":
        score += 0.16
    score = min(1.0, round(score, 3))

    if scenario.patient_facing:
        decision = "human approval required"
    elif score >= 0.70:
        decision = "expedited review"
    elif score >= 0.40:
        decision = "data quality review"
    else:
        decision = "standard operations queue"

    return {
        "scenario_id": scenario.scenario_id,
        "integrated_risk_score": score,
        "decision": decision,
        "components": {
            "statistical_data_quality": scenario.data_quality_risk,
            "supervised_ml_confidence": scenario.supervised_model_confidence,
            "deep_learning_status": scenario.image_model_status,
            "generative_ai_quality_flag": scenario.generative_quality_flag,
            "agentic_boundary": "human approval" if scenario.patient_facing else "internal routing",
        },
    }


def main() -> list[dict]:
    scenarios = [
        Scenario("SYN-001", 0.12, 0.91, "confident", "in-distribution", False),
        Scenario("SYN-002", 0.36, 0.64, "uncertain", "in-distribution", False),
        Scenario("SYN-003", 0.18, 0.86, "confident", "outlier", True),
        Scenario("SYN-004", 0.50, 0.58, "uncertain", "outlier", False),
    ]
    outputs = [integrated_route(item) for item in scenarios]
    OUT.mkdir(exist_ok=True)
    (OUT / "integrated_scenario_results.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    for item in outputs:
        print(f"{item['scenario_id']}: {item['decision']} ({item['integrated_risk_score']})")
    return outputs


if __name__ == "__main__":
    main()
