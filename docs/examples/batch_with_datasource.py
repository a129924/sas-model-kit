"""Example: Using BatchExplainProcessor with DataSource.

This example demonstrates Phase 1 DataSource integration pattern:
manually combining DataSource + Processor for batch Shapley explanation.

Pattern:
    1. Prepare input data via DataSource
    2. Execute batch processing
    3. Fetch results via DataSource

Prerequisites:
    - Active SWAT connection
    - Training data uploaded to CAS
    - ASTORE model available
"""

from __future__ import annotations

import pandas as pd
from swat import CAS

from sas_model_kit.connection.swat import SWATConnection
from sas_model_kit.datasource import CASTableDataSource, DataFrameDataSource
from sas_model_kit.model.types import ModelTableType
from sas_model_kit.operation.swat import SWATOperationAdapter
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.processor.swat import BatchExplainProcessor


def main() -> None:
    """Demonstrate batch explain with DataSource integration."""
    # Step 1: Connect to CAS
    with SWATConnection(
        "hostname", 5570, username="user", password="pass"
    ) as connection:
        session: CAS = connection.get_session()

        operation = SWATOperationAdapter(session)

        # Step 2: Prepare training data (DataFrame → DataSource → CAS)
        training_df = pd.DataFrame(
            {
                "customer_id": ["C001", "C002", "C003"],
                "age": [25, 35, 45],
                "income": [50000, 60000, 70000],
                "credit_score": [650, 700, 750],
                "prediction": [0.2, 0.5, 0.8],
            }
        )

        input_ds = DataFrameDataSource(
            data=training_df, caslib="public", table="training_data"
        )

        # Upload to CAS via DataSource
        input_ds.prepare(operation)
        print("✓ Training data uploaded to CAS: public.training_data")

        # Step 3: Configure Explain parameters
        explain_param = ExplainParameter(
            train_caslib="public",
            train_table="training_data",
            predicted_target="prediction",
            features=["age", "income", "credit_score"],
            id_cols={"customer_id"},
            depth=1,
            model_table_type=ModelTableType.ASTORE,
            model_caslib="models",
            model_table="my_astore_model",
            sas_score_code="",
        )

        # Step 4: Create processor and execute batch
        processor = BatchExplainProcessor(
            parameter=explain_param, operation=operation, id_column="customer_id"
        )

        result = processor.process_batch(
            ids=["C001", "C002", "C003"],
            id_column="customer_id",
            batch_caslib="public",
            output_table="shapley_results",
        )

        # Step 5: Handle result
        if result.is_ok:
            final_table = result.unwrap()
            print(
                f"✓ Batch processing succeeded: {final_table.caslib}.{final_table.name}"
            )

            # Step 6: Fetch results via DataSource (CAS → DataFrame)
            output_ds = CASTableDataSource(
                caslib=final_table.caslib,  # type: ignore
                table=final_table.name,  # type: ignore
            )
            results_df = output_ds.fetch_result(
                operation,
                caslib=final_table.caslib,  # type: ignore
                table=final_table.name,  # type: ignore
            )

            print("\n📊 Shapley Results:")
            print(results_df.head(5))

            # Optional: Analysis
            print("\n📈 Top influential features:")
            for customer_id in results_df["customer_id"].unique():
                customer_data = results_df[results_df["customer_id"] == customer_id]
                top_feature = customer_data.nlargest(1, "ShapleyValue")
                print(
                    f"  {customer_id}: {top_feature['Variable'].values[0]} "
                    f"(Shapley={top_feature['ShapleyValue'].values[0]:.4f})"
                )

        else:
            error = result.unwrap_err()
            print(f"✗ Batch processing failed: {error.message}")
            if error.errors:
                print(f"  Errors: {len(error.errors)} IDs failed")
                for err in error.errors[:3]:  # Show first 3
                    print(f"    - ID {err['id']}: {err['message']}")
            if error.partial_output:
                print(
                    f"  Partial results available: {error.partial_output.caslib}.{error.partial_output.name}"
                )

        # Cleanup
        print("\n✓ Session closed")


if __name__ == "__main__":
    main()
