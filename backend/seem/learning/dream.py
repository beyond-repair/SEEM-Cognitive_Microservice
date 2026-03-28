from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random


@dataclass
class RouteVariant:
    id: str
    original_id: str
    k_lambda: float
    max_iters: int
    fitness: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "original_id": self.original_id,
            "k_lambda": self.k_lambda,
            "max_iters": self.max_iters,
            "fitness": self.fitness,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class ConsolidatedSkill:
    id: str
    name: str
    variants: List[RouteVariant] = field(default_factory=list)
    best_variant_id: str = ""
    consolidated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total_success_count: int = 0
    total_failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def overall_fitness(self) -> float:
        if not self.variants:
            return 0.0
        return sum(v.fitness for v in self.variants) / len(self.variants)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "variants": [v.to_dict() for v in self.variants],
            "best_variant_id": self.best_variant_id,
            "overall_fitness": self.overall_fitness,
            "consolidated_at": self.consolidated_at,
            "total_success_count": self.total_success_count,
            "total_failure_count": self.total_failure_count,
            "metadata": self.metadata,
        }


class DreamPhaseEngine:
    def __init__(
        self,
        population_size: int = 50,
        elite_size: int = 5,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.7,
        consolidation_threshold: float = 0.75,
    ):
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.consolidation_threshold = consolidation_threshold

        self.route_variants: Dict[str, List[RouteVariant]] = {}
        self.consolidated_skills: Dict[str, ConsolidatedSkill] = {}
        self.dream_cycle_count = 0

    def create_variant(
        self,
        original_id: str,
        base_k_lambda: float = 0.5,
        base_max_iters: int = 7,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouteVariant:
        variant_id = f"{original_id}_v{len(self.route_variants.get(original_id, []))}"

        k_lambda = base_k_lambda + random.uniform(-0.1, 0.1)
        k_lambda = max(0.1, min(1.0, k_lambda))

        max_iters = base_max_iters + random.randint(-1, 2)
        max_iters = max(3, min(10, max_iters))

        variant = RouteVariant(
            id=variant_id,
            original_id=original_id,
            k_lambda=k_lambda,
            max_iters=max_iters,
            metadata=metadata or {},
        )

        if original_id not in self.route_variants:
            self.route_variants[original_id] = []
        self.route_variants[original_id].append(variant)

        return variant

    def record_variant_execution(
        self,
        variant_id: str,
        success: bool,
        fitness_score: float,
    ) -> None:
        for variants_list in self.route_variants.values():
            for variant in variants_list:
                if variant.id == variant_id:
                    if success:
                        variant.success_count += 1
                    else:
                        variant.failure_count += 1
                    variant.fitness = (
                        variant.fitness * 0.8 + fitness_score * 0.2
                    )
                    return

    def select_elite(self, original_id: str) -> List[RouteVariant]:
        variants = self.route_variants.get(original_id, [])
        if not variants:
            return []

        sorted_variants = sorted(
            variants,
            key=lambda v: (v.success_rate, v.fitness),
            reverse=True,
        )
        return sorted_variants[:self.elite_size]

    def crossover(
        self,
        parent1: RouteVariant,
        parent2: RouteVariant,
    ) -> RouteVariant:
        if random.random() < 0.5:
            k_lambda = parent1.k_lambda
        else:
            k_lambda = parent2.k_lambda

        if random.random() < 0.5:
            max_iters = parent1.max_iters
        else:
            max_iters = parent2.max_iters

        offspring = RouteVariant(
            id=f"{parent1.original_id}_cross_{random.randint(1000, 9999)}",
            original_id=parent1.original_id,
            k_lambda=k_lambda,
            max_iters=max_iters,
            fitness=(parent1.fitness + parent2.fitness) / 2,
        )
        return offspring

    def mutate(self, variant: RouteVariant) -> RouteVariant:
        mutated = RouteVariant(
            id=f"{variant.original_id}_mut_{random.randint(1000, 9999)}",
            original_id=variant.original_id,
            k_lambda=variant.k_lambda + random.uniform(-0.05, 0.05),
            max_iters=variant.max_iters + random.randint(-1, 1),
            fitness=variant.fitness,
        )
        mutated.k_lambda = max(0.1, min(1.0, mutated.k_lambda))
        mutated.max_iters = max(3, min(10, mutated.max_iters))
        return mutated

    def run_dream_cycle(self, original_id: str) -> List[RouteVariant]:
        elite = self.select_elite(original_id)
        if not elite:
            return []

        new_generation = elite.copy()

        while len(new_generation) < self.population_size:
            if random.random() < self.crossover_rate and len(elite) > 1:
                parent1, parent2 = random.sample(elite, 2)
                offspring = self.crossover(parent1, parent2)
                new_generation.append(offspring)
            elif random.random() < self.mutation_rate:
                parent = random.choice(elite)
                offspring = self.mutate(parent)
                new_generation.append(offspring)
            else:
                new_generation.append(random.choice(elite))

        self.route_variants[original_id] = new_generation[:self.population_size]
        self.dream_cycle_count += 1

        return new_generation

    def consolidate_skill(self, original_id: str, skill_name: str) -> Optional[ConsolidatedSkill]:
        elite = self.select_elite(original_id)
        if not elite:
            return None

        best_variant = elite[0]
        if best_variant.fitness < self.consolidation_threshold:
            return None

        skill = ConsolidatedSkill(
            id=f"skill_{original_id}_{self.dream_cycle_count}",
            name=skill_name,
            variants=elite,
            best_variant_id=best_variant.id,
            total_success_count=sum(v.success_count for v in elite),
            total_failure_count=sum(v.failure_count for v in elite),
        )

        self.consolidated_skills[skill.id] = skill
        return skill

    def get_best_variant(self, original_id: str) -> Optional[RouteVariant]:
        elite = self.select_elite(original_id)
        return elite[0] if elite else None

    def get_consolidated_skills(self) -> List[ConsolidatedSkill]:
        return list(self.consolidated_skills.values())

    def get_skill_by_id(self, skill_id: str) -> Optional[ConsolidatedSkill]:
        return self.consolidated_skills.get(skill_id)

    def get_statistics(self) -> Dict[str, Any]:
        total_variants = sum(len(v) for v in self.route_variants.values())
        total_skills = len(self.consolidated_skills)

        avg_fitness = 0.0
        if total_variants > 0:
            avg_fitness = sum(
                v.fitness
                for variants in self.route_variants.values()
                for v in variants
            ) / total_variants

        return {
            "dream_cycles": self.dream_cycle_count,
            "total_variants": total_variants,
            "total_consolidated_skills": total_skills,
            "average_variant_fitness": avg_fitness,
            "population_size": self.population_size,
        }
