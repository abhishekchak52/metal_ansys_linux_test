# Ansys interface structure (pyEPR)

**Document status:** Last updated after pyaedt parity refactor (HfssDesign create_*_setup, OpenPolyline, HfssModeler full COM parity). `ansys.py` removed; `ansys/` package and `PYEPR_USE_PYAEDT` dispatch in place. **Section 9.6** is the handoff summary for the next stage of refactoring.

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
- `HfssDesign`: holds `HfssModeler`, `Optimetrics`; `get_setup()` → `HfssEMSetup` / `HfssDMSetup` / `HfssDTSetup` / `AnsysQ3DSetup`; provides `create_em_setup`, `create_dm_setup`, `create_dt_setup`, `create_q3d_setup`, `delete_setup`; uses `HfssDesignSolutions`, `HfssReport`, `HfssFrequencySweep`
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

- **Resolved — HfssDesign create_*_setup:** Implemented `create_em_setup`, `create_dm_setup`, `create_dt_setup`, `create_q3d_setup` in [packages/pyEPR/pyEPR/ansys/hfss_design.py](packages/pyEPR/pyEPR/ansys/hfss_design.py) for the pyaedt backend; `project_info.connect_setup()` now works when no setup exists (e.g. Q3D). `delete_setup` was also added for API parity.
- **Validation:** Run the full pyEPR test suite ([packages/pyEPR/tests/](packages/pyEPR/tests/)) and, where possible, tutorial notebooks with both backends (`PYEPR_USE_PYAEDT` unset and set) to confirm parity and compatibility.
- **API parity:** Compare pyaedt module behavior with ansys_com (and the old dual-backend ansys.py) for key workflows (open project, run setup, export report, field calcs, Q3D matrix export). Some pyaedt modules were condensed (e.g. HfssModeler, Polyline/OpenPolyline); restore or add any missing methods if needed.
- **Documentation:** Document `PYEPR_USE_PYAEDT` in user-facing docs (README, installation, or configuration) and in docstrings for `get_backend` / `set_backend`.
- **Deprecation (optional):** If the long-term goal is pyaedt-only, define a deprecation path for the COM backend and timeline.
- **Known gaps (optional):** After the refactor below, HfssDesign setup creation, OpenPolyline, and HfssModeler are at parity with COM for the flows used by project_info, qiskit-metal ansys_renderer (Q3D/HFSS), and model_entity. Remaining gaps (if any) are in lesser-used workflows (e.g. CalcObject integration, PyAEDT-native APIs).

### 8.1 HfssDesign API parity status (pyaedt backend)

| Method (ansys_com) | ansys/hfss_design.py | Used by |
|--------------------|----------------------|---------|
| `create_em_setup` | Implemented | project_info.connect_setup |
| `create_dm_setup` | Implemented | project_info.connect_setup |
| `create_dt_setup` | Implemented | project_info.connect_setup |
| `create_q3d_setup` | Implemented | project_info.connect_setup |
| `delete_setup` | Implemented | (parity) |
| `get_setup_names`, `get_setup`, `name`, `solution_type`, `modeler`, `get_variable_names`, `get_nominal_variation`, `clean_up_solutions`, `get_fields`, `add_message`, `save_screenshot`, `rename_design`, `copy_to_project`, `duplicate`, `export_report_to_file` | Present | project_info / core_distributed_analysis |

## 9. Refactoring updates (pyaedt parity)

Summary of changes made to the pyaedt subpackage so it matches the COM API used by `project_info`, qiskit-metal ansys_renderer (Q3D/HFSS), and model_entity. All edits were confined to `packages/pyEPR/pyEPR/ansys/`; `ansys_com.py` was not modified.

### 9.1 HfssDesign ([ansys/hfss_design.py](packages/pyEPR/pyEPR/ansys/hfss_design.py))

- **Added:** `create_q3d_setup`, `create_dm_setup`, `create_dt_setup`, `create_em_setup` — each calls `self._setup_module.InsertSetup(...)` with the same setup type and property arrays as ansys_com (Matrix / HfssDriven / HfssEigen), then returns the corresponding setup wrapper (`AnsysQ3DSetup`, `HfssDMSetup`, `HfssDTSetup`, `HfssEMSetup`).
- **Added:** `delete_setup(name)` — calls `_setup_module.DeleteSetups(name)` when name is in `get_setup_names()`.
- **Import:** `increment_name` from `pyEPR.ansys._units` for unique setup names.
- **Rationale:** `project_info.connect_setup()` creates a default setup when none exists (e.g. Q3D); without these methods, `AttributeError: 'HfssDesign' object has no attribute 'create_q3d_setup'` occurred.

### 9.2 OpenPolyline ([ansys/model_entity.py](packages/pyEPR/pyEPR/ansys/model_entity.py))

- **Added:** `vertices()`, `fillet(radius, vertex_index)`, `fillets(radius, do_not_fillet=[])`, `sweep_along_path(to_sweep)`, `rename(new_name)`, `copy(new_name)`; property `show_direction` via `make_prop`; `__init__` sets `n_points` when `points` is provided.
- **Imports:** `increment_name` from `_units`; `numpy as np` for `fillets` (np.delete); `make_prop` from `_wrapper`.
- **Rationale:** qiskit-metal ansys_renderer `render_element_path` uses `poly_ansys.rename(name)`, then `modeler._fillet(...)` and `modeler._sweep_along_path(shortline, poly_ansys)`. OpenPolyline.rename and the modeler sweep/fillet methods were required for lom_test path rendering.

### 9.3 HfssModeler ([ansys/hfss_modeler.py](packages/pyEPR/pyEPR/ansys/hfss_modeler.py))

**Phase 1 — Critical for ansys_renderer / lom_test**

- **Fixes:** `_attributes_array` wireframe string built like COM (`flags += "#" if len(flags) > 0 else ""` then `flags += "Wireframe"`). `draw_rect_corner`: added `"WhichAxis:=", axis` to CreateRectangle. `get_objects_in_group(group)`: now returns `list(...)` (or `list()` when _modeler is falsy).
- **Added:** `draw_rect_center(pos, x_size=0, y_size=0, z_size=0, **kwargs)`, `subtract(blank_name, tool_names, keep_originals=False)`.

**Phase 2 — Critical for HFSS / components**

- **Added:** `unite(names, keep_originals=False)`, `assign_perfect_E(obj, name="PerfE")` (with `increment_name` vs boundaries).
- **Updated:** `eval_expr(expr, units="mm")` — optional `units`; delegates to `self.parent.eval_expr(expr, units)` when parent has it.

**Phase 3 — Full COM parity**

- **Added:** `get_all_properties`, `translate(name, vector)`, `intersect(names, keep_originals=False)`, `get_boundary_assignment`, `append_PerfE_assignment`, `_make_lumped_rlc`, `_make_lumped_port` (using `fix_units`, `LENGTH_UNIT`, `increment_name` from `_units`); `mesh_reassign`, `mesh_get_names`, `mesh_get_all_props`, `append_mesh`; `draw_cylinder`, `draw_cylinder_center`, `draw_wirebond`, `draw_region`; `set_working_coordinate_system`, `create_relative_coorinate_system_both` (typo kept for API compatibility); `_fillet_edges`, `sweep_along_vector`.
- **Updated:** `mesh_length`: invalid kwargs now logged with `logger.error` like COM. `copy(obj)`: return value normalized to a single name (first element if list/tuple).
- **Imports:** `copy` (stdlib), `LENGTH_UNIT`, `fix_units`, `increment_name` from `_units`. `get_vertex_ids` uses `GetVertexIDsFromObject` when available, else `GetVertexIDs`.

### 9.4 Verification

- **Script:** [scripts/lom_test.py](scripts/lom_test.py) with `PYEPR_USE_PYAEDT` set — exercises connect_setup (create_q3d_setup), path rendering (draw_polyline → OpenPolyline.rename, _fillet, _sweep_along_path), and optionally chip/ground (draw_rect_center, subtract) when the design includes those elements.
- **Scope:** All changes are under `packages/pyEPR/pyEPR/ansys/`; no edits to ansys_com, qiskit-metal, or scripts except for manual testing.

### 9.5 Starting the next stage

- **Validation:** Run pyEPR tests and lom_test (and HFSS flows if applicable) with both backends to confirm parity.
- **Remaining parity:** Compare other classes (e.g. HfssSetup, HfssDesignSolutions, Optimetrics, HfssFieldsCalc) with ansys_com line ranges in Section 5; add any missing methods or fix signature/behavior differences as needed.
- **Docs:** Document `PYEPR_USE_PYAEDT` and backend selection in user-facing docs and in `get_backend` / `set_backend` docstrings.

### 9.6 Summary for next-stage refactoring (handoff)

Use this subsection to resume work or hand off to another developer/AI.

**Problems addressed**

1. **HfssDesign missing setup creation** — With `PYEPR_USE_PYAEDT` set, `project_info.connect_setup()` failed with `AttributeError: 'HfssDesign' object has no attribute 'create_q3d_setup'` when no setup existed (e.g. new Q3D design). Secondary failure in `disconnect()` due to incomplete connection.
2. **OpenPolyline and HfssModeler gaps** — After fixing (1), `scripts/lom_test.py` (and qiskit-metal ansys_renderer for Q3D/HFSS) still failed because the pyaedt backend lacked `OpenPolyline` methods (`rename`, `vertices`, `fillet`/`fillets`, `sweep_along_path`, `copy`, `show_direction`) and many `HfssModeler` methods (`_fillet`, `_sweep_along_path`, `draw_rect_center`, `subtract`, `unite`, `assign_perfect_E`, mesh/cylinder/wirebond/region/coordinate-system methods, etc.).

**Solutions applied**

- **HfssDesign:** Implemented `create_q3d_setup`, `create_dm_setup`, `create_dt_setup`, `create_em_setup`, and `delete_setup` in `ansys/hfss_design.py` (mirroring ansys_com; uses `_setup_module.InsertSetup` and returns the correct setup wrapper).
- **OpenPolyline:** Implemented full COM parity in `ansys/model_entity.py`: `vertices()`, `fillet`/`fillets`, `sweep_along_path`, `rename`, `copy`, `show_direction`, and `n_points` in `__init__`.
- **HfssModeler:** Brought `ansys/hfss_modeler.py` to full COM parity: fixed `_attributes_array` (wireframe), `draw_rect_corner` (WhichAxis), `eval_expr` (units + parent delegation), `get_objects_in_group` (return list), `copy` (return single name); added `subtract`, `draw_rect_center`, `unite`, `assign_perfect_E`, `translate`, `intersect`, boundary/mesh/cylinder/wirebond/region/coordinate-system methods, `_fillet_edges`, `sweep_along_vector`, and lumped RLC/port helpers.

**Files modified**

- `packages/pyEPR/pyEPR/ansys/hfss_design.py` — create_*_setup, delete_setup.
- `packages/pyEPR/pyEPR/ansys/model_entity.py` — OpenPolyline methods and properties.
- `packages/pyEPR/pyEPR/ansys/hfss_modeler.py` — fixes and full COM parity (Phases 1–3).
- `ANSYS_INTERFACE_STRUCTURE.md` — this document (Sections 4, 8, 8.1, 9).
- No changes to `ansys_com.py`, qiskit-metal, or scripts except for manual testing.

**Current status**

- **Done:** HfssDesign setup creation, OpenPolyline parity, and HfssModeler full COM parity. Document status and API parity tables (Sections 8.1, 9.1–9.4) are up to date.
- **Next:** (1) **Validation** — run `packages/pyEPR/tests/`, `scripts/lom_test.py`, and relevant notebooks with `PYEPR_USE_PYAEDT` set and unset. (2) **Remaining API parity** — compare `HfssSetup`, `HfssDesignSolutions`, `Optimetrics`, `HfssFieldsCalc` (and related) with ansys_com (Section 5 line ranges) and implement any missing methods. (3) **Documentation** — document `PYEPR_USE_PYAEDT` and backend selection in user-facing docs and in `get_backend` / `set_backend` docstrings.
