"""Shared helpers for minimization modules."""
from __future__ import annotations

from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from lab2_sem4.models import CoverageTable, Mask, MinimizationResult, MinimizationStage


def index_to_mask(index: int, variable_count: int) -> Mask:
    bits = format(index, f'0{variable_count}b')
    return tuple(int(bit) for bit in bits)


def combine_masks(left_mask: Mask, right_mask: Mask) -> Optional[Mask]:
    difference_count = 0
    result: List[Optional[int]] = []
    for left_bit, right_bit in zip(left_mask, right_mask):
        if left_bit == right_bit:
            result.append(left_bit)
            continue
        if left_bit is None or right_bit is None:
            return None
        difference_count += 1
        result.append(None)
    if difference_count == 1:
        return tuple(result)
    return None


def covers(mask: Mask, index: int, variable_count: int) -> bool:
    bits = format(index, f'0{variable_count}b')
    for mask_bit, bit_character in zip(mask, bits):
        if mask_bit is None:
            continue
        if mask_bit != int(bit_character):
            return False
    return True


def mask_to_dnf_term(mask: Mask, variables: Sequence[str]) -> str:
    literals = []
    for variable, bit in zip(variables, mask):
        if bit is None:
            continue
        literals.append(variable if bit == 1 else f'¬{variable}')
    return '(' + ' ∧ '.join(literals) + ')' if literals else '1'


def mask_to_cnf_clause(mask: Mask, variables: Sequence[str]) -> str:
    literals = []
    for variable, bit in zip(variables, mask):
        if bit is None:
            continue
        literals.append(variable if bit == 0 else f'¬{variable}')
    return '(' + ' ∨ '.join(literals) + ')' if literals else '0'


def _mask_sort_key(mask: Mask) -> Tuple[int, ...]:
    key = []
    for bit in mask:
        if bit is None:
            key.append(2)
        else:
            key.append(bit)
    return tuple(key)


class PrimeImplicantFinder:
    def build_stages(self, masks: Iterable[Mask]) -> Tuple[Tuple[Mask, ...], Tuple[MinimizationStage, ...]]:
        current_terms = tuple(sorted(set(masks), key=_mask_sort_key))
        stages: List[MinimizationStage] = []
        prime_implicants: Set[Mask] = set()
        while current_terms:
            combined_terms, used_terms, combination_descriptions = self._build_next_stage(current_terms)
            stages.append(
                MinimizationStage(
                    input_terms=current_terms,
                    combined_terms=tuple(sorted(combined_terms, key=_mask_sort_key)),
                    combinations=tuple(sorted(combination_descriptions)),
                )
            )
            for term in current_terms:
                if term not in used_terms:
                    prime_implicants.add(term)
            if not combined_terms:
                break
            current_terms = tuple(sorted(combined_terms, key=_mask_sort_key))
        return tuple(sorted(prime_implicants, key=_mask_sort_key)), tuple(stages)

    def _build_next_stage(self, current_terms: Tuple[Mask, ...]) -> Tuple[Set[Mask], Set[Mask], Set[str]]:
        combined_terms: Set[Mask] = set()
        used_terms: Set[Mask] = set()
        descriptions: Set[str] = set()
        for left_index, right_index in combinations(range(len(current_terms)), 2):
            left_term = current_terms[left_index]
            right_term = current_terms[right_index]
            combined = combine_masks(left_term, right_term)
            if combined is None:
                continue
            combined_terms.add(combined)
            used_terms.add(left_term)
            used_terms.add(right_term)
            descriptions.add(f'{left_term} + {right_term} -> {combined}')
        return combined_terms, used_terms, descriptions


class ExactCoverSelector:
    def select(
        self,
        prime_implicants: Sequence[Mask],
        covered_indices: Sequence[int],
        variables: Sequence[str],
    ) -> Tuple[Mask, ...]:
        variable_count = len(variables)
        coverage_map = {
            implicant: {index for index in covered_indices if covers(implicant, index, variable_count)}
            for implicant in prime_implicants
        }
        essential_implicants = self._find_essential(prime_implicants, covered_indices, coverage_map)
        already_covered = set().union(*(coverage_map[implicant] for implicant in essential_implicants)) if essential_implicants else set()
        remaining_indices = set(covered_indices) - already_covered
        if not remaining_indices:
            return tuple(sorted(essential_implicants, key=_mask_sort_key))
        remaining_implicants = [implicant for implicant in prime_implicants if implicant not in essential_implicants]
        best_choice = self._search_best_cover(remaining_implicants, remaining_indices, coverage_map)
        return tuple(sorted(set(essential_implicants) | set(best_choice), key=_mask_sort_key))

    @staticmethod
    def _find_essential(
        prime_implicants: Sequence[Mask],
        covered_indices: Sequence[int],
        coverage_map: Dict[Mask, Set[int]],
    ) -> List[Mask]:
        essential_implicants: List[Mask] = []
        for index in covered_indices:
            owners = [implicant for implicant in prime_implicants if index in coverage_map[implicant]]
            if len(owners) == 1 and owners[0] not in essential_implicants:
                essential_implicants.append(owners[0])
        return essential_implicants

    def _search_best_cover(
        self,
        implicants: Sequence[Mask],
        remaining_indices: Set[int],
        coverage_map: Dict[Mask, Set[int]],
    ) -> Tuple[Mask, ...]:
        best_solution: Tuple[Mask, ...] = tuple()
        best_cost = (float('inf'), float('inf'))
        for subset_size in range(1, len(implicants) + 1):
            for subset in combinations(implicants, subset_size):
                union = set().union(*(coverage_map[implicant] for implicant in subset))
                if not remaining_indices.issubset(union):
                    continue
                cost = (len(subset), self._literal_count(subset))
                if cost < best_cost:
                    best_cost = cost
                    best_solution = subset
            if best_solution:
                break
        return best_solution

    @staticmethod
    def _literal_count(implicants: Sequence[Mask]) -> int:
        return sum(sum(1 for bit in implicant if bit is not None) for implicant in implicants)


def build_coverage_table(
    implicants: Sequence[Mask],
    indices: Sequence[int],
    variables: Sequence[str],
    formatter,
) -> CoverageTable:
    variable_count = len(variables)
    headers = tuple(str(index) for index in indices)
    row_names = tuple(formatter(implicant, variables) for implicant in implicants)
    cells = []
    for implicant in implicants:
        row = tuple(covers(implicant, index, variable_count) for index in indices)
        cells.append(row)
    return CoverageTable(headers=headers, row_names=row_names, cells=tuple(cells))
