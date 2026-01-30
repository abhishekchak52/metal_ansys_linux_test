---
name: pyEPR Ansys modernization
overview: Document the structure and interdependencies of the pyEPR Ansys COM interface (ansys_com.py), then refactor so that (1) PYEPR_USE_PYAEDT controls backend selection with COM as default, (2) ansys_com.py remains unchanged and is exposed when pyaedt is not used, and (3) the large ansys.py is replaced by an ansys/ subpackage containing pyaedt-only code split by class, with a single entry point that dispatches to either ansys_com or the subpackage.
todos:
  - id: discovery-doc
    content: Create ANSYS_INTERFACE_STRUCTURE.md at project root from ansys_com.py (structure, API, hierarchy, coupling, line ranges)
    status: completed
  - id: backend-env
    content: "Implement PYEPR_USE_PYAEDT handling: default = COM; when set truthy = pyaedt"
    status: completed
  - id: ansys-package-init
    content: Add ansys/ package with __init__.py that dispatches to ansys_com or pyaedt subpackage and re-exports public API
    status: completed
  - id: pyaedt-units-wrapper
    content: Add ansys/_units.py and ansys/_wrapper.py (pyaedt-only units and wrapper/release)
    status: completed
  - id: pyaedt-backend
    content: Add ansys/_backend.py for backend detection and get/set_backend, using_pyaedt, using_com
    status: completed
  - id: pyaedt-app-desktop-project
    content: Add ansys/hfss_app.py, hfss_desktop.py, hfss_project.py (pyaedt-only)
    status: completed
  - id: pyaedt-reporter-design
    content: Add ansys/_reporter.py and ansys/hfss_design.py (pyaedt-only)
    status: completed
  - id: pyaedt-setup-solutions
    content: Add ansys/hfss_setup.py and ansys/hfss_design_solutions.py, hfss_frequency_sweep.py (pyaedt-only)
    status: completed
  - id: pyaedt-report-optimetrics
    content: Add ansys/hfss_report.py and ansys/optimetrics.py (pyaedt-only)
    status: completed
  - id: pyaedt-modeler-entity
    content: Add ansys/hfss_modeler.py and ansys/model_entity.py (pyaedt-only)
    status: completed
  - id: pyaedt-fields-load
    content: Add ansys/hfss_fields_calc.py and ansys/load.py (pyaedt-only)
    status: completed
  - id: remove-ansys-py
    content: Remove packages/pyEPR/pyEPR/ansys.py after ansys/ package is complete and __init__.py re-exports correctly
    status: completed
  - id: validate
    content: Run tests and optionally tutorials; verify PYEPR_USE_PYAEDT unset -> COM, set -> pyaedt
    status: completed
isProject: false
---

# pyEPR Ansys interface modernization plan

## Current state

- **[packages/pyEPR/pyEPR/ansys_com.py](packages/pyEPR/pyEPR/ansys_com.py)** (~3748 lines): COM-only implementation. Same public API (classes and functions). **Not imported** by ansys.py today; it is a standalone reference implementation. Must remain **unchanged** and be the source of truth when `PYEPR_USE_PYAEDT` is unset.
- **[packages/pyEPR/pyEPR/ansys.py](packages/pyEPR/pyEPR/ansys.py)** (~5063 lines): Current facade. Contains backend selection, shared utilities, and **all** HFSS/Q3D classes with **dual-backend branching** (`if using_pyaedt()` / `elif using_com()`) inside each class. Does not read `PYEPR_USE_PYAEDT`; auto-selects pyaedt if available, else COM.
- **Consumers**: [packages/pyEPR/pyEPR/**init**.py](packages/pyEPR/pyEPR/__init__.py) (`from . import ansys`, `from .ansys import parse_units, parse_units_user, parse_entry`), [project_info.py](packages/pyEPR/pyEPR/project_info.py) (`ansys.load_ansys_project`, `ansys.release`), [core_quantum_analysis.py](packages/pyEPR/pyEPR/core_quantum_analysis.py) (`ureg`), [core_distributed_analysis.py](packages/pyEPR/pyEPR/core_distributed_analysis.py) (`CalcObject`, `ConstantVecCalcObject`, `set_property`, `ureg`).

---

## Phase 0: Discovery document (ANSYS_INTERFACE_STRUCTURE.md)

Create a single markdown document at the **project root**: `ANSYS_INTERFACE_STRUCTURE.md`. It should accurately and efficiently describe the structure and coupling of **ansys_com.py** (and how it relates to the current ansys.py facade). Suggested content:

### 0.1 File inventory and roles

- **ansys_com.py** (~3748 lines): COM-only implementation. Same class/function names as the public `pyEPR.ansys` API. Windows-only (win32com). Not modified by this refactor.
- **ansys.py** (current ~5063 lines): Facade with dual-backend logic. To be replaced by: (1) backend dispatch, (2) ansys/ subpackage with pyaedt-only code.

### 0.2 Public API surface (must remain importable from `pyEPR.ansys`)

- **Constants:** `BASIS_ORDER`, `LENGTH_UNIT`, `LENGTH_UNIT_ASSUMED`, `ureg`, `Q`
- **Unit/expr helpers:** `simplify_arith_expr`, `increment_name`, `extract_value_unit`, `extract_value_dim`, `parse_entry`, `fix_units`, `parse_units`, `unparse_units`, `parse_units_user`, `VariableString`, `var`
- **Property helpers:** `make_str_prop`, `make_int_prop`, `make_float_prop`, `make_prop`, `set_property`
- **Base/release:** `COMWrapper`, `HfssPropertyObject`, `_add_release_fn`, `release` (and for pyaedt path only: `_unwrap_aedt_handle`)
- **Backend (after Phase 1):** `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com`
- **App hierarchy:** `HfssApp`, `HfssDesktop`, `HfssProject`, `HfssDesign`
- **Setup hierarchy:** `HfssSetup`, `HfssDMSetup`, `HfssDTSetup`, `HfssEMSetup`, `AnsysQ3DSetup`
- **Solutions/reports:** `HfssDesignSolutions`, `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions`, `HfssFrequencySweep`, `HfssReport`, `Optimetrics`
- **Modeler/geometry:** `HfssModeler`, `ModelEntity`, `Box`, `Rect`, `Polyline`, `OpenPolyline`
- **Fields/calc:** `HfssFieldsCalc`, `CalcObject`, `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject`
- **Standalone:** `get_active_project`, `get_active_design`, `get_report_arrays`, `load_ansys_project`
- **Internal (pyaedt path):** `_ReporterWrapper` (used by HfssDesign)

### 0.3 Class hierarchy and coupling (from ansys_com.py)

**Inheritance (summary):**

- `COMWrapper` → `HfssApp`, `HfssDesktop`, `HfssProject`, `HfssDesign`, `HfssDesignSolutions`, `HfssFrequencySweep`, `HfssReport`, `Optimetrics`, `HfssModeler`, `HfssFieldsCalc`, `CalcObject`
- `HfssPropertyObject(COMWrapper)` → `HfssSetup` → `HfssDMSetup`, `HfssEMSetup`, `AnsysQ3DSetup`; `HfssDMSetup` → `HfssDTSetup`
- `HfssDesignSolutions` → `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions`
- `CalcObject` → `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject`
- `ModelEntity(str, HfssPropertyObject)` → `Box`, `Rect`, `Polyline`, `OpenPolyline`

**Key coupling (who returns/uses whom):**

- `HfssApp.get_app_desktop()` → `HfssDesktop`
- `HfssDesktop.get_active_project()`, `open_project()`, `new_project()` → `HfssProject`
- `HfssProject.get_designs()`, `get_design()` → `HfssDesign`
- `HfssDesign`: holds `HfssModeler`, `Optimetrics`; `get_setup()` → `HfssEMSetup` / `HfssDMSetup` / `HfssDTSetup` / `AnsysQ3DSetup`; uses `HfssDesignSolutions`, `HfssReport`, `HfssFrequencySweep`
- `HfssSetup.insert_sweep()` → `HfssFrequencySweep`; setup types use design solutions
- `HfssModeler` creates/returns `ModelEntity` subclasses (`Box`, `Rect`, `Polyline`, etc.)
- `HfssFieldsCalc` and `CalcObject` hierarchy used by design for field calculations
- Standalone functions: `get_active_project()` → `HfssApp` → `HfssDesktop` → `HfssProject`; `get_active_design()` → project; `get_report_arrays()` → `HfssDesign`, `HfssReport`; `load_ansys_project()` → app, desktop, project

Include in the doc a **concise** class/function list with approximate line ranges in ansys_com.py (e.g. HfssDesign 627–1122, HfssSetup 1123–1453, …) so the split order for the pyaedt subpackage is clear.

---

## Phase 1: Backend selection via `PYEPR_USE_PYAEDT`

- **Goal:** Backend is chosen by environment variable `PYEPR_USE_PYAEDT` when set; **default (unset) = COM** (expose ansys_com). When set to a truthy value (e.g. `1`, `true`, `yes`), use pyaedt if available.
- **Behavior:**
  - `PYEPR_USE_PYAEDT` unset or not present → use COM backend → `pyEPR.ansys` exposes members from **ansys_com** (desired default).
  - `PYEPR_USE_PYAEDT` set to truthy → use pyaedt backend if available → `pyEPR.ansys` exposes members from the new **ansys/** subpackage (pyaedt-only).
  - Optional: support falsy value (e.g. `0`, `false`, `no`) to force COM when both are available.
- **No change** to ansys_com.py. Logic lives in the new entry point (see Phase 3).

---

## Phase 2: Retain COM code as-is

- **Goal:** Leave [packages/pyEPR/pyEPR/ansys_com.py](packages/pyEPR/pyEPR/ansys_com.py) **completely untouched**. It remains the COM-only implementation and is the module whose members are re-exported by `pyEPR.ansys` when `PYEPR_USE_PYAEDT` is unset.

---

## Phase 3: Replace ansys.py with ansys/ package and pyaedt-only subpackage

### 3.1 Entry-point layout

- **Remove** the current single file `packages/pyEPR/pyEPR/ansys.py`.
- **Add** directory `packages/pyEPR/pyEPR/ansys/` (Python package).
- `**ansys/__init__.py**` (single entry point):
  - Read `PYEPR_USE_PYAEDT` (and optionally `get_backend` / `set_backend` for runtime override).
  - If backend is COM (default when env unset): import all public symbols from `..ansys_com` and re-export them (so `from pyEPR.ansys import HfssDesktop`, `load_ansys_project`, `parse_units`, etc. work unchanged). Optionally expose `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com` as stubs or thin wrappers (e.g. `using_pyaedt()` → False, `using_com()` → True).
  - If backend is pyaedt: import and re-export from the pyaedt submodules (see 3.2). No dual-backend branching inside the subpackage—only pyaedt code.

This preserves: `from pyEPR import ansys`, `from pyEPR.ansys import parse_units, parse_units_user, parse_entry`, `ansys.load_ansys_project`, `ansys.release`, and all class references used by project_info and core modules.

### 3.2 ansys/ subpackage contents (pyaedt-only)

The subpackage contains **only** the pyaedt implementation. Each module corresponds to one class (or a small, cohesive group). Extract the **pyaedt branches** from the current ansys.py; do not carry over COM branches or `using_com()` / `using_pyaedt()` conditionals inside these modules.

Suggested layout:


| Module                     | Contents                                                                                                                                                                                                                                                             |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_backend.py`              | Backend detection, `_BACKEND`, `_auto_select_backend`, `_PYAEDT_AVAILABLE`, `_COM_AVAILABLE`; `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com` (used only when pyaedt path is active from `__init__.py`)                          |
| `_units.py`                | Constants (`BASIS_ORDER`, `LENGTH_UNIT`, `LENGTH_UNIT_ASSUMED`), `ureg`, `Q`; unit/expr helpers: `simplify_arith_expr`, `increment_name`, `extract_value_*`, `parse_entry`, `fix_units`, `parse_units`, `unparse_units`, `parse_units_user`, `VariableString`, `var` |
| `_wrapper.py`              | `COMWrapper`, `HfssPropertyObject`, `_unwrap_aedt_handle`, `make_*_prop`, `set_property`, `_add_release_fn`, `release` (pyaedt-aware release)                                                                                                                        |
| `hfss_app.py`              | `HfssApp` (pyaedt)                                                                                                                                                                                                                                                   |
| `hfss_desktop.py`          | `HfssDesktop` (pyaedt)                                                                                                                                                                                                                                               |
| `hfss_project.py`          | `HfssProject` (pyaedt)                                                                                                                                                                                                                                               |
| `_reporter.py`             | `_ReporterWrapper`                                                                                                                                                                                                                                                   |
| `hfss_design.py`           | `HfssDesign` (pyaedt; uses _ReporterWrapper)                                                                                                                                                                                                                         |
| `hfss_setup.py`            | `HfssSetup`, `HfssDMSetup`, `HfssDTSetup`, `HfssEMSetup`, `AnsysQ3DSetup`                                                                                                                                                                                            |
| `hfss_design_solutions.py` | `HfssDesignSolutions`, `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions`                                                                                                                                           |
| `hfss_frequency_sweep.py`  | `HfssFrequencySweep`                                                                                                                                                                                                                                                 |
| `hfss_report.py`           | `HfssReport`                                                                                                                                                                                                                                                         |
| `optimetrics.py`           | `Optimetrics`                                                                                                                                                                                                                                                        |
| `hfss_modeler.py`          | `HfssModeler`                                                                                                                                                                                                                                                        |
| `model_entity.py`          | `ModelEntity`, `Box`, `Rect`, `Polyline`, `OpenPolyline`                                                                                                                                                                                                             |
| `hfss_fields_calc.py`      | `HfssFieldsCalc`, `CalcObject`, `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject`                                                                                                                                                                     |
| `load.py`                  | `get_active_project`, `get_active_design`, `get_report_arrays`, `load_ansys_project`                                                                                                                                                                                 |


Import order in `ansys/__init__.py` when pyaedt is active: `_backend` → `_units` → `_wrapper` → app → desktop → project → _reporter → setup, design_solutions, frequency_sweep, report, optimetrics, modeler, model_entity, fields_calc → design → load. Avoid circular imports (e.g. design imports setup, solutions, modeler, report; load imports app, desktop, project).

### 3.3 Compatibility

- **Public entry point:** `pyEPR.ansys` is the package `ansys/`. No `ansys.py` file. All existing imports (`from pyEPR.ansys import ...`, `ansys.load_ansys_project`, etc.) continue to work.
- **Tests and tutorials:** No change to import paths; only internal layout and backend dispatch change.

---

## Phase 4: Validation

- Run existing pyEPR tests (e.g. under [packages/pyEPR/tests/](packages/pyEPR/tests/) if present).
- Optionally run tutorial notebooks to confirm `pyEPR.ansys` and `load_ansys_project` work.
- Confirm: `PYEPR_USE_PYAEDT` unset (or falsy) → COM backend → members from ansys_com; `PYEPR_USE_PYAEDT=1` (or truthy) → pyaedt backend → members from ansys/ subpackage.

---

## Summary

1. **Deliverable:** Create [ANSYS_INTERFACE_STRUCTURE.md](ANSYS_INTERFACE_STRUCTURE.md) at project root with the structure and coupling of ansys_com.py (and relation to current ansys.py) as in Phase 0.
2. **Backend:** Use `PYEPR_USE_PYAEDT` for selection; **default = COM** (expose ansys_com); leave ansys_com.py unchanged.
3. **Split:** Replace monolithic ansys.py with package `ansys/` whose `__init__.py` dispatches to either ansys_com (COM) or internal pyaedt-only modules (one module per class or logical group), with full re-export for drop-in compatibility.

