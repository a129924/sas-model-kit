"""SWAT-specific parameter mappers.

This module provides mappers for converting domain Parameter objects
to SWAT action-specific dictionary formats.

Mappers:
    - AstoreParameterToSwatDictMapper: Maps AstoreParameter to astore.score dict
    - ExplainParameterToSwatDictMapper: Maps ExplainParameter to explainModel.shapleyExplainer dict
    - DataStepParameterToSwatDictMapper: Maps DataStepParameter to datastep.runCode dict

Design:
    - Each mapper is stateless (only behavior, no state)
    - SWAT-specific details hidden from Parameter layer
    - Parameters stay pure (no knowledge of backends)
    - Mapper layer bridges domain and backend

Examples:
    >>> param = AstoreParameter(...)
    >>> mapper = AstoreParameterToSwatDictMapper()
    >>> swat_dict = mapper.map(param, where_condition="id=123")
"""

from __future__ import annotations

from typing import Any

from typing_extensions import override

from sas_model_kit.model.mapper.base import ParameterMapper
from sas_model_kit.parameter import (
    AstoreParameter,
    DataStepParameter,
    ExplainParameter,
)


class AstoreParameterToSwatDictMapper(ParameterMapper[AstoreParameter]):
    """Maps AstoreParameter to SWAT astore.score action dictionary.

        Converts domain AstoreParameter into SWAT's expected format for
        the astore.score action call.

        SWAT astore.score requires:
            - table: Input table specification
            - rstore: Model store specification
            - out: Output table specification (casout)
            - code: Optional DS2 code parameter

        Examples:
            >>> param = AstoreParameter(
            ...     input_caslib="public",
            ...     input_table="customers",
            ...     model_caslib="models",
            ...     model_table="my_astore",
            ...     score_code="dcl double x1-x5; ..."
            ... )
            >>> mapper = AstoreParameterToSwatDictMapper()
            >>> swat_dict = mapper.map(param)
            >>> # Returns:
            >>> # {
            >>> #     "table": {"name": "customers", "caslib": "public"},
            >>> #     "rstore": {"name": "my_astore", "caslib": "models"},
            >>> #     "out": {"name": "scored_data", "caslib": "public", "replace": True},
            >>> #     "code": "dcl double x1-x5; ..."
            >>> # }

    cas_result = conn.astore.score(
        table={"name": input_table, "caslib": input_caslib},
        rstore={"name": model_table, "caslib": model_caslib},
        casout={"name": output_table, "caslib": output_caslib},
        ds2code=content,
    )
    """

    @override
    def map(self, parameter: AstoreParameter, **context: Any) -> dict[str, Any]:
        """Map AstoreParameter to astore.score action dictionary.

        Args:
            parameter: AstoreParameter with input, model, and output spec
            **context: Runtime context (optional overrides)

        Returns:
            Dictionary suitable for session.astore.score(**dict)

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Validate parameter
        parameter.validate()

        # Build input table spec
        table_spec = {
            "name": parameter.input_table,
            "caslib": parameter.input_caslib,
        }

        # Build model store spec
        rstore_spec = {
            "name": parameter.model_table,
            "caslib": parameter.model_caslib,
        }

        # Build output spec (from parameter or context)
        # Use parameter.casout if provided, otherwise auto-generate
        if parameter.casout:
            out_spec = parameter.casout.copy()
        else:
            # Auto-generate from context or use defaults
            output_caslib = context.get("output_caslib", parameter.input_caslib)
            output_table = context.get(
                "output_table", f"{parameter.input_table}_scored"
            )
            out_spec = {
                "name": output_table,
                "caslib": output_caslib,
                "replace": True,
            }

        # Build action dictionary
        action_dict = {
            "table": table_spec,
            "rstore": rstore_spec,
            "out": out_spec,
            "code": parameter.score_code,
        }

        return action_dict


class ExplainParameterToSwatDictMapper(ParameterMapper[ExplainParameter]):
    """Maps ExplainParameter to SWAT explainModel.shapleyExplainer action dictionary.

        Converts domain ExplainParameter into SWAT's expected format for
        the explainModel.shapleyExplainer action call.

        Important:
            - SWAT explainModel.shapleyExplainer only handles ONE row at a time
            - where_condition MUST filter to exactly one observation
            - Caller is responsible for looping over multiple IDs

        SWAT explainModel.shapleyExplainer requires:
            - modelTableType: "ASTORE" or "DATASTEP"
            - id: ID column name
            - depth: Shapley calculation depth
            - trainTable: Training data for reference
            - code: Optional SAS score code

        Examples:
            >>> param = ExplainParameter(
            ...     train_caslib="public",
            ...     train_table="training",
            ...     predicted_target="churn",
            ...     features=["age", "income", "tenure"],
            ...     id_cols={"customer_id"},
            ...     depth=1,
            ...     model_caslib="models",
            ...     model_table="my_astore"
            ... )
            >>> mapper = ExplainParameterToSwatDictMapper()
            >>> swat_dict = mapper.map(
            ...     param,
            ...     where_condition="customer_id=123"
            ... )

    explan_model_result = conn.explainModel.shapleyExplainer(
        table={"caslib": train_caslib, "name": train_table_name},
        query={
            "name": output_table,
            "caslib": output_caslib,
            "where": '<where query>' # 我測過只能一筆一筆這樣打 超過一筆就會報錯
        },
        id=id_,         # ← SWAT 會保留這個欄位 # set[str]
        inputs=features, # list[str]
        modelTable={
            "name" : model_table,
            "caslib" : model_caslib,
        },
        modelTableType="<ASTORE | DataStep>",
        predictedTarget=predicted_target, # str
        code=sas_code,
        depth=1
    )
    """

    @override
    def map(self, parameter: ExplainParameter, **context: Any) -> dict[str, Any]:
        """Map ExplainParameter to explainModel.shapleyExplainer dictionary.

        Args:
            parameter: ExplainParameter with training, model spec, and explicit model_table_type
            **context: Runtime context (where_condition, output locations)

        Returns:
            Dictionary suitable for session.explainModel.shapleyExplainer(**dict)

        Raises:
            ValueError: If required parameters missing or invalid

        Note:
            - model_table_type must be explicitly provided (not inferred)
            - where_condition in context should filter to exactly one row
        """
        # Validate parameter
        parameter.validate()

        # Build training table spec
        train_table_spec = {
            "name": parameter.train_table,
            "caslib": parameter.train_caslib,
        }

        # Build base action dictionary
        # model_table_type is explicitly required in parameter
        model_type = parameter.model_table_type.value

        action_dict: dict[str, Any] = {
            "modelTableType": model_type,
            "id": ",".join(parameter.id_cols),  # Join multiple ID cols
            "depth": parameter.depth,
            "trainTable": train_table_spec,
            "target": parameter.predicted_target,
            "inputs": ",".join(parameter.features),  # Join feature names
        }

        # Add model spec based on type
        if model_type == "ASTORE":
            action_dict["modelTable"] = {
                "name": parameter.model_table,
                "caslib": parameter.model_caslib,
            }
        elif model_type == "DATASTEP":
            action_dict["code"] = parameter.sas_score_code

        # Add optional score data if provided
        if parameter.score_caslib and parameter.score_table:
            action_dict["scoreTable"] = {
                "name": parameter.score_table,
                "caslib": parameter.score_caslib,
            }

        # Add where condition if provided (filters to specific rows)
        if "where_condition" in context and context["where_condition"]:
            action_dict["where"] = context["where_condition"]

        # Add output spec if provided
        if "output_caslib" in context and "output_table" in context:
            action_dict["out"] = {
                "name": context["output_table"],
                "caslib": context["output_caslib"],
                "replace": True,
            }

        return action_dict


class DataStepParameterToSwatDictMapper(ParameterMapper[DataStepParameter]):
    """Maps DataStepParameter to SWAT datastep.runCode action dictionary.

    Converts domain DataStepParameter into SWAT's expected format for
    the datastep.runCode action call.

    SWAT datastep.runCode requires:
        - code: Complete SAS DATA step code

    The code should include all DATA/SET statements for input/output.

    Examples:
        >>> param = DataStepParameter(
        ...     score_code=\"\"\"
        ...         data public.processed;
        ...         set public.raw;
        ...         new_var = var1 * 2;
        ...         run;
        ...     \"\"\",
        ...     output_caslib="public",
        ...     output_table="processed"
        ... )
        >>> mapper = DataStepParameterToSwatDictMapper()
        >>> swat_dict = mapper.map(param)
        >>> # Returns:
        >>> # {
        >>> #     "code": "data public.processed; ...",
        >>> #     "single": True  # Execute on single node
        >>> # }

    cas_result = conn.datastep.runCode(
        code=score_code,
        single=True,  # Execute on single node
    )
    """

    @override
    def map(self, parameter: DataStepParameter, **context: Any) -> dict[str, Any]:
        """Map DataStepParameter to datastep.runCode action dictionary.

        Args:
            parameter: DataStepParameter with code and output location
            **context: Runtime context (optional, unused for DataStep)

        Returns:
            Dictionary suitable for session.datastep.runCode(**dict)

        Raises:
            ValueError: If code or output location is missing or invalid
        """
        # Validate parameter
        parameter.validate()

        # Build action dictionary
        action_dict: dict[str, Any] = {
            "code": parameter.score_code,
            "single": True,  # Execute on single thread/node
        }
        return action_dict
