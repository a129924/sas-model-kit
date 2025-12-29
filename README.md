# SAS Model Kit

Python package for SAS Viya Analytics Models.

## Overview

SAS Model Kit provides a clean, Pythonic API for working with SAS Viya analytics models:
- ASTORE (Analytical Store) models
- Explainable AI models
- Data Step models

## Features (Phase 1)

- **Connection Management**: SessionProtocol-based connection handling
- **Operation Adapter**: Unified action execution across backends (SWAT, SASCTL, HTTPx)
- **DataSource**: PyTorch-style data handling with prepare() and fetch_result()

## Installation

```bash
# Install from source
uv pip install .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Quick Start

```python
from sas_model_kit.connection.swat import SWATConnection
from sas_model_kit.datasource import DataFrameDataSource
import pandas as pd

# Connect to CAS
with SWATConnection('hostname', 5570, username='user', password='pass') as conn:
    # Get operation adapter
    operation = conn.get_operation()
    
    # Prepare data
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    datasource = DataFrameDataSource(df, caslib='public', table='input_data')
    datasource.prepare(operation)
    
    # Execute model (coming in Block 4)
    # result = model.predict(datasource, operation)
```

## Development

### Setup

```bash
# Clone repository
git clone <repository-url>
cd sas-model-kit

# Install dependencies
uv sync

# Run tests
uv run pytest
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sas_model_kit --cov-report=html

# Run specific test file
uv run pytest tests/test_connection/test_swat_connection.py
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type check
uv run mypy src
```

## Architecture

### Design Principles

- **Protocol (SRP)**: Protocols follow Single Responsibility Principle
- **ABC (CSRP)**: Abstract classes follow Concrete Single Responsibility Principle
- **Explicit Inheritance**: All implementations explicitly inherit from Protocol/ABC
- **@override Decorator**: All implementations use @typing_extensions.override

### Layer Structure

1. **Connection Layer**: SessionProtocol for connection lifecycle
2. **Operation Layer**: OperationProtocol for action execution (Adapter Pattern)
3. **DataSource Layer**: DataSourceProtocol for data handling (PyTorch-style)
4. **Model Layer**: Model classes for analytics workflows (Phase 1 focus)

## License

TBD

## Contributing

TBD
