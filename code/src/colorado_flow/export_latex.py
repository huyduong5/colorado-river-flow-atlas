from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from .io import read_json, resolve_path, write_text


MODEL_LABELS = {
    "naive": "Naive persistence",
    "seasonal_naive_365": "Seasonal Naive 365",
    "lightgbm_direct": "LightGBM direct 7 (delta)",
}


def vnum(value: Any, digits: int = 2) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    text = f"{value:,.{digits}f}"
    if "." in text:
        integer, decimal = text.rsplit(".", 1)
        return f"{integer.replace(',', '.')}{{,}}{decimal}"
    return text.replace(",", ".")


def plain_num(value: Any, digits: int = 0) -> str:
    if digits == 0:
        return f"{int(round(float(value))):,}".replace(",", ".")
    return f"{float(value):,.{digits}f}".replace(",", ".")


def export_latex(cfg: dict[str, Any], manifest: dict[str, Any]) -> Path:
    latex_dir = Path(cfg["_root_dir"]) / "latex"
    generated = latex_dir / "generated"
    tables_dir = latex_dir / "tables"
    figures_dir = latex_dir / "figures"
    generated.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    results_dir = resolve_path(cfg, "results_dir")
    code_tables = resolve_path(cfg, "tables_dir")
    code_figures = resolve_path(cfg, "figures_dir")
    q1 = read_json(results_dir / "q1_summary.json")
    q2 = read_json(results_dir / "q2_summary.json")
    season = read_json(results_dir / "seasonality_metrics.json")
    quality = read_json(results_dir / "data_quality.json")
    split = read_json(results_dir / "split_manifest.json")
    overall = pd.read_csv(code_tables / "metrics_overall.csv")
    by_horizon = pd.read_csv(code_tables / "metrics_by_horizon.csv")
    top5 = pd.read_csv(code_tables / "extreme_events_top5.csv")

    test = overall[overall["split"] == "test"].set_index("model")
    vals = {
        "DatasetN": plain_num(quality["n_records"]),
        "DateMin": quality["date_min"].replace("-", "/"),
        "DateMax": quality["date_max"].replace("-", "/"),
        "QMean": vnum(quality["stats"]["mean"]),
        "QStd": vnum(quality["stats"]["std_sample"]),
        "QMin": vnum(quality["stats"]["min"]),
        "QMax": vnum(quality["stats"]["max"]),
        "QMedian": vnum(quality["stats"]["median"]),
        "QHigh": vnum(q2["threshold"]),
        "NDaysHigh": plain_num(q2["n_days_high"]),
        "ShareHigh": vnum(q2["share_days_high"] * 100, 2),
        "NEvents": plain_num(q2["n_events"]),
        "ZThreshold": vnum(q2["z_threshold"], 3),
        "TrainOrigins": plain_num(split["splits"]["train"]["n_origins"]),
        "ValOrigins": plain_num(split["splits"]["validation"]["n_origins"]),
        "TestOrigins": plain_num(split["splits"]["test"]["n_origins"]),
        "RefitOrigins": plain_num(split["splits"]["refit"]["n_origins"]),
        "SeasonalStrength": vnum(season["seasonal_strength"], 3),
        "TrendStrength": vnum(season["trend_strength"], 3),
        "AcfYear": vnum(season["acf_lag_365"], 3),
        "MonthlyMinMonth": str(q1["monthly_mean_min"]["month"]),
        "MonthlyMinValue": vnum(q1["monthly_mean_min"]["value"]),
        "MonthlyMaxMonth": str(q1["monthly_mean_max"]["month"]),
        "MonthlyMaxValue": vnum(q1["monthly_mean_max"]["value"]),
        "YearlyMinYear": str(q1["yearly_mean_min"]["year"]),
        "YearlyMinValue": vnum(q1["yearly_mean_min"]["value"]),
        "YearlyMaxYear": str(q1["yearly_mean_max"]["year"]),
        "YearlyMaxValue": vnum(q1["yearly_mean_max"]["value"]),
        "LongestEvent": plain_num(q2["longest_event_days"]),
        "MaxEventPeak": vnum(q2["max_event_peak"]),
        "RunId": manifest["run_id"],
        "DatasetHashShort": manifest["dataset_hash"][:12],
    }
    for model in ("naive", "seasonal_naive_365", "lightgbm_direct"):
        if model not in test.index:
            continue
        row = test.loc[model]
        suffix = {"naive": "Naive", "seasonal_naive_365": "Seasonal", "lightgbm_direct": "Lgbm"}[model]
        vals[f"{suffix}MeanRmse"] = vnum(row["mean_RMSE_7"])
        vals[f"{suffix}MeanMae"] = vnum(row["mean_MAE_7"])
        vals[f"{suffix}MeanNse"] = vnum(row["mean_NSE_7"], 3)
        vals[f"{suffix}PooledRmse"] = vnum(row["pooled_RMSE"])
        vals[f"{suffix}PooledNse"] = vnum(row["pooled_NSE"], 3)

    lines = ["% Sinh tự động bởi export_latex.py; không sửa tay.", ""]
    for key, value in vals.items():
        lines.append(f"\\newcommand{{\\{key}}}{{{value}}}")
    write_text(generated / "numbers.tex", "\n".join(lines) + "\n")

    model_rows = []
    for model in ("naive", "seasonal_naive_365", "lightgbm_direct"):
        if model not in test.index:
            continue
        row = test.loc[model]
        model_rows.append(
            f"{MODEL_LABELS[model]} & {vnum(row['mean_RMSE_7'])} & {vnum(row['mean_MAE_7'])} & "
            f"{vnum(row['mean_NSE_7'], 3)} & {vnum(row['pooled_RMSE'])} & {vnum(row['pooled_NSE'], 3)} \\\\"
        )
    write_text(
        tables_dir / "model_metrics.tex",
        "\\begin{tabular}{lrrrrr}\n\\toprule\n"
        "Mô hình & mean RMSE & mean MAE & mean NSE & pooled RMSE & pooled NSE \\\\\n"
        "\\midrule\n" + "\n".join(model_rows) + "\n\\bottomrule\n\\end{tabular}\n",
    )

    event_rows = []
    for _, row in top5.iterrows():
        event_rows.append(
            f"{int(row['rank'])} & {str(row['start_date'])[8:10]}/{str(row['start_date'])[5:7]}/{str(row['start_date'])[0:4]}"
            f"–{str(row['end_date'])[8:10]}/{str(row['end_date'])[5:7]}/{str(row['end_date'])[0:4]} & "
            f"{int(row['duration_days'])} & {str(row['peak_date'])[8:10]}/{str(row['peak_date'])[5:7]}/{str(row['peak_date'])[0:4]} & "
            f"{vnum(row['peak_flow'])} \\\\"
        )
    write_text(
        tables_dir / "top_events.tex",
        "\\begin{tabular}{clrrr}\n\\toprule\n"
        "Hạng & Khoảng ngày & Số ngày & Ngày đỉnh & Đỉnh (m³/s) \\\\\n"
        "\\midrule\n" + "\n".join(event_rows) + "\n\\bottomrule\n\\end{tabular}\n",
    )

    split_rows = []
    for key, label in (("train", "Train"), ("validation", "Validation"), ("refit", "Refit"), ("test", "Test")):
        s = split["splits"][key]
        split_rows.append(
            f"{label} & {s['target_start'][8:10]}/{s['target_start'][5:7]}/{s['target_start'][0:4]}"
            f"–{s['target_end'][8:10]}/{s['target_end'][5:7]}/{s['target_end'][0:4]} & "
            f"{plain_num(s['n_origins'])} \\\\"
        )
    horizon_test = by_horizon[by_horizon["split"] == "test"].set_index(["model", "horizon"])
    horizon_rows = []
    for horizon in range(1, 8):
        n = horizon_test.loc[("naive", horizon)]
        l = horizon_test.loc[("lightgbm_direct", horizon)]
        horizon_rows.append(
            f"D+{horizon} & {vnum(n['RMSE'])} & {vnum(n['MAE'])} & {vnum(n['NSE'], 3)} & "
            f"{vnum(l['RMSE'])} & {vnum(l['MAE'])} & {vnum(l['NSE'], 3)} \\\\"
        )
    write_text(
        tables_dir / "metrics_by_horizon.tex",
        "\\begin{tabular}{crrrrrr}\n\\toprule\n"
        "Horizon & \\multicolumn{3}{c}{Naive persistence} & \\multicolumn{3}{c}{LightGBM direct 7} \\\\\n"
        "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\n"
        " & RMSE & MAE & NSE & RMSE & MAE & NSE \\\\\n"
        "\\midrule\n" + "\n".join(horizon_rows) + "\n\\bottomrule\n\\end{tabular}\n",
    )

    write_text(
        tables_dir / "split_summary.tex",
        "\\begin{tabular}{llr}\n\\toprule\n"
        "Tập & Khoảng ngày mục tiêu & Số gốc dự báo \\\\\n"
        "\\midrule\n" + "\n".join(split_rows) + "\n\\bottomrule\n\\end{tabular}\n",
    )

    write_text(
        latex_dir / "metadata.tex",
        "\\newcommand{\\University}{TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN}\n"
        "\\newcommand{\\Faculty}{KHOA TOÁN CƠ - TIN HỌC}\n"
        "\\newcommand{\\StudentName}{Dương Quang Huy}\n"
        "\\newcommand{\\StudentId}{23001524}\n"
        "\\newcommand{\\Major}{Khoa học dữ liệu}\n"
        "\\newcommand{\\Course}{68}\n"
        "\\newcommand{\\Supervisor}{GS. Đỗ Minh Đức}\n"
        "\\newcommand{\\ReportTitle}{PHÂN TÍCH VÀ DỰ BÁO CHUỖI THỜI GIAN LƯU LƯỢNG DÒNG CHẢY SÔNG COLORADO GIAI ĐOẠN 2010--2023}\n"
        "\\newcommand{\\ReportPlaceYear}{Hà Nội, 2026}\n",
    )

    for src, dst in (
        ("trend_seasonality.pdf", "trend_seasonality.pdf"),
        ("stl_seasonality.pdf", "stl_seasonality.pdf"),
        ("extremes_full_series.pdf", "extremes_full_series.pdf"),
        ("metrics_by_horizon.pdf", "metrics_by_horizon.pdf"),
        ("forecast_hydrograph.pdf", "forecast_hydrograph.pdf"),
        ("forecast_scatter.pdf", "forecast_scatter.pdf"),
    ):
        src_path = code_figures / src
        if src_path.exists():
            shutil.copy2(src_path, figures_dir / dst)

    logo = Path(cfg["_root_dir"]) / "logo_dhkhtn.jpg"
    if logo.exists():
        shutil.copy2(logo, latex_dir / "assets" / "logo_dhkhtn.jpg")
    return latex_dir
