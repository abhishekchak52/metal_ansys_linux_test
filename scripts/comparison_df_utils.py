import pandas as pd


def create_comparison_dataframe(results: pd.DataFrame) -> pd.DataFrame:
    """Transform results (one row per sample with nested ref/pred dicts) into long format."""

    comparison_df_list = []

    # 1. Design parameters
    if "ref_design" in results and "pred_design" in results:
        design_ref_long = (
            pd.json_normalize(results["ref_design"])
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="reference")
        )
        design_pred_long = (
            pd.json_normalize(results["pred_design"])
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="predicted")
        )
        design_comparison = pd.merge(
            design_ref_long,
            design_pred_long,
            on=["Sample", "quantity"],
        ).assign(category="Design param")
        comparison_df_list.append(design_comparison)

    # 2. H_params
    if "ref_H_params" in results and "pred_H_params" in results:
        h_ref_long = (
            pd.json_normalize(results["ref_H_params"])
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="reference")
        )
        h_pred_long = (
            pd.json_normalize(results["pred_H_params"])
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="predicted")
        )
        hparams_comparison = pd.merge(
            h_ref_long,
            h_pred_long,
            on=["Sample", "quantity"],
        ).assign(category="H param")
        comparison_df_list.append(hparams_comparison)

    # 3. Cap matrix (drop 'units')
    if "ref_cap_matrix" in results and "pred_cap_matrix" in results:
        cap_ref_long = (
            pd.json_normalize(results["ref_cap_matrix"])
            .drop(columns=["units"], errors="ignore")
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="reference")
        )
        cap_pred_long = (
            pd.json_normalize(results["pred_cap_matrix"])
            .drop(columns=["units"], errors="ignore")
            .assign(Sample=results["Sample"])
            .melt(id_vars="Sample", var_name="quantity", value_name="predicted")
        )
        capmatrix_comparison = pd.merge(
            cap_ref_long,
            cap_pred_long,
            on=["Sample", "quantity"],
        ).assign(category="Capacitance")
        comparison_df_list.append(capmatrix_comparison)

    # 4. Concatenate and sort; index: Sample, category, quantity
    comparison_df = pd.concat(comparison_df_list, ignore_index=True)
    comparison_df = comparison_df.sort_values(
        ["Sample", "category", "quantity"]
    ).set_index(["Sample", "category", "quantity"])
    return comparison_df
