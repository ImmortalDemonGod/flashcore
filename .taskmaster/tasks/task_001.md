# Task ID: 1

**Title:** Spoke Initialization & Structural Alignment

**Status:** pending

**Dependencies:** None

**Priority:** medium

**Description:** Align the existing boilerplate structure with setup.py requirements and define strict dependency constraints.

**Details:**

The directory 'flashcore-lib' already exists but must be renamed to 'flashcore' to match setup.py expectations (line 34: version=read('flashcore', 'VERSION')). Update requirements.txt to exclude torch/fsrs-optimizer and include only lightweight runtime dependencies: fsrs>=3.0.0, duckdb>=1.0.0, pydantic>=2.7.0, typer>=0.12.0, rich>=13.0.0, ruamel.yaml>=0.17.0. This enforces the 'Nuclear Reactor' fix from PRD Section 2.A.

**Test Strategy:**

Verify the repository structure and ensure all dependencies are correctly listed in pyproject.toml.

## Subtasks

### 1.1. Rename Package Directory

**Status:** pending  
**Dependencies:** None  

Rename 'flashcore-lib' to 'flashcore' to match setup.py package name.

**Details:**

Execute: mv flashcore-lib flashcore. This fixes the mismatch where setup.py expects 'flashcore' (line 34) but the directory is named 'flashcore-lib'. CRITICAL: The template contains flashcore/cli.py, but the migrated implementation will use a flashcore/cli/ package. Remove or rename flashcore/cli.py after the move to avoid Python import collisions (module vs package).

### 1.2. Enforce Dependency Constraints (Nuclear Reactor Fix)

**Status:** pending  
**Dependencies:** 1.1  

Update requirements.txt to exclude heavy ML dependencies and include only lightweight runtime deps.

**Details:**

Edit requirements.txt to contain ONLY: duckdb>=1.0.0, pydantic>=2.7.0, fsrs>=3.0.0 (NOT fsrs-optimizer), typer>=0.12.0, rich>=13.0.0, ruamel.yaml>=0.17.0, PyYAML>=6.0.0, bleach>=6.0.0. CRITICAL: Exclude torch, transformers, fsrs-optimizer per PRD Section 2.A. NOTE: PyYAML and bleach are required by the legacy YAML processing subsystem being ported (yaml_processor.py/yaml_models.py).

### 1.3. Establish Modern Build System and Deprecate Legacy Setup

**Status:** pending  
**Dependencies:** 1.2  

Create pyproject.toml as single source of truth and deprecate setup.py.

**Details:**

Create pyproject.toml with [project] name='flashcore', version from VERSION file, requires-python='>=3.10', and dependencies matching requirements.txt. Add [build-system] using setuptools. CRITICAL: After creating pyproject.toml, rename setup.py to setup.py.bak or remove it entirely to prevent build tool confusion. Modern Python packaging (PEP 517/518) uses pyproject.toml as the single source of truth. Having both files creates ambiguity about which defines dependencies and metadata.

### 1.4. Verify No Heavy Dependencies in Tree

**Status:** pending  
**Dependencies:** 1.3  

Audit the full dependency tree to ensure no transitive heavy dependencies.

**Details:**

Run 'pip install -e .' then 'pip list' and verify total install size <50MB. Use 'pipdeptree' to check for torch/transformers in transitive deps.

### 1.5. Create .gitignore for Python Package

**Status:** pending  
**Dependencies:** 1.4  

Add .gitignore to exclude build artifacts and virtual environments.

**Details:**

Create .gitignore with: __pycache__/, *.pyc, *.pyo, *.egg-info/, dist/, build/, .venv/, .pytest_cache/, .coverage.
