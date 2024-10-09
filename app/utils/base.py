import pandas as pd
from fastapi import HTTPException, status
from openpyxl import load_workbook
from datetime import datetime

from app.utils.files import get_path


class ReportExcel:
    def __init__(self, path_in, path_out):
        self.path_in = path_in
        self.path_out = path_out

    @staticmethod
    async def _get_dict_data(path):
        with open(path, 'r', encoding='utf-8') as file:
            res = file.read()
            result_list = []
            for line in res.splitlines()[6: -2]:
                result_list.append(line.split(',')[:3])

        dct = {}
        date_time = []
        for line in result_list:
            line = list(j.strip('"') for j in line)
            if line[0] not in date_time:
                date_time.append(line[0])
            try:
                dct[line[1]].append(line[2])
            except KeyError:
                dct[line[1]] = []
                dct[line[1]].append(line[2])
        for k, v in dct.items():
            if len(v) != 24:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail=f'В файле {path.split("/")[-1]} отсутствует статистика за час')
        return {'dct': dct, 'date_time': date_time}

    @staticmethod
    async def _get_operators_cic(name):
        with open(f'app/files_db/CICs/{name}.csv', 'r', encoding='utf-8') as file:
            res = file.read()
            operators_cic = {}
            for line in res.splitlines():
                k, v = line.split(',')

                operators_cic[k] = int(v)
            return operators_cic

    async def _dict_result(self, name):
        operators_cic = await self._get_operators_cic(name)
        dict_result = {}
        dict_overload = {}
        not_counted = []

        for operator in self.df_sum:
            if operator in operators_cic:
                values = [float(format(i / operators_cic.get(operator), '.4f'))
                          for i in list(self.df_sum[operator].values)]
                dict_result[operator] = values
                if any(map(lambda x: x >= 0.6, values)):
                    dict_overload[operator] = values
            else:
                dict_result[operator] = [0 * 24]
                not_counted.append(operator)
        return {'dict_result': dict_result, 'dict_overload': dict_overload, 'not_counted': not_counted}

    async def _df_maker(self, name):
        data_in = await self._get_dict_data(self.path_in)
        data_out = await self._get_dict_data(self.path_out)
        dict_in = data_in.get('dct')
        dict_out = data_out.get('dct')
        date_time_in = data_in.get('date_time')

        self.date = datetime.strptime(date_time_in[0], '%d/%m/%Y %H:%M:%S')
        self.columns_all = sorted(set(list(dict_in.keys()) + list(dict_out.keys())))
        self.df_in = pd.DataFrame(dict_in, index=date_time_in, columns=self.columns_all, dtype=float)
        self.df_out = pd.DataFrame(dict_out, index=date_time_in, columns=self.columns_all, dtype=float)
        self.df_sum = self.df_in.add(self.df_out, fill_value=0)
        dict_result = await self._dict_result(name)
        self.df_result = pd.DataFrame(dict_result.get('dict_result'), index=date_time_in)
        self.df_overload = pd.DataFrame(dict_result.get('dict_overload'), index=date_time_in)
        return {'not_counted': dict_result['not_counted']}

    @staticmethod
    async def coloring_values(df):
        def highlight_value(value):
            if value >= 1:
                return 'color: white'
            return

        styled_df = df.style.map(highlight_value).map(
            lambda x: 'background-color: #000001' if x >= 1 else '').map(
            lambda x: ('background-color: red' if 0.8 <= x < 1 else '') or
                      ('background-color: plum' if 0.7 <= x < 0.8 else '') or
                      ('background-color: orange' if 0.6 <= x < 0.7 else ''))
        return styled_df

    @staticmethod
    def set_column_width(path, sheet_name, columns):
        wb = load_workbook(path)
        ws = wb[sheet_name]
        desired_width = 20
        for n, column_cells in enumerate(ws.columns, start=-1):
            column = column_cells[0].column_letter
            if column == 'A':
                ws.column_dimensions[column].width = desired_width
            else:
                desired_width = len(columns[n])
                ws.column_dimensions[column].width = desired_width
        wb.save(path)

    async def write_overload(self, path, name):
        try:
            with pd.ExcelWriter(path, mode='a', if_sheet_exists="overlay") as writer:
                df_overload = await self.coloring_values(self.df_overload)
                df_overload.to_excel(writer, sheet_name=f'Отчет {name}')
        except FileNotFoundError as e:
            with pd.ExcelWriter(path, mode='w') as writer:
                df_overload = await self.coloring_values(self.df_overload)
                df_overload.to_excel(writer, sheet_name=f'Отчет {name}')
        finally:
            self.set_column_width(path=path, sheet_name=f'Отчет {name}', columns=df_overload.columns)

    async def write_exel(self, path, name):
        with pd.ExcelWriter(path, mode='a', if_sheet_exists="overlay") as writer:
            self.df_in.to_excel(writer, sheet_name=f'Общая статистика {name}')
            self.df_out.to_excel(writer, startrow=26, sheet_name=f'Общая статистика {name}')
            self.df_sum.to_excel(writer, startrow=26 * 2, sheet_name=f'Общая статистика {name}')
            styled_df = await self.coloring_values(self.df_result)
            styled_df.to_excel(writer, startrow=26 * 3, sheet_name=f'Общая статистика {name}')
        self.set_column_width(path=path, sheet_name=f'Общая статистика {name}', columns=self.columns_all)

    async def get_result(self, name):
        df_maker = await self._df_maker(name)
        path = f'app/files_db/results/{name.split("-")[0]}_{self.date.date()}.xlsx'
        if name == 'RND' or name == 'SMA':
            path = f'app/files_db/results/SMA_RND_{self.date.date()}.xlsx'
        await self.write_overload(path, name)
        await self.write_exel(path, name)
        return df_maker


async def calculate_load():
    path = get_path()
    nodes = [('SPB-NAT', 'SPB-INT'), ('MSK-NAT', 'MSK-INT'), ('RND', 'SMA')]
    not_counted = {}

    for node in nodes:
        first_node = ReportExcel(path_in=f'{path}/{node[0]}-IN.csv', path_out=f'{path}/{node[0]}-OUT.csv')
        second_node = ReportExcel(path_in=f'{path}/{node[1]}-IN.csv', path_out=f'{path}/{node[1]}-OUT.csv')
        first_node = await first_node.get_result(node[0])
        second_node = await second_node.get_result(node[1])
        if first_node.get('not_counted'):
            not_counted[node[0]] = first_node.get('not_counted')
        if second_node.get('not_counted'):
            not_counted[node[1]] = second_node.get('not_counted')
    return not_counted
