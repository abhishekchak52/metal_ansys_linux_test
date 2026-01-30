# Ansys interface structure (pyEPR)

**Document status:** Last updated to reflect refactor completed 2025; `ansys.py` removed, `ansys/` package and `PYEPR_USE_PYAEDT` dispatch in place.

This document describes the structure and coupling of the pyEPR Ansys interface, based on **ansys_com.py** (COM-only implementation). It documents the current state after refactor and serves as a starting point for the next phase.

## 1. File inventory and roles

| File | Approx. lines | Role |
|------|----------------|------|
| **packages/pyEPR/pyEPR/ansys_com.py** | ~3748 | COM-only implementation. Same class/function names as the public `pyEPR.ansys` API. Windows-only (win32com). **Not modified**; re-exported when `PYEPR_USE_PYAEDT` is unset. |
| **packages/pyEPR/pyEPR/ansys.py** | — | **Removed.** No longer exists. |
| **packages/pyEPR/pyEPR/ansys/** (package) | — | Single entry point. Dispatches to COM (`ansys_com`) or pyaedt submodules based on `PYEPR_USE_PYAEDT`. Default (unset) = COM; when set truthy = pyaedt if available. |

### 1.2 ansys/ package layout (pyaedt path)

| Module | Contents |
|--------|----------|
| `_backend.py` | Backend detection, `PYEPR_USE_PYAEDT` handling, `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com` |
| `_units.py` | Constants, `ureg`, `Q`, unit/expr helpers, `VariableString`, `var` |
| `_wrapper.py` | `COMWrapper`, `HfssPropertyObject`, `_unwrap_aedt_handle`, `make_*_prop`, `set_property`, `release`, `_add_release_fn` |
| `hfss_app.py` | `HfssApp` (pyaedt) |
| `hfss_desktop.py` | `HfssDesktop` |
| `hfss_project.py` | `HfssProject` |
| `_reporter.py` | `_ReporterWrapper` (ExportToFile gRPC compatibility) |
| `hfss_design.py` | `HfssDesign` |
| `hfss_setup.py` | `HfssSetup`, `HfssDMSetup`, `HfssDTSetup`, `HfssEMSetup`, `AnsysQ3DSetup` |
| `hfss_design_solutions.py` | `HfssDesignSolutions`, `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions` |
| `hfss_frequency_sweep.py` | `HfssFrequencySweep` |
| `hfss_report.py` | `HfssReport` |
| `optimetrics.py` | `Optimetrics` |
| `hfss_modeler.py` | `HfssModeler` |
| `model_entity.py` | `ModelEntity`, `Box`, `Rect`, `Polyline`, `OpenPolyline` |
| `hfss_fields_calc.py` | `HfssFieldsCalc`, `CalcObject`, `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject` |
| `load.py` | `get_active_project`, `get_active_design`, `get_report_arrays`, `load_ansys_project` |

### 1.3 Backend dispatch

- **Entry point:** [packages/pyEPR/pyEPR/ansys/__init__.py](packages/pyEPR/pyEPR/ansys/__init__.py) imports `_backend`; backend is resolved in `_backend` on import via `_resolve_backend_from_env()`.
- **If `get_backend() == "com"`:** Re-export all public names from `..ansys_com` and add backend API from `_backend` (so `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com` are available even when COM is selected).
- **Else:** Import and re-export from the pyaedt submodules listed in 1.2.
- **Important:** Backend is fixed at **first import** of `pyEPR.ansys`; `PYEPR_USE_PYAEDT` must be set before that import.

## 2. Public API surface (must remain importable from `pyEPR.ansys`)

- **Constants:** `BASIS_ORDER`, `LENGTH_UNIT`, `LENGTH_UNIT_ASSUMED`, `ureg`, `Q`
- **Unit/expr helpers:** `simplify_arith_expr`, `increment_name`, `extract_value_unit`, `extract_value_dim`, `parse_entry`, `fix_units`, `parse_units`, `unparse_units`, `parse_units_user`, `VariableString`, `var`
- **Property helpers:** `make_str_prop`, `make_int_prop`, `make_float_prop`, `make_prop`, `set_property`
- **Base/release:** `COMWrapper`, `HfssPropertyObject`, `_add_release_fn`, `release` (pyaedt path also has `_unwrap_aedt_handle`)
- **Backend (after refactor):** `get_available_backends`, `get_backend`, `set_backend`, `using_pyaedt`, `using_com`
- **App hierarchy:** `HfssApp`, `HfssDesktop`, `HfssProject`, `HfssDesign`
- **Setup hierarchy:** `HfssSetup`, `HfssDMSetup`, `HfssDTSetup`, `HfssEMSetup`, `AnsysQ3DSetup`
- **Solutions/reports:** `HfssDesignSolutions`, `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions`, `HfssFrequencySweep`, `HfssReport`, `Optimetrics`
- **Modeler/geometry:** `HfssModeler`, `ModelEntity`, `Box`, `Rect`, `Polyline`, `OpenPolyline`
- **Fields/calc:** `HfssFieldsCalc`, `CalcObject`, `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject`
- **Standalone:** `get_active_project`, `get_active_design`, `get_report_arrays`, `load_ansys_project`
- **Internal (pyaedt path):** `_ReporterWrapper` (used by HfssDesign)

## 3. Class hierarchy (ansys_com.py)

**Inheritance:**

- `COMWrapper` → `HfssApp`, `HfssDesktop`, `HfssProject`, `HfssDesign`, `HfssDesignSolutions`, `HfssFrequencySweep`, `HfssReport`, `Optimetrics`, `HfssModeler`, `HfssFieldsCalc`, `CalcObject`
- `HfssPropertyObject(COMWrapper)` → `HfssSetup` → `HfssDMSetup`, `HfssEMSetup`, `AnsysQ3DSetup`; `HfssDMSetup` → `HfssDTSetup`
- `HfssDesignSolutions` → `HfssEMDesignSolutions`, `HfssDMDesignSolutions`, `HfssDTDesignSolutions`, `HfssQ3DDesignSolutions`
- `CalcObject` → `NamedCalcObject`, `ConstantCalcObject`, `ConstantVecCalcObject`
- `ModelEntity(str, HfssPropertyObject)` → `Box`, `Rect`, `Polyline`, `OpenPolyline`

## 4. Coupling (who returns/uses whom)

- `HfssApp.get_app_desktop()` → `HfssDesktop`
- `HfssDesktop.get_active_project()`, `open_project()`, `new_project()` → `HfssProject`
- `HfssProject.get_designs()`, `get_design()` → `HfssDesign`
- `HfssDesign`: holds `HfssModeler`, `Optimetrics`; `get_setup()` → `HfssEMSetup` / `HfssDMSetup` / `HfssDTSetup` / `AnsysQ3DSetup`; uses `HfssDesignSolutions`, `HfssReport`, `HfssFrequencySweep`
- `HfssSetup.insert_sweep()` → `HfssFrequencySweep`; setup types use design solutions
- `HfssModeler` creates/returns `ModelEntity` subclasses (`Box`, `Rect`, `Polyline`, etc.)
- `HfssFieldsCalc` and `CalcObject` hierarchy used by design for field calculations
- Standalone: `get_active_project()` → `HfssApp` → `HfssDesktop` → `HfssProject`; `get_active_design()` → project; `get_report_arrays()` → `HfssDesign`, `HfssReport`; `load_ansys_project()` → app, desktop, project

## 5. ansys_com.py: class/function list with line ranges

| Lines | Symbol |
|-------|--------|
| 77–85 | `simplify_arith_expr` |
| 86–98 | `increment_name` |
| 99–113 | `extract_value_unit` |
| 114–120 | `extract_value_dim` |
| 121–135 | `parse_entry` |
| 136–157 | `fix_units` |
| 158–170 | `parse_units` |
| 171–182 | `unparse_units` |
| 183–190 | `parse_units_user` |
| 191–234 | `VariableString` |
| 235–243 | `var` |
| 244–251 | `_add_release_fn` |
| 252–268 | `release` |
| 269–278 | `COMWrapper` |
| 279–284 | `HfssPropertyObject` |
| 285–344 | `make_str_prop`, `make_int_prop`, `make_float_prop`, `make_prop`, `set_property` |
| 367–386 | `HfssApp` |
| 387–482 | `HfssDesktop` |
| 483–626 | `HfssProject` |
| 627–1122 | `HfssDesign` |
| 1123–1453 | `HfssSetup` |
| 1454–1505 | `HfssDMSetup` |
| 1506–1510 | `HfssDTSetup` |
| 1511–1523 | `HfssEMSetup` |
| 1524–1729 | `AnsysQ3DSetup` |
| 1730–1770 | `HfssDesignSolutions` |
| 1771–1934 | `HfssEMDesignSolutions` |
| 1935–1938 | `HfssDMDesignSolutions` |
| 1939–1942 | `HfssDTDesignSolutions` |
| 1943–1946 | `HfssQ3DDesignSolutions` |
| 1947–2037 | `HfssFrequencySweep` |
| 2038–2058 | `HfssReport` |
| 2059–2302 | `Optimetrics` |
| 2303–3132 | `HfssModeler` |
| 3133–3163 | `ModelEntity` |
| 3164–3189 | `Box` |
| 3190–3228 | `Rect` |
| 3229–3312 | `Polyline` |
| 3313–3377 | `OpenPolyline` |
| 3378–3419 | `HfssFieldsCalc` |
| 3420–3629 | `CalcObject` |
| 3630–3636 | `NamedCalcObject` |
| 3637–3642 | `ConstantCalcObject` |
| 3643–3648 | `ConstantVecCalcObject` |
| 3649–3672 | `get_active_project` |
| 3673–3677 | `get_active_design` |
| 3678–3683 | `get_report_arrays` |
| 3684–3748 | `load_ansys_project` |

## 6. External consumers (must keep working)

- **packages/pyEPR/pyEPR/__init__.py:** `from . import ansys`, `from .ansys import parse_units, parse_units_user, parse_entry`
- **packages/pyEPR/pyEPR/project_info.py:** `ansys.load_ansys_project`, `ansys.release`
- **packages/pyEPR/pyEPR/core_quantum_analysis.py:** `from .ansys import ureg`
- **packages/pyEPR/pyEPR/core_distributed_analysis.py:** `from .ansys import CalcObject, ConstantVecCalcObject, set_property, ureg`
- Tutorials/docs reference `pyEPR.ansys.HfssApp`, `HfssEMSetup`, `CalcObject`, etc.

## 7. Lessons learned and pitfalls

Use this section to avoid repeating mistakes in future refactors.

- **Circular imports**
  - **hfss_project ↔ hfss_design:** `HfssProject` needs `HfssDesign` for `get_designs()`, `get_design()`, `get_active_design()`, `new_design()`. Do not use a top-level import of `HfssDesign` in `hfss_project.py`; use a **lazy import** inside those methods (`from .hfss_design import HfssDesign`).
  - **hfss_setup ↔ hfss_fields_calc:** `HfssSetup.get_fields()` returns `HfssFieldsCalc(self)`; `add_fields_convergence_expr` uses `NamedCalcObject`. Import `HfssFieldsCalc` and `NamedCalcObject` **inside** those methods to avoid cycles.
  - **hfss_fields_calc → hfss_setup:** `hfss_fields_calc` imports `HfssDMSetup` from `hfss_setup` for `isinstance(self.setup, HfssDMSetup)` in `CalcObject.evaluate()`. This is safe because `hfss_setup` does not import `hfss_fields_calc` at top level.
  - **Import order in ansys/__init__.py (pyaedt path):** Load `_backend`, `_units`, `_wrapper` first; then app → desktop → project → design; then setup, design_solutions, frequency_sweep, report, optimetrics, modeler, model_entity, fields_calc; then load. Do not import design before its dependencies (setup, modeler, etc.).

- **Backend resolution**
  - Backend is set once when `_backend` is first imported (`_resolve_backend_from_env()` runs at end of `_backend.py`). Changing `PYEPR_USE_PYAEDT` after `import pyEPR.ansys` has no effect; the process must be restarted (or the backend switched via `set_backend()` if both are available).

- **load_ansys_project**
  - When opening a project by name that is not already open, `project_path` is **required**. The implementation raises `ValueError` if `project_path` is None in that case. Document this in the function docstring and in this doc.

- **Pyaedt-only modules and COM fallbacks**
  - Pyaedt submodules contain **no** `if using_com()` branches. They do contain "COM fallbacks" where the code calls the design/setup COM object (e.g. `odesign.Analyze(name)`): pyaedt still exposes COM under the hood, so these calls are kept. Do not remove them when trimming "COM-only" code.

- **_ReporterWrapper**
  - Exists only in the pyaedt path. It wraps the ReportSetup COM module so that `ExportToFile` can use PyAEDT's native API when the raw gRPC COM call fails. Used by `HfssDesign._reporter`.

- **When no backend is available**
  - If both pyaedt and COM are unavailable, `_BACKEND` is `None`. The package still takes the `else` branch in `__init__.py` and loads pyaedt submodules. Calling `HfssApp()` (or similar) will then fail at runtime. Consider documenting or handling "no backend" explicitly if desired.

- **ansys_com location**
  - `ansys_com` is a **sibling** of the `ansys` package (`..ansys_com`), not a submodule. The COM path does **not** import from inside `ansys/` except for `_backend` (for backend API stubs).

## 8. Next steps (future refactor work)

Use this section as a starting point for the next phase.

- **Validation:** Run the full pyEPR test suite ([packages/pyEPR/tests/](packages/pyEPR/tests/)) and, where possible, tutorial notebooks with both backends (`PYEPR_USE_PYAEDT` unset and set) to confirm parity and compatibility.
- **API parity:** Compare pyaedt module behavior with ansys_com (and the old dual-backend ansys.py) for key workflows (open project, run setup, export report, field calcs, Q3D matrix export). Some pyaedt modules were condensed (e.g. HfssModeler, Polyline/OpenPolyline); restore or add any missing methods if needed.
- **Documentation:** Document `PYEPR_USE_PYAEDT` in user-facing docs (README, installation, or configuration) and in docstrings for `get_backend` / `set_backend`.
- **Deprecation (optional):** If the long-term goal is pyaedt-only, define a deprecation path for the COM backend and timeline.
- **Known gaps (optional):** List any known trimmed or simplified methods in the pyaedt modules (e.g. HfssModeler copy/rename, OpenPolyline sweep_along_path, CalcObject integration helpers) that may need to be restored from ansys_com or the original ansys.py for full parity.
