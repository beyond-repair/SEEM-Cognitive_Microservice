import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Hypervector:
    vector: np.ndarray
    dimension: int = 16384
    dtype: str = "complex128"

    def __post_init__(self):
        self.vector = np.asarray(self.vector, dtype=np.complex128)
        if self.vector.size == 0:
            self.vector = np.zeros(self.dimension, dtype=np.complex128)
        if len(self.vector.shape) > 1:
            self.vector = self.vector.flatten()
        if self.vector.size != self.dimension:
            self.dimension = int(self.vector.size)

    def copy(self) -> "Hypervector":
        return Hypervector(np.array(self.vector, copy=True), self.dimension)

    def normalize(self) -> "Hypervector":
        """Project each nonzero component onto the unit circle (FHRR phasor).

        Exact zeros stay zero. ``np.angle(0)`` is 0, so do not turn zeros into
        ``1+0j`` — that would invent a shared phase and inflate similarity.
        """
        mag = np.abs(self.vector)
        phasor = np.zeros(self.dimension, dtype=np.complex128)
        nz = mag > 1e-15
        phasor[nz] = self.vector[nz] / mag[nz]
        return Hypervector(phasor, self.dimension)

    def cosine_similarity(self, other: "Hypervector") -> float:
        """Mean real alignment of phasors. Identical full phasors score 1."""
        prod = self.vector * np.conj(other.vector)
        return float(np.real(np.mean(prod)))

    def bind(self, other: "Hypervector") -> "Hypervector":
        """Element-wise FHRR bind: self ⊙ other."""
        return Hypervector(self.vector * other.vector, self.dimension).normalize()

    def unbind(self, bound: "Hypervector") -> "Hypervector":
        """Recover the other factor from ``bound = self ⊙ other`` via conj(self)."""
        return Hypervector(bound.vector * np.conj(self.vector), self.dimension).normalize()

    def bundle(self, other: "Hypervector") -> "Hypervector":
        return Hypervector(self.vector + other.vector, self.dimension).normalize()


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
        theta = np.random.uniform(0.0, 2.0 * np.pi, self.dimension)
        vector = np.exp(1j * theta)
        return Hypervector(vector, self.dimension).normalize()

    def encode_symbol(self, symbol_id: str) -> Hypervector:
        if symbol_id in self.symbol_codebook:
            return self.symbol_codebook[symbol_id]
        hv = self.create_random_hypervector()
        self.symbol_codebook[symbol_id] = hv
        return hv

    def bind_symbols(self, symbol1_id: str, symbol2_id: str) -> Hypervector:
        hv1 = self.encode_symbol(symbol1_id)
        hv2 = self.encode_symbol(symbol2_id)
        return hv1.bind(hv2)

    def cleanup(self, vector: Hypervector) -> Tuple[Optional[str], Hypervector, float]:
        """Nearest codebook phasor. Returns (None, vector, 0) if the book is empty."""
        if not self.symbol_codebook:
            return None, vector, 0.0
        best_id: Optional[str] = None
        best_hv = vector
        best_c = -2.0
        for sid, hv in self.symbol_codebook.items():
            c = vector.cosine_similarity(hv)
            if c > best_c:
                best_id = sid
                best_hv = hv
                best_c = c
        return best_id, best_hv, float(best_c)

    def resonator_loop(
        self,
        query: Hypervector,
        context: Hypervector,
        target: Hypervector,
    ) -> Tuple[Hypervector, float, int]:
        """Unbind ``context`` from ``query``, then snap to the codebook.

        Cosine is the cleaned vector against ``target``. This does not walk
        random noise toward the target. One stable codebook snap ends the loop.
        """
        current = context.unbind(query)
        best_cosine = current.cosine_similarity(target)
        best_result = current
        iterations = 0

        for i in range(self.max_iterations):
            iterations = i + 1
            sid, cleaned, clean_cos = self.cleanup(current)
            candidate = cleaned if sid is not None else current
            cosine_sim = candidate.cosine_similarity(target)

            if cosine_sim > best_cosine:
                best_cosine = cosine_sim
                best_result = candidate

            self.iteration_log.append({
                "iteration": i,
                "cosine_similarity": float(cosine_sim),
                "norm": float(np.linalg.norm(candidate.vector)),
                "cleanup_id": sid,
                "cleanup_cosine": float(clean_cos),
            })

            current = candidate
            if best_cosine >= self.invertibility_threshold or sid is not None:
                break

        return best_result, float(best_cosine), iterations

    def unbind_with_resonance(
        self,
        bound_vector: Hypervector,
        key: Hypervector,
        max_attempts: int = 3,
    ) -> Tuple[Hypervector, float, int]:
        """Algebraic unbind, then at most one codebook snap.

        ``max_attempts`` is retained for callers; the phasor unbind does not
        improve by repeating itself. Cosine is alignment with the nearest
        codebook item, or 0 when the book is empty.
        """
        del max_attempts
        unbound = key.unbind(bound_vector)
        sid, cleaned, clean_cos = self.cleanup(unbound)
        if sid is None:
            return unbound, 0.0, 1
        return cleaned, float(clean_cos), 1

    def measure_invertibility(
        self,
        role_vector: Hypervector,
        filler_vector: Hypervector,
    ) -> float:
        """Algebraic FHRR invertibility: unbind(bind(role, filler), role) vs filler.

        No resonator and no planted score. For unit phasors this is ~1.
        """
        bound = role_vector.bind(filler_vector)
        recovered = role_vector.unbind(bound)
        return float(recovered.cosine_similarity(filler_vector))

    def apply_sparsity(
        self,
        vector: Hypervector,
        ratio: Optional[float] = None,
    ) -> Hypervector:
        """Zero a fraction of components. Zeros are kept (not refilled)."""
        ratio = self.sparsity_ratio if ratio is None else ratio
        num_zeros = int(self.dimension * ratio)
        sparse_vector = vector.vector.copy()
        if num_zeros > 0:
            indices = np.random.choice(self.dimension, size=num_zeros, replace=False)
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
            result = result.bundle(role.bind(filler))
        return result.normalize()

    def decompose_structure(
        self,
        structure: Hypervector,
        role_id: str,
    ) -> Tuple[Hypervector, float, int]:
        role = self.encode_symbol(role_id)
        return self.unbind_with_resonance(structure, role)

    def clear_logs(self):
        self.iteration_log = []
