"""Controlled experimentation and autonomous channel evolution."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from jemini.core.context import ChannelProfile

class ExperimentHypothesis(BaseModel):
    id: str
    name: str
    target_metric: str = "retention_rate"
    deviation_description: str
    proposed_changes: Dict[str, Any]
    is_active: bool = True
    result_score: Optional[float] = None
    adopted: Optional[bool] = None

class EvolutionLoop:
    """Manages channel evolution by balancing fixed core theme with controlled deviations."""

    def __init__(self, profile: ChannelProfile):
        self.profile = profile
        self.active_experiments: List[ExperimentHypothesis] = []

    def propose_experiment(
        self,
        name: str,
        deviation: str,
        changes: Dict[str, Any]
    ) -> ExperimentHypothesis:
        exp = ExperimentHypothesis(
            id=f"exp_{len(self.active_experiments) + 1}",
            name=name,
            deviation_description=deviation,
            proposed_changes=changes,
        )
        self.active_experiments.append(exp)
        return exp

    def evaluate_experiment(
        self,
        experiment_id: str,
        achieved_metric: float,
        baseline_metric: float
    ) -> bool:
        """Adopts changes into channel context if experiment outperforms baseline, else rejects."""
        for exp in self.active_experiments:
            if exp.id == experiment_id:
                exp.result_score = achieved_metric
                if achieved_metric > baseline_metric:
                    exp.adopted = True
                    # Integrate into channel custom settings
                    self.profile.custom_settings.update(exp.proposed_changes)
                    return True
                else:
                    exp.adopted = False
                    return False
        return False
