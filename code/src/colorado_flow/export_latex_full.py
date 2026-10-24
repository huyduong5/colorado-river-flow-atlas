from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .export_latex import MODEL_LABELS, export_latex, plain_num, vnum
from .io import load_raw_csv, read_json, resolve_path, write_json, write_text


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.dpi": 120,
    }
)


def _tex(value: Any) -> str:
    return (
        str(value)
        .replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
    )


def _num(value: Any, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "--"
    return vnum(value, digits)


def _count(value: Any) -> str:
    if value is None or pd.isna(value):
        return "--"
    return plain_num(value)


def _date(value: Any) -> str:
    if value is None or pd.isna(value):
        return "--"
    return pd.Timestamp(value).strftime("%d/%m/%Y")


def _write_tabular(path: Path, spec: str, header: str, rows: list[str]) -> None:
    write_text(
        path,
        "\\begin{tabular}{" + spec + "}\n\\toprule\n"
        + header
        + " \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n",
    )


def _save_figure(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_monthly_box(df: pd.DataFrame, path: Path) -> None:
    q = df["discharge_m3s"]
    months = df.index.month
    data = [q[months == m].to_numpy() for m in range(1, 13)]
    monthly_mean = [float(q[months == m].mean()) for m in range(1, 13)]

    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    bp = ax.boxplot(
        data,
        tick_labels=[f"T{m}" for m in range(1, 13)],
        patch_artist=True,
        showmeans=True,
    )
    for patch in bp["boxes"]:
        patch.set_facecolor("#DBEAFE")
        patch.set_edgecolor("#1D4ED8")
    for median in bp["medians"]:
        median.set_color("#DC2626")
    ax.plot(range(1, 13), monthly_mean, color="#0F766E", marker="o", linewidth=1.4, label="Trung bình tháng")
    ax.set_title("Phân bố lưu lượng theo tháng, 2010–2023")
    ax.set_xlabel("Tháng")
    ax.set_ylabel("m³/s")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, fontsize=8)
    _save_figure(fig, path)


def _plot_yearly_flow(yearly: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ax.plot(yearly["year"], yearly["mean"], color="#1D4ED8", marker="o", linewidth=1.6, label="Trung bình năm")
    ax.fill_between(
        yearly["year"],
        yearly["min"],
        yearly["max"],
        color="#DBEAFE",
        alpha=0.7,
        label="Khoảng min–max",
    )
    ax.set_title("Trung bình và khoảng biến thiên lưu lượng theo năm")
    ax.set_xlabel("Năm")
    ax.set_ylabel("m³/s")
    ax.set_xticks(yearly["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=8)
    _save_figure(fig, path)


def _plot_monthly_heatmap(monthly_by_year: pd.DataFrame, path: Path) -> None:
    frame = monthly_by_year.set_index("year")
    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    image = ax.imshow(frame.to_numpy(), aspect="auto", cmap="YlGnBu", interpolation="nearest")
    ax.set_xticks(range(12), [f"T{m}" for m in range(1, 13)])
    ax.set_yticks(range(len(frame.index)), [str(year) for year in frame.index])
    ax.set_title("Trung bình tháng theo từng năm")
    ax.set_xlabel("Tháng")
    ax.set_ylabel("Năm")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
    colorbar.set_label("m³/s")
    _save_figure(fig, path)


def _plot_high_flow(by_year: pd.DataFrame, by_month: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.6))
    ax = axes[0]
    ax.bar(by_year["year"], by_year["n_days_high"], color="#1D4ED8", alpha=0.85)
    ax.set_title("Số ngày vượt Q95 theo năm")
    ax.set_xlabel("Năm")
    ax.set_ylabel("Số ngày")
    ax.set_xticks(by_year["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.2)

    ax = axes[1]
    ax.bar(by_month["month"], by_month["n_days_high"], color="#0F766E", alpha=0.85)
    ax.set_title("Số ngày vượt Q95 theo tháng")
    ax.set_xlabel("Tháng")
    ax.set_ylabel("Số ngày")
    ax.set_xticks(range(1, 13))
    ax.grid(axis="y", alpha=0.2)
    ax2 = ax.twinx()
    ax2.plot(
        by_month["month"],
        by_month["share_days"] * 100,
        color="#DC2626",
        marker="o",
        linewidth=1.3,
        label="Tỷ lệ ngày vượt Q95",
    )
    ax2.set_ylabel("Tỷ lệ (%)")
    ax2.legend(frameon=False, fontsize=8, loc="upper right")

    _save_figure(fig, path)


def _plot_validation(validation: pd.DataFrame, path: Path) -> None:
    order = ["naive", "seasonal_naive_365", "lightgbm_direct"]
    labels = ["Naive", "Seasonal\nNaive 365", "LightGBM"]
    data = validation.set_index("model")
    metrics = (
        ("mean_RMSE_7", "Mean RMSE (m³/s)"),
        ("mean_MAE_7", "Mean MAE (m³/s)"),
        ("mean_NSE_7", "Mean NSE"),
    )
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.4))
    for ax, (column, title) in zip(axes, metrics):
        values = [float(data.loc[model, column]) if model in data.index else np.nan for model in order]
        colors = ["#64748B", "#DC2626", "#1D4ED8"]
        ax.bar(labels, values, color=colors, alpha=0.88)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.2)
        ax.axhline(0, color="#334155", linewidth=0.8)
    fig.suptitle("So sánh mô hình trên Validation 2020–2021", fontsize=12)
    _save_figure(fig, path)


def _plot_residuals(predictions: pd.DataFrame, path: Path) -> None:
    subset = predictions[predictions["model"] == "lightgbm_direct"]
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2))
    for ax, horizon in zip(axes, (1, 4, 7)):
        part = subset[subset["horizon"] == horizon]
        residual = part["y_pred"] - part["y_true"]
        ax.hist(residual, bins=45, color="#1D4ED8", alpha=0.75)
        ax.axvline(0, color="#DC2626", linewidth=1)
        ax.set_title(f"LightGBM D+{horizon}")
        ax.set_xlabel("Dự báo − quan trắc (m³/s)")
        ax.set_ylabel("Số ngày")
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Phân bố phần dư của LightGBM trên Test 2022–2023", fontsize=12)
    _save_figure(fig, path)


def _plot_feature_importance(importance: pd.DataFrame, path: Path) -> None:
    top = (
        importance.groupby("feature", as_index=False)["gain"]
        .mean()
        .sort_values("gain", ascending=False)
        .head(12)
    )
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.barh(top["feature"][::-1], top["gain"][::-1], color="#0F766E", alpha=0.85)
    ax.set_title("Top 12 feature theo gain trung bình trên 7 horizon")
    ax.set_xlabel("Gain trung bình")
    ax.grid(axis="x", alpha=0.2)
    _save_figure(fig, path)


def _plot_error_by_year(by_year: pd.DataFrame, path: Path) -> None:
    subset = by_year[by_year["model"] == "lightgbm_direct"]
    pivot = subset.pivot(index="horizon", columns="target_year", values="RMSE").sort_index()
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    for year in pivot.columns:
        ax.plot(pivot.index, pivot[year], marker="o", linewidth=1.5, label=str(int(year)))
    ax.set_title("RMSE của LightGBM theo horizon và năm mục tiêu")
    ax.set_xlabel("Horizon (ngày)")
    ax.set_ylabel("RMSE (m³/s)")
    ax.set_xticks(range(1, 8))
    ax.grid(alpha=0.2)
    ax.legend(title="Năm", frameon=False, fontsize=8)
    _save_figure(fig, path)


def _table_data_quality(quality: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in quality.iterrows():
        label = str(row.iloc[0])
        value = str(row.iloc[1])
        if label == "SHA256":
            value = _tex(value[:16]) + r"\ldots{}"
        else:
            value = _tex(value)
        rows.append(f"{_tex(label)} & {value} \\\\")
    _write_tabular(path, "@{}ll@{}", "Hạng mục & Giá trị", rows)


def _table_monthly(monthly: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in monthly.iterrows():
        rows.append(
            f"T{int(row['month'])} & {_count(row['n'])} & {_num(row['mean'])} & "
            f"{_num(row['median'])} & {_num(row['std_sample'])} & {_num(row['min'])} & "
            f"{_num(row['p25'])} & {_num(row['p75'])} & {_num(row['max'])} \\\\"
        )
    _write_tabular(
        path,
        "lrrrrrrrr",
        "Tháng & n & Mean & Median & SD & Min & P25 & P75 & Max",
        rows,
    )


def _table_yearly(yearly: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in yearly.iterrows():
        rows.append(
            f"{int(row['year'])} & {_count(row['n'])} & {_num(row['mean'])} & "
            f"{_num(row['median'])} & {_num(row['std_sample'])} & {_num(row['min'])} & "
            f"{_num(row['p95'])} & {_num(row['max'])} \\\\"
        )
    _write_tabular(
        path,
        "rrrrrrrr",
        "Năm & n & Mean & Median & SD & Min & P95 & Max",
        rows,
    )


def _table_events(events: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in events.iterrows():
        rows.append(
            f"{_tex(row['event_id'])} & {_date(row['start_date'])} & {_date(row['end_date'])} & "
            f"{int(row['duration_days'])} & {_date(row['peak_date'])} & "
            f"{_num(row['peak_flow'])} & {int(row['n_exceedance_days'])} \\\\"
        )
    _write_tabular(
        path,
        "llrrrrr",
        "Mã & Bắt đầu & Kết thúc & Số ngày & Ngày đỉnh & Đỉnh (m³/s) & Ngày vượt",
        rows,
    )


def _table_high_flow_year(by_year: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in by_year.iterrows():
        rows.append(
            f"{int(row['year'])} & {int(row['n_days_high'])} & {int(row['n_days'])} & "
            f"{_num(row['share_days'] * 100)} & {int(row['n_events'])} \\\\"
        )
    _write_tabular(
        path,
        "rrrrr",
        "Năm & Ngày vượt Q95 & Tổng ngày & Tỷ lệ (\\%) & Số đợt",
        rows,
    )


def _table_high_flow_month(by_month: pd.DataFrame, path: Path) -> None:
    rows = []
    for _, row in by_month.iterrows():
        rows.append(
            f"T{int(row['month'])} & {int(row['n_days_high'])} & {int(row['n_days'])} & "
            f"{_num(row['share_days'] * 100)} \\\\"
        )
    _write_tabular(
        path,
        "rrrr",
        "Tháng & Ngày vượt Q95 & Tổng ngày & Tỷ lệ (\\%)",
        rows,
    )


def _table_trials(trials: pd.DataFrame, path: Path) -> None:
    best_trial = int(trials.loc[trials["mean_RMSE"].idxmin(), "trial_id"])
    rows = []
    for _, row in trials.sort_values("trial_id").iterrows():
        trial = int(row["trial_id"])
        label = f"\\textbf{{{trial}}}" if trial == best_trial else str(trial)
        rows.append(
            f"{label} & {_num(row['learning_rate'], 2)} & {int(row['num_leaves'])} & "
            f"{int(row['max_depth'])} & {int(row['min_child_samples'])} & "
            f"{_num(row['reg_lambda'], 1)} & {_num(row['mean_RMSE'])} & "
            f"{_num(row['mean_MAE'])} & {_num(row['mean_NSE'], 3)} \\\\"
        )
    _write_tabular(
        path,
        "rrrrrrrrr",
        "Trial & LR & Leaves & Depth & Min child & Lambda & mean RMSE & mean MAE & mean NSE",
        rows,
    )


def _table_validation(validation: pd.DataFrame, path: Path) -> None:
    order = ["naive", "seasonal_naive_365", "lightgbm_direct"]
    indexed = validation.set_index("model")
    rows = []
    for model in order:
        if model not in indexed.index:
            continue
        row = indexed.loc[model]
        rows.append(
            f"{MODEL_LABELS[model]} & {_num(row['mean_RMSE_7'])} & {_num(row['mean_MAE_7'])} & "
            f"{_num(row['mean_NSE_7'], 3)} & {_num(row['pooled_RMSE'])} & "
            f"{_num(row['pooled_NSE'], 3)} \\\\"
        )
    _write_tabular(
        path,
        "lrrrrr",
        "Mô hình & mean RMSE & mean MAE & mean NSE & pooled RMSE & pooled NSE",
        rows,
    )


def _table_metrics_by_year(by_year: pd.DataFrame, path: Path) -> None:
    order = ["naive", "seasonal_naive_365", "lightgbm_direct"]
    aggregated = (
        by_year.groupby(["model", "target_year"], as_index=False)[["RMSE", "MAE", "NSE"]]
        .mean()
        .sort_values(["model", "target_year"])
    )
    rows = []
    for model in order:
        part = aggregated[aggregated["model"] == model]
        for _, row in part.iterrows():
            rows.append(
                f"{MODEL_LABELS[model]} & {int(row['target_year'])} & {_num(row['RMSE'])} & "
                f"{_num(row['MAE'])} & {_num(row['NSE'], 3)} \\\\"
            )
    _write_tabular(
        path,
        "lrrrr",
        "Mô hình & Năm & RMSE & MAE & NSE",
        rows,
    )


def _table_feature_importance(importance: pd.DataFrame, path: Path) -> None:
    all_gain = importance.groupby("feature", as_index=False)["gain"].mean()
    total = float(all_gain["gain"].sum())
    mean_gain = (
        all_gain.sort_values("gain", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )
    rows = []
    for rank, row in mean_gain.iterrows():
        share = 100.0 * float(row["gain"]) / total if total else 0.0
        rows.append(
            f"{rank + 1} & \\texttt{{{_tex(row['feature'])}}} & {_num(row['gain'])} & {_num(share)} \\\\"
        )
    _write_tabular(
        path,
        "rlrr",
        "Hạng & Feature & Mean gain & Tỷ trọng (\\%)",
        rows,
    )


def _append_numbers(base_path: Path, output_path: Path, values: dict[str, str]) -> None:
    base = base_path.read_text(encoding="utf-8").rstrip()
    extra = "\n".join(f"\\newcommand{{\\{key}}}{{{value}}}" for key, value in values.items())
    write_text(output_path, base + "\n\n" + extra + "\n")


def export_latex_full(cfg: dict[str, Any], manifest: dict[str, Any]) -> Path:
    root = Path(cfg["_root_dir"])
    latex_dir = export_latex(cfg, manifest)
    full_dir = root / "latex_full"
    tables_dir = full_dir / "tables"
    figures_dir = full_dir / "figures"
    generated_dir = full_dir / "generated"
    assets_dir = full_dir / "assets"
    for path in (tables_dir, figures_dir, generated_dir, assets_dir):
        path.mkdir(parents=True, exist_ok=True)

    results_dir = resolve_path(cfg, "results_dir")
    code_tables = resolve_path(cfg, "tables_dir")
    code_figures = resolve_path(cfg, "figures_dir")
    checkpoints = resolve_path(cfg, "checkpoints_dir")
    df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    quality = pd.read_csv(code_tables / "data_quality.csv", dtype=str)
    monthly = pd.read_csv(code_tables / "monthly_stats.csv")
    yearly = pd.read_csv(code_tables / "yearly_stats.csv")
    monthly_by_year = pd.read_csv(code_tables / "monthly_by_year.csv")
    by_year = pd.read_csv(code_tables / "high_flow_by_year.csv")
    by_month = pd.read_csv(code_tables / "high_flow_by_month.csv")
    events = pd.read_csv(code_tables / "extreme_events.csv")
    trials = pd.read_csv(code_tables / "lightgbm_trials.csv")
    validation = pd.read_csv(code_tables / "metrics_validation.csv")
    metrics_by_year = pd.read_csv(code_tables / "metrics_by_year.csv")
    predictions = pd.read_csv(code_tables / "predictions_long.csv")
    importance = pd.read_csv(checkpoints / "lightgbm_feature_importance.csv")

    _table_data_quality(quality, tables_dir / "data_quality.tex")
    _table_monthly(monthly, tables_dir / "monthly_stats.tex")
    _table_yearly(yearly, tables_dir / "yearly_stats.tex")
    _table_events(events, tables_dir / "extreme_events.tex")
    _table_high_flow_year(by_year, tables_dir / "high_flow_by_year.tex")
    _table_high_flow_month(by_month, tables_dir / "high_flow_by_month.tex")
    _table_trials(trials, tables_dir / "lightgbm_trials.tex")
    _table_validation(validation, tables_dir / "validation_metrics.tex")
    _table_metrics_by_year(metrics_by_year, tables_dir / "metrics_by_year.tex")
    _table_feature_importance(importance, tables_dir / "feature_importance.tex")

    for name in ("model_metrics.tex", "top_events.tex", "metrics_by_horizon.tex", "split_summary.tex"):
        source = latex_dir / "tables" / name
        if source.exists():
            shutil.copy2(source, tables_dir / name)

    _plot_monthly_box(df, code_figures / "monthly_boxplot.pdf")
    _plot_yearly_flow(yearly, code_figures / "yearly_flow.pdf")
    _plot_monthly_heatmap(monthly_by_year, code_figures / "monthly_heatmap.pdf")
    _plot_high_flow(by_year, by_month, code_figures / "high_flow_year_month.pdf")
    _plot_validation(validation, code_figures / "validation_comparison.pdf")
    _plot_residuals(predictions, code_figures / "residual_distribution.pdf")
    _plot_feature_importance(importance, code_figures / "feature_importance.pdf")
    _plot_error_by_year(metrics_by_year, code_figures / "error_by_year.pdf")

    for source in code_figures.glob("*.pdf"):
        shutil.copy2(source, figures_dir / source.name)

    q1 = read_json(results_dir / "q1_summary.json")
    season = read_json(results_dir / "seasonality_metrics.json")
    selection = read_json(results_dir / "model_selection_full.json")
    best = selection["best_trial"]
    values = {
        "MonthlyAmplitude": vnum(q1["monthly_amplitude_mean"]),
        "YearlyAmplitude": vnum(q1["yearly_amplitude_mean"]),
        "Acf7": vnum(season["acf_lag_7"], 3),
        "Acf30": vnum(season["acf_lag_30"], 3),
        "Acf182": vnum(season["acf_lag_182"], 3),
        "TrendStart": vnum(season["trend_start"]),
        "TrendEnd": vnum(season["trend_end"]),
        "TrendMin": vnum(season["trend_min"]),
        "TrendMax": vnum(season["trend_max"]),
        "NTrials": plain_num(selection["n_trials"]),
        "BestTrial": plain_num(best["trial_id"]),
        "BestTrialRmse": vnum(best["mean_RMSE"]),
        "BestTrialMae": vnum(best["mean_MAE"]),
        "BestTrialNse": vnum(best["mean_NSE"], 3),
    }
    _append_numbers(latex_dir / "generated" / "numbers.tex", generated_dir / "numbers.tex", values)

    for name in ("metadata.tex",):
        source = latex_dir / name
        if source.exists():
            shutil.copy2(source, full_dir / name)
    for source in (latex_dir / "assets").glob("*"):
        if source.is_file():
            shutil.copy2(source, assets_dir / source.name)

    files = sorted(
        str(path.relative_to(full_dir))
        for path in full_dir.rglob("*")
        if path.is_file() and path.name != "assets_manifest.json"
    )
    write_json(
        generated_dir / "assets_manifest.json",
        {
            "run_id": manifest["run_id"],
            "dataset_hash": manifest["dataset_hash"],
            "tables": [name for name in files if name.startswith("tables/")],
            "figures": [name for name in files if name.startswith("figures/")],
            "files": files,
        },
    )
    return full_dir
