# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-01-13

### 🎯 Major Achievements

#### Result Pattern Implementation
- **DataSourceProtocol**: All methods return `Result[T, E]`
  - `prepare()`: `None` → `Result[None, UploadFailure]`
  - `fetch_result()`: `T` → `Result[T, DataFetchFailure]`
- **OperationProtocol**: All methods return `Result[T, E]`
  - `call_action()`: `Any` → `Result[Any, OperationError]`
  - `upload_data()`: `T` → `Result[T, OperationError]`
  - `table_exists()`: `bool` → `Result[bool, OperationError]`
  - `model_exists()`: `bool` → `Result[bool, OperationError]`
- **TransformerProtocol**: All `execute()` return `Result[T, E]`
- Complete migration from exception-based to Result-based error handling

#### Pure Transform Principle
- Removed `InvalidColumnFailure` from Transformer layer
- Clear separation of concerns:
  - **Parameter layer**: Validates input
  - **DataSource layer**: Prepares data (uploads to CAS)
  - **Transformer layer**: Pure execution only (no validation)
  - **Model layer**: Catches exceptions → Result pattern
- Updated SyncModel documentation with Pure Transform guidelines

#### Result Combinators
- `and_then()`: Result-returning function chaining
- `map()`: Value transformation without error handling
- `map_err()`: Error type transformation
- `or_else()`: Error recovery pipeline

#### Error Hierarchy
- Added `TableNotFoundError` to Operation layer
- Unified error handling with `Result[T, E]` pattern
- Error context preservation across layer boundaries

### 💥 Breaking Changes

All protocol signatures changed to return `Result[T, E]`:

```python
# DataSourceProtocol
- def prepare(self, operation: OperationProtocol) -> None
+ def prepare(self, operation: OperationProtocol) -> Result[None, UploadFailure]

- def fetch_result(self, operation: OperationProtocol, caslib: str, table: str) -> ReSourceT
+ def fetch_result(self, operation: OperationProtocol, caslib: str, table: str) -> Result[ReSourceT, DataFetchFailure]

# OperationProtocol
- def call_action(self, action_name: str, **kwargs: Any) -> Any
+ def call_action(self, action_name: str, **kwargs: Any) -> Result[Any, OperationError]

- def upload_data(self, data: ReSourceType, caslib: str, table: str) -> ReturnType
+ def upload_data(self, data: ReSourceType, caslib: str, table: str) -> Result[ReturnType, OperationError]

- def table_exists(self, caslib: str, table: str) -> bool
+ def table_exists(self, caslib: str, table: str) -> Result[bool, OperationError]

# TransformerProtocol
- def execute(self, input_table: CASTable) -> CASTable
+ def execute(self, input_table: CASTable) -> Result[CASTable, TransformerError]
```

### 🐛 Bug Fixes
- Fixed match-case pattern for action_result handling in dataframe.py
- Restored proper error handling flow in DataSource implementations

### 📊 Statistics
- **414 tests** passing (100% success rate)
- **5 improvements** implemented in Phase 2
- **24 files** modified
- **0 test failures**

### 🔗 References
- Branch: `ai/phase-2-pure-transform-optimization`
- Commits: b05df11, 0c16524, eb2bd08, dd760c0, 26b1aea
- Merge: 6406ffb

---

## [0.2.0] - Previous Release

### Added
- Transformer Layer implementation
- Result Type refactoring
- Basic error hierarchy

---

## How to Upgrade

### From 0.2.0 to 0.3.0

1. **Update all DataSource implementations**:
   ```python
   # Before
   def prepare(self, operation):
       operation.upload_data(...)
   
   # After
   def prepare(self, operation) -> Result[None, UploadFailure]:
       return operation.upload_data(...).map(lambda _: None).map_err(...)
   ```

2. **Update Operation calls**:
   ```python
   # Before
   result = operation.call_action('astore.score', ...)
   
   # After
   action_result = operation.call_action('astore.score', ...)
   match action_result:
       case Ok(result):
           # Handle success
       case Err(error):
           # Handle error
   ```

3. **Update Transformer implementations**:
   ```python
   # Before
   def execute(self, input_table):
       # ... operations ...
       return output_table
   
   # After
   def execute(self, input_table) -> Result[CASTable, TransformerError]:
       # ... operations ...
       return Ok(output_table)
   ```

4. **Remove InvalidColumnFailure usage**:
   - Column validation should be done in Parameter layer, not Transformer layer
   - Use DuplicateKeyError or other semantic errors instead

---

[0.3.0]: https://github.com/a129924/sas-model-kit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/a129924/sas-model-kit/releases/tag/v0.2.0
