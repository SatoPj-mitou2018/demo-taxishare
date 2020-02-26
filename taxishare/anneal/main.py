import numpy as np
import pandas as pd

from taxishare.anneal import preparations, modeling


def main(df):
    """
    与えられた利用者集団に対し、配車番号を求める。

    Parameters
    ----------
    df: pandas.dataframe
        標準化前の特徴量データフレーム

    Returns
    -------
    number_list:numpy.ndarray
        配車番号リスト
    """

    UPPER_USER = 10

    user = len(df)
    if user > UPPER_USER:
        raise ValueError('number of user is less than 50.')
    else:
        taxi = 15
        norm_df = preparations.normalize(df)
        dist_array = preparations.calc_dist_array(norm_df, [1, 0, 0])
        number_list = []

        if dist_array.any():
            model = modeling.CostFunction(user, taxi)
            model.initialize(dist_array, 10, 10)
            qubit_dict = model.to_dict()
            solver = modeling.DAPTSolver()
            response = solver.minimize(qubit_dict)
            qubit_array = response.to_array(user, taxi)
            f_user, f_taxi = response.check_penalty()
            if f_user == 0 and f_taxi == 0:
                number_list = response.group()
            else:
                raise ValueError('given penalties do not satisfy the function.')
        else:
            number_list = np.random.randint(0, taxi, user)  # 全員が同じ地点にいたらランダムにグループ分け

    return number_list


if __name__=='__main__':
    main(df)
