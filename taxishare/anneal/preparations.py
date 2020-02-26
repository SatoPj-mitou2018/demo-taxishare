from datetime import date
import numpy as np
import pandas as pd
from scipy.stats import zscore


def normalize(df):
    """
    特徴量を標準化する。

    Parameters
    ----------
    df: pandas.dataframe
        標準化前の特徴量データフレーム

    Returns
    -------
    norm_df: pandas.dataframe
        標準化された特徴量データフレーム
    """

    def calc_age(born):
        """
        生年月日から年齢を計算する。

        Parameters
        ----------
        born: datetime.datetime
            利用者の生年月日

        Returns
        -------
        age: int
            利用者の年齢
        """
        today = date.today()
        age = today.year-born.year-((today.month, today.day)<(born.month, born.day))
        return age

    # 年齢を算出する。
    df['age'] = df['birth_date'].map(calc_age)

    # 標準化する。
    norm_df = pd.DataFrame()
    # norm_df['id'] = df['id']
    f_cols = ['desitination_latitude', 'desitination_longitude', 'age', 'sex']
    norm_df[f_cols] = df[f_cols].apply(zscore)
    return norm_df


def calc_dist_array(norm_df, f_w=[1, 1, 1]):
    """
    特徴量からデータ間距離を求める。

    Parameters
    ----------
    norm_df: pandas.dataframe
        標準化された特徴量のデータフレーム
    f_w: list
        各特徴量の重み

    Returns
    -------
    dist_array: numpy.ndarray
        利用者間のデータ間距離2次元配列（上三角行列）
    """
    d_lat = norm_df['desitination_latitude'].values
    d_long = norm_df['desitination_longitude'].values
    age = norm_df['age'].values
    sex = norm_df['sex'].values

    def square_diff_matrix(f_array):
        """
        1次元配列の各要素の差分の二乗を計算する。

        Parameters
        ----------
        f_array: numpy.ndarray
            利用者毎の特徴量を示す１次元配列

        Returns
        -------
        diff_array: numpy.ndarray
            差分の二乗が入った2次元配列
        """
        length_fa = len(f_array)
        diff_array = np.array([(i-j)**2 for i in f_array for j in f_array])
        diff_array = diff_array.reshape(length_fa, length_fa)
        return diff_array

    # 各特徴量の差分の二乗和の行列を求める。
    direct_dist = np.sqrt(square_diff_matrix(d_lat)+square_diff_matrix(d_long))
    age_dist = square_diff_matrix(age)
    sex_dist = square_diff_matrix(sex)

    # 各特徴量への重みづける
    dist_array = f_w[0]*direct_dist+f_w[1]*age_dist+f_w[2]*sex_dist
    dist_array = dist_array/sum(f_w)
    dist_array = np.triu(dist_array)
    return dist_array
