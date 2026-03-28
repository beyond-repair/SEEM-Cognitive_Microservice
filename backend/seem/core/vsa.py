import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Hypervector:
    vector: np.ndarray
    dimension: int = 16384
    dtype: str = "complex128"

    def __post_init__(self):
        if self.vector.size == 0:
            self.vector = np.zeros(self.dimension, dtype=np.complex128)
        if len(self.vector.shape) > 1:
            self.vector = self.vector.flatten()

    def normalize(self) -> "Hypervector":
        norm = np.linalg.norm(self.vector)
        if norm == 0:
            return Hypervector(self.vector.copy(), self.dimension)
        normalized = self.vector / norm
        return Hypervector(normalized, self.dimension)

    def cosine_similarity(self, other: "Hypervector") -> float:
        a = self.vector / (np.linalg.norm(self.vector) + 1e-10)
        b = other.vector / (np.linalg.norm(other.vector) + 1e-10)
        return float(np.real(np.dot(a.conj(), b)))

    def bind(self, other: "Hypervector") -> "Hypervector":
        bound = self.vector * np.conj(other.vector)
        return Hypervector(bound, self.dimension).normalize()

    def unbind(self, bound: "Hypervector") -> "Hypervector":
        unbound = bound.vector * np.conj(self.vector)
        return Hypervector(unbound, self.dimension).normalize()

    def bundle(self, other: "Hypervector") -> "Hypervector":
        bundled = self.vector + other.vector
        return Hypervector(bundled, self.dimension).normalize()


class ResonatorVSA:
    def __init__(
        self,
        dimension: int = 16384,
        max_iterations: int = 7,
        invertibility_threshold: float = 0.92,
        sparsity_ratio: float = 0.1,
    ):
        self.dimension = dimension
        self.max_iterations = max_iterations
        self.invertibility_threshold = invertibility_threshold
        self.sparsity_ratio = sparsity_ratio
        self.symbol_codebook: dict[str, Hypervector] = {}
        self.iteration_log: list[dict] = []

    def create_random_hypervector(self) -> Hypervector:
        real = np.random.randn(self.dimension)
        imag = np.random.randn(self.dimension)
        vector = real + 1j * imag
        return Hypervector(vector, self.dimension).normalize()

    def encode_symbol(self, symbol_id: str) -> Hypervector:
        if symbol_id in self.symbol_codebook:
            return self.symbol_codebook[symbol_id]

        hv = self.create_random_hypervector()
        self.symbol_codebook[symbol_id] = hv
        return hv

    def bind_symbols(
        self, symbol1_id: str, symbol2_id: str
    ) -> Hypervector:
        hv1 = self.encode_symbol(symbol1_id)
        hv2 = self.encode_symbol(symbol2_id)
        return hv1.bind(hv2)

    def resonator_loop(
        self,
        query: Hypervector,
        context: Hypervector,
        target: Hypervector,
    ) -> Tuple[Hypervector, float, int]:
        current = query.copy()
        best_cosine = 0.0
        best_result = current
        iterations = 0

        for i in range(self.max_iterations):
            iterations = i + 1
            resonated = current.bundle(context)
            cosine_sim = resonated.cosine_similarity(target)

            if cosine_sim > best_cosine:
                best_cosine = cosine_sim
                best_result = resonated

            self.iteration_log.append({
                "iteration": i,
                "cosine_similarity": cosine_sim,
                "norm": float(np.linalg.norm(resonated.vector)),
            })

            if cosine_sim >= self.invertibility_threshold:
                break

            perturbation = self.create_random_hypervector()
            current = resonated.bundle(perturbation)

        return best_result, best_cosine, iterations

    def unbind_with_resonance(
        self,
        bound_vector: Hypervector,
        filler: Hypervector,
        max_attempts: int = 3,
    ) -> Tuple[Hypervector, float, int]:
        best_unbound = bound_vector
        best_cosine = 0.0
        total_iterations = 0

        for attempt in range(max_attempts):
            unbound = filler.unbind(bound_vector)
            resonated, cosine, iters = self.resonator_loop(
                unbound,
                filler,
                bound_vector,
            )
            total_iterations += iters

            if cosine > best_cosine:
                best_cosine = cosine
                best_unbound = resonated

            if best_cosine >= self.invertibility_threshold:
                break

        return best_unbound, best_cosine, total_iterations

    def measure_invertibility(
        self,
        role_vector: Hypervector,
        filler_vector: Hypervector,
    ) -> float:
        bound = role_vector.bind(filler_vector)
        unbound, cosine, _ = self.unbind_with_resonance(bound, role_vector)

        rebind = role_vector.bind(unbound)
        invertibility = rebind.cosine_similarity(bound)

        return float(invertibility)

    def apply_sparsity(
        self,
        vector: Hypervector,
        ratio: Optional[float] = None,
    ) -> Hypervector:
        ratio = ratio or self.sparsity_ratio
        num_zeros = int(self.dimension * ratio)
        indices = np.random.choice(
            self.dimension, size=num_zeros, replace=False
        )
        sparse_vector = vector.vector.copy()
        sparse_vector[indices] = 0
        return Hypervector(sparse_vector, self.dimension).normalize()

    def compose_bindings(
        self,
        bindings: list[Tuple[str, str]],
    ) -> Hypervector:
        result = self.create_random_hypervector()

        for role_id, filler_id in bindings:
            role = self.encode_symbol(role_id)
            filler = self.encode_symbol(filler_id)
            binding = role.bind(filler)
            result = result.bundle(binding)

        return result.normalize()

    def decompose_structure(
        self,
        structure: Hypervector,
        role_id: str,
    ) -> Tuple[Hypervector, float, int]:
        role = self.encode_symbol(role_id)
        unbound, cosine, iters = self.unbind_with_resonance(
            structure,
            role,
        )
        return unbound, cosine, iters

    def clear_logs(self):
        self.iteration_log = []
