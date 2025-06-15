import pandas as pd
import numpy as np
import glob
import os
# .xlsx では openpyxl が必要
# PCのコマンドで "pip install openpyxl" を実行

# ファイルの読み込みと出力フォルダ
input_folder = "./data"
output_folder = "./data/output"
# 出力フォルダがなければ作成
os.makedirs(output_folder, exist_ok=True)
# 拡張子を変えること
file_list = sorted(glob.glob(os.path.join(input_folder, "ALL*.csv")))

for filepath in file_list:
    # ファイル名（拡張子なし）を取得
    basename = os.path.splitext(os.path.basename(filepath))[0]
    print(f"Processing: {basename}")
    # データ読み込み（ヘッダー行数に応じてskiprows調整）
    df = pd.read_csv(filepath, header=None, skiprows=25)  # CSV読み込み
    #df = pd.read_excel(filepath, header=None, skiprows=25)  # Excel読み込み
    # データを列ごとに配列に入れる
    # データファイルの仕様に合わせること
    try:
        freq1 = df[0].astype(float).to_numpy()
        volt1 = df[1].astype(float).to_numpy()
        freq2 = df[2].astype(float).to_numpy()
        volt2 = df[3].astype(float).to_numpy()
    except Exception as e:
        print(f"Error in file {filepath}: {e}")
        continue
##########
    # 任意の演算 計算したい式を入力すること npが便利
    processed1 = (10 * volt1) / (5e-4) *1e-5
    processed2 = (1e-7 * volt2) /(2e-5) *1e2
##########
    # 出力のためのデータフレーム構築
    output_df = pd.DataFrame({
    'Freq1': [f"{x:.4e}" for x in freq1],
    'Volt1_processed': [f"{x:.4e}" for x in processed1],
    'Volt2_processed': [f"{x:.4e}" for x in processed2]
    })
    # 出力ファイルパスを出力フォルダに変更
    output_path = os.path.join(output_folder, f"{basename}.dat")
    # .datファイルとして出力（スペース区切り）
    output_df.to_csv(output_path, sep=' ', index=False, header=False)
    print(f"{basename}.dat saved to {output_folder}")