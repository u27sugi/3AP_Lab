import pandas as pd
import numpy as np
import glob, os

def extract_upper_lower(df, e_decimal=5):
    """
    EvsD データフレーム df から，
    ・上側ループ（D が最大の行）
    ・下側ループ（D が最小の行）
    を抽出して返す．
    """
    df = df.copy()
    df['E_round'] = df['E'].round(e_decimal)
    idx_max = df.groupby('E_round')['D'].idxmax()
    idx_min = df.groupby('E_round')['D'].idxmin()
    df_up   = df.loc[idx_max].sort_values('E_round').reset_index(drop=True)
    df_down = df.loc[idx_min].sort_values('E_round').reset_index(drop=True)
    return df_up.drop(columns='E_round'), df_down.drop(columns='E_round')

if __name__ == '__main__':
    input_folder   = 'data/output_20250616'
    output_folder1 = os.path.join(input_folder, 'BTO')
    os.makedirs(output_folder1, exist_ok=True)

    # ─── 上側・下側ループを分割して CSV 出力 ───
    for path in sorted(glob.glob(os.path.join(input_folder, 'ALL*.dat'))):
        fname = os.path.splitext(os.path.basename(path))[0]
        print(f"Processing: {fname}")

        df_all = pd.read_csv(
            path,
            sep=r'\s+',      # 空白文字で分割
            header=0,
            names=['E','D'],
            usecols=[1,2],
            dtype=float,
            comment='#'
        )

        df_up, df_down = extract_upper_lower(df_all)

        # 上側ループ
        df_up.to_csv(os.path.join(output_folder1, f'upper_{fname}.csv'), index=False)
        # 下側ループ
        df_down.to_csv(os.path.join(output_folder1, f'lower_{fname}.csv'), index=False)

    # ─── 抗電場(Ec)と自発分極(Ps)の計算 ───
    results = []
    for upper_path in sorted(glob.glob(os.path.join(output_folder1, 'upper_ALL*.csv'))):
        basename = os.path.basename(upper_path)
        print(f"\nFitting: {basename}")

        # 上側ループ読み込み
        df_up = pd.read_csv(upper_path)
        # 下側ループは同名の lower_*.csv
        lower_fname = basename.replace('upper_', 'lower_')
        lower_path = os.path.join(output_folder1, lower_fname)
        df_down = pd.read_csv(lower_path)

        # 1) df_down から |D| が小さい16点を抽出して Ec を求める
        df_zero = df_down.loc[df_down['D'].abs().nsmallest(16).index]
        E_z = df_zero['E'].to_numpy()
        D_z = df_zero['D'].to_numpy()
        slope_z, intercept_z = np.polyfit(E_z, D_z, 1)
        Ec = -intercept_z / slope_z
        print(f"  → Ec (抗電場) = {Ec:.4e}")

        # 2) Ec を自発分極計算の下限に設定
        E = df_up['E'].to_numpy()
        D = df_up['D'].to_numpy()
        E_fit_min = Ec
        E_fit_max = np.max(E)
        mask = (E >= E_fit_min) & (E <= E_fit_max)

        if mask.sum() < 2:
            print("  → SKIP: フィット点不足. Ec/E_max を見直してください.")
            continue

        slope, Ps = np.polyfit(E[mask], D[mask], 1)
        print(f"  → slope = {slope:.4e}, Ps = {Ps:.4e}")

        results.append({'Filename': basename, 'Ec': Ec, 'Slope': slope, 'Ps': Ps})

    # 結果を CSV 化
    output_df = pd.DataFrame(results)
    output_df.to_csv(os.path.join(input_folder, "BTO_Ps_Ec_results.csv"), index=False)
    print("Saved BTO_Ps_Ec_results.csv")
