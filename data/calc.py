import logging
import matplotlib.pyplot as plt
import numpy as np
import uproot

logging.basicConfig(level=logging.INFO)


# ==========================================
# 1. 位置座標変換ユーティリティ
# ==========================================
def file_num_to_position(
    file_numbers, step: float = 0.05, start_pos: float = 0.0
) -> np.ndarray:
    """ファイル番号のシーケンスを実空間の位置配列（例: cm）に変換

    Parameters:
    -----------
    file_numbers : list or iterable
        ファイル番号のリスト（例: range(1, 121)）
    step : float, default 0.05
        1ファイルあたりの移動間隔（例: 0.05 cm）
    start_pos : float, default 0.0
        最初のファイル（先頭要素）に対応する開始位置

    Returns:
    --------
    np.ndarray
        変換された位置の1次元配列
    """
    file_nums = np.array(file_numbers)
    # 先頭要素からの相対インデックスをベースに位置を算出
    indices = file_nums - file_nums[0]
    return start_pos + indices * step


# ==========================================
# 2. ROOTデータ取得・解析ロジック
# ==========================================
def read_histogram_data(file_path: str, obj_name: str = "ADC_HIGH_7"):
    """ROOTファイルから指定オブジェクトのヒストグラム値とx軸BIN中心を取得"""
    with uproot.open(file_path) as f:
        hist = f[obj_name]
        values, edges = hist.to_numpy()
        x_centers = (edges[:-1] + edges[1:]) / 2.0
        return values, x_centers


def calculate_centroid(values: np.ndarray, x_centers: np.ndarray) -> float:
    """ヒストグラムの値と座標から重心（Mean）を計算"""
    total_counts = np.sum(values)
    if total_counts > 0:
        return float(np.sum(x_centers * values) / total_counts)
    return np.nan


def get_single_centroid(
    file_path: str, obj_name: str = "ADC_HIGH_7"
) -> float:
    """単一ROOTファイルから重心を取得"""
    try:
        values, x_centers = read_histogram_data(file_path, obj_name)
        return calculate_centroid(values, x_centers)
    except Exception as e:
        logging.warning(f"Failed to process {file_path}: {e}")
        return np.nan


def get_centroid_array(
    file_numbers,
    base_path: str = "slitA-008-{:03d}.root",
    obj_name: str = "ADC_HIGH_7",
) -> np.ndarray:
    """複数ファイル番号から順に重心の配列を取得"""
    centroids = [
        get_single_centroid(base_path.format(n), obj_name) for n in file_numbers
    ]
    return np.array(centroids)


# ==========================================
# 3. 描画用プロット関数群
# ==========================================
def plot_centroid_trend(
    file_numbers,
    centroids: np.ndarray,
    step: float = None,
    start_pos: float = 0.0,
    unit: str = "cm",
    ax=None,
    **kwargs,
):
    """重心の推移をプロット（step指定の有無で横軸を位置／ファイル番号に切替）"""
    if ax is None:
        ax = plt.gca()

    if step is not None:
        x = file_num_to_position(file_numbers, step=step, start_pos=start_pos)
        xlabel = f"Position [{unit}]"
    else:
        x = np.array(file_numbers)
        xlabel = "File Number"

    line = ax.plot(
        x, centroids, marker=kwargs.pop("marker", "o"), **kwargs
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Centroid (Mean)")
    ax.set_title("Centroid Trend Plot")
    ax.grid(True)
    return line


def plot_histogram(
    file_num: int,
    base_path: str = "slitA-008-{:03d}.root",
    obj_name: str = "ADC_HIGH_7",
    use_x_centers: bool = True,
    label: str = None,
    ax=None,
    **kwargs,
) -> np.ndarray:
    """指定したファイル番号のヒストグラムを描画"""
    if ax is None:
        ax = plt.gca()

    file_name = base_path.format(file_num)
    values, x_centers = read_histogram_data(file_name, obj_name)

    x_axis = x_centers if use_x_centers else np.arange(len(values))
    plot_label = label if label is not None else f"File #{file_num}"

    ax.plot(x_axis, values, label=plot_label, **kwargs)
    return values

# パラメータ設定
file_numbers = list(range(0, 29))
base_path = "slitA-012-{:03d}.root"
obj_name = "ADC_HIGH_7"
step_cm = 0.05  # 1ファイルあたり 0.05 cm

# 1. 重心アレイの取得
centroids = get_centroid_array(file_numbers, base_path, obj_name)

# 位置アレイの計算（単体で必要な場合）
positions = file_num_to_position(file_numbers, step=step_cm, start_pos=0.0)

# 2. 最小・最大の特定
min_idx = np.nanargmin(centroids)
max_idx = np.nanargmax(centroids)

print(
    f"MIN -> File #{file_numbers[min_idx]} ({positions[min_idx]:.2f} cm), "
    f"Centroid: {centroids[min_idx]:.4f}"
)
print(
    f"MAX -> File #{file_numbers[max_idx]} ({positions[max_idx]:.2f} cm), "
    f"Centroid: {centroids[max_idx]:.4f}"
)

# 3. 横軸を「位置(cm)」にして重心推移を描画
plt.figure()
plot_centroid_trend(
    file_numbers, centroids, step=step_cm, start_pos=0.0, unit="cm"
)
plt.savefig("centroid.png")
plt.show()

# 4. 最小・最大のスペクトル比較（位置ラベルを凡例に付記）
fig, ax = plt.subplots()
plot_histogram(
    file_numbers[min_idx],
    base_path,
    obj_name,
    ax=ax,
    label=f"Min ({positions[min_idx]:.2f} cm)",
)
plot_histogram(
    file_numbers[max_idx],
    base_path,
    obj_name,
    ax=ax,
    label=f"Max ({positions[max_idx]:.2f} cm)",
)

ax.set_xlim(700, 1000)
ax.set_xlabel("Channels")
ax.set_ylabel("Counts")
ax.set_title("Max and Min Spectrum Comparison")
ax.legend()
plt.savefig("Maxmin.png")
plt.show()
