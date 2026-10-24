"""GRU direct 7 là hạng mục mở rộng.

Môi trường hiện tại chưa cài PyTorch; module này giữ chỗ để không tạo kết quả giả.
Khi có PyTorch CPU, cài `pip install torch --index-url https://download.pytorch.org/whl/cpu`
và bổ sung huấn luyện theo mục 14 của plan.
"""

from __future__ import annotations


def unavailable_reason() -> str:
    return (
        "GRU chưa chạy trong run này vì môi trường không có PyTorch; "
        "LightGBM direct 7 đáp ứng yêu cầu thuật toán của đề."
    )
