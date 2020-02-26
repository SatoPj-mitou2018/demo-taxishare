import json
import numpy as np
import requests


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class CostFunction(object):
    """
    配車を行う目的関数を保持する。

    Attributes
    ----------
    user: int
        利用者数
    taxi: int
        タクシー数
    coefficient_array: numpy.ndarray
        qubit毎の係数を格納する配列
    const: float
        定数
    initialize: method
        qubit毎の係数を定義する。
    to_dict: method
        qubitsの係数配列、定数をデジタルアニーラに投げる形式に変換する。
    """
    def __init__(self, user, taxi):
        """
        Parameters
        ----------
        user: int
            利用者数
        taxi: int
            タクシー数
        coefficient_array: numpy.ndarray
            qubit毎の係数を格納する配列
        const: float
            定数
        """
        self.user = user
        self.taxi = taxi
        number_qubit = (user+5)*taxi
        self.coefficient_array = np.zeros((number_qubit, number_qubit))
        self.const = 0

    def initialize(self, dist_array, penalty1, penalty2):
        """
        qubitの係数を定義する。

        Parameters
        ----------
        dist_array: numpy.ndarray
            データ間距離の上三角行列
        penalty1: int
            制約項1の係数
        penalty2: int
            制約項2の係数
        """
        ylk_started_bit = self.user*self.taxi

        # 2次項を計算する
        for k in range(self.taxi):
            group_k = self.user*k
            for i in range(self.user):
                a = group_k+i
                for j in range(i+1, self.user):
                    b = group_k+j
                    self.coefficient_array[a, b] += dist_array[i, j]+2*penalty2  # (dij+2β)*q_ik*q_jk
                for l in range(5):
                    b = ylk_started_bit+5*k+l
                    self.coefficient_array[a, b] += -l*2*penalty2  # -l*2β*q_ik*y_lk

            for l in range(5):
                a = ylk_started_bit+5*k+l
                for l2 in range(l+1, 5):
                    b = ylk_started_bit+5*k+l2
                    self.coefficient_array[a, b] += 2*penalty2*(l*l2+1)  # 2β*(ll'+1)
        for i in range(self.user):
            for k in range(self.taxi):
                a = self.user*k+i
                for k2 in range(k+1, self.taxi):
                    b = self.user*k2+i
                    self.coefficient_array[a, b] += 2*penalty1  # 2α*q_ik*q_ik'

        # 1次項を計算する
        diag_list = [penalty2-penalty1]*self.user*self.taxi  # (β-α)*q_ik
        diag_list.extend([penalty2*(l*l-1) for _ in range(self.taxi) for l in range(5)])  # β*(ll-1)
        self.coefficient_array += np.diag(diag_list)
        # print(self.coefficient_array)

        # 定数項を計算する
        self.const = penalty1*self.user+penalty2*self.taxi  # αI+βK

    def to_dict(self):
        """
        qubitsの係数配列、定数をデジタルアニーラに投げる形式に変換する。

        Returns
        ----------
        qubit_dict: dictionary
            qubits係数の辞書
        """
        k1 = "coefficient"  # float型で渡す必要あり
        k2 = "polynomials"  # int型で渡す必要あり
        row_i, col_i = self.coefficient_array.nonzero()
        value = self.coefficient_array[row_i, col_i]
        qubit_dict = [{k1: float(v), k2: [int(r), int(c)]} for r, c, v in zip(row_i, col_i, value)]

        if self.const != 0:
            qubit_dict.append({k1: float(self.const), k2: []})

        qubit_dict = {'binary_polynomial': {'terms': qubit_dict}}
        return qubit_dict


class Response(object):
    """
    ソルバーからの処理結果を保持する。

    Attributes
    ----------
    config: dictionary
        qubitの辞書
    energy: float
        タクシー数
    timing: numpy.ndarray
        qubit毎の係数を格納する配列
    qubit_array: numpy.ndarray
        qubitの配列
    to_array: method
        qubitの配列に変換する。
    check_penalty: method
        制約を満たすか確認する。
    group: method
        配車番号を返す。
    """
    def __init__(self, j):
        """
        Parameters
        ----------
        j: json
            デジタルアニーラの戻り値
        """
        config = j['solutions'][0]['configuration']
        self.config = {int(k): int(v) for k, v in config.items()}
        self.energy = j['solutions'][0]['energy']
        self.timing = j['timing']
        self.qubit_array = None

    def to_array(self, user, taxi):
        """
        qubitの配列に変換する。

        Parameters
        ----------
        user: int
            利用者数
        taxi: int
            タクシー数
        """
        dict_v = self.config.values()
        qubit_array = np.array(list(dict_v)[:taxi*user])
        self.qubit_array = qubit_array.reshape((taxi, user))

    def check_penalty(self):
        """
        制約を満たすか確認する。

        Returns
        -------
        f_user: int
            利用者数
        f_taxi: int
            タクシー数
        """
        f_user = len([x for x in self.qubit_array.sum(axis=0) if x != 1])
        f_taxi = len([x for x in self.qubit_array.sum(axis=1) if x >= 5])
        return f_user, f_taxi

    def group(self):
        """
        配車番号を返す。

        Returns
        -------
        number: int
            配車番号
        """
        qubit_array_t = self.qubit_array.T
        index, number = np.where(qubit_array_t == 1)
        return number


class DAPTSolver(object):
    """
    ソルバー情報を保持する。

    Attributes
    ----------
    url: str
        デジタルアニーラのURL
    access_key: str
        APIキー
    rest_headers: dictionary
        接続形式
    params: dictionary
        マシンパラメータ
    minimize: method
        デジタルアニーラで計算する。
    """
    def __init__(self):
        self.url = 'YOUR_URL'
        self.access_key = 'YOUR_KEY'
        self.rest_headers = {'content-type': 'application/json'}
        self.params = {}
        self.params['number_iterations'] = 100_000
        self.params['number_replicas'] = 100
        self.params['offset_increase_rate'] = 1000
        self.params['solution_mode'] = 'QUICK'

    def minimize(self, qubit_dict):
        """
        デジタルアニーラで計算する。

        Parameters
        ----------
        qubit_dict: dictionary
            qubits係数の辞書

        Returns
        -------
        Response: class
            デジタルアニーラの戻り値を処理するクラス
        """
        request = {"fujitsuDAPT": self.params}
        request.update(qubit_dict)
        dump_request = json.dumps(request,cls = MyEncoder).encode('utf-8')
        headers = self.rest_headers
        headers['X-DA-Access-Key'] = self.access_key
        url = self.url + '/v1/qubo/solve'
        response = requests.post(url, dump_request, headers=headers)
        if response.ok:
            j = response.json()[u'qubo_solution']
            if j[u'result_status']:
                return Response(j)
            raise RuntimeError('result_status is false.')
        else:
            raise RuntimeError(response.text)
