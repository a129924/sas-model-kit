"""ShapleyValuesTransformer

Transforms Shapley values from long format SASDataFrame into a single-row
wide format pandas DataFrame and appends an ID column for alignment.

SRP: Single transformation responsibility.
"""

from __future__ import annotations

from typing import Any

from swat.dataframe import SASDataFrame


class ShapleyValuesTransformer:
    """Transform Shapley SASDataFrame to wide SASDataFrame with ID.

    Input columns expected:
        - "Variable"
        - "ShapleyValue"
    """

    def __init__(self, id_column: str = "id") -> None:
        """Initialize transformer with ID column name.

        Args:
            id_column: Name of the ID column to add
        """
        self.id_column = id_column

    def transform(self, data: SASDataFrame, *, id_value: Any) -> SASDataFrame:
        wide = data.set_index("Variable").T
        wide[self.id_column] = id_value
        return wide
