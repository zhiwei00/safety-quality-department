import datetime
import os
import re
import sys
from pathlib import Path
from typing import List

import requests


class Process:
    def __init__(self, input_dir: str, ocr_ip: str, text_port: str, table_port: str, ):
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(os.path.dirname(os.path.realpath(sys.argv[0]))).joinpath("缓存")
        self.run_time = datetime.datetime.today().strftime("%Y年%m月%d日%H时%M分%S秒")
        self.root_path: Path = Path(__file__).parent
        self.ocr_text = f"http://{ocr_ip}:{text_port}/ysocr/ocr"
        self.ocr_table = f"http://{ocr_ip}:{table_port}/api/table/task"
        self.pdf_list: List[dict] = self.get_pdf()
        self.zip_path = None

    def get_pdf(self):
        pdf_list = []
        if self.input_dir.is_dir():
            for item in self.input_dir.iterdir():
                if item.is_file() and item.suffix.lower() == ".pdf":
                    pdf_list.append({"name": item.name, "source": item.__str__(), "target": None,
                                     "header": None, "wbs": None, "department": None})
        else:
            raise Exception("输入的扫描路径不是一个文件夹.")
        return pdf_list

    def get_ocr_text(self):
        def find_element_index(lst, target):
            try:
                index = lst.index(target)
                return index
            except ValueError:
                return None

        texts = ["WBS号", "项目名称", "外部部门", "项目经理", "外包人员", "联系方式", ["开始时间", "计划进场日期"],
                 ["离职时间", "计划退场日期"], "补提采购离职时间", "人员级别", "人员类别", "人员单价", "外包供应商",
                 "是否本地化", "工作地",
                 "省份", "状态", "有无采购申请", "采购申请到期", "网络安全承诺书", "保密协议", ["姓名", "面试人姓名"]]
        for pdf_info in self.pdf_list:
            response = requests.post(self.ocr_text, files={"file": open(pdf_info['source'], "rb"),
                                                           "active_desalt_signet": True})
            if response.status_code == 200 and response.json()['code'] == 200:
                tmp = {}
                for index, row in enumerate(response.json()['img_data_list']):
                    text_list = [i['text_string'].strip().replace(' ', '') for i in row['text_info'] if
                                 i['text_string'].strip()]
                    for t in texts:
                        if isinstance(t, str):
                            f_index = find_element_index(text_list, t)
                            if f_index and len(text_list) - 1 > f_index:
                                tmp[t] = text_list[f_index + 1]
                        if isinstance(t, list):
                            f_index = find_element_index(text_list, t[1])
                            if f_index and len(text_list) - 1 > f_index:
                                tmp[t[0]] = text_list[f_index + 1]
                    print(text_list)
                    print(tmp)
                    break
        return

    def get_ocr_table(self):
        def find_element_index(lst, target):
            try:
                index = lst.index(target)
                return index
            except ValueError:
                return None
        texts = ["WBS号", "项目名称", "外部部门", "项目经理", "外包人员", "联系方式", ["开始时间", "计划进场日期"],
                 ["离职时间", "计划退场日期"], "补提采购离职时间", ["人员级别", ""], "人员类别", ["人员单价", "初定人天单价"],
                 ["外包供应商", "外包单位"],
                 "是否本地化", "工作地", "省份", "状态", "有无采购申请", "采购申请到期", "网络安全承诺书", "保密协议",
                 ["姓名", "面试人姓名"]]
        for pdf_info in self.pdf_list:
            tmp = {}
            response = requests.post(self.ocr_table,
                                     files={"file": open(pdf_info['source'], "rb"), },
                                     data={"feature_type_id": 89,
                                           "async_task": False},
                                     )
            if response.status_code == 200 and response.json()['message'] == "任务创建成功":
                print(response.json())
                text_list = []
                for index, table in enumerate(response.json()['result'][0]['result']['tables']):
                    [text_list.extend(i) for i in table['tables'][0]['text_matrix']]
                    break
                text_list = [i.strip().replace(' ', '') for i in text_list if i.strip()]
                print(text_list)
                for t in texts:
                    if isinstance(t, str):
                        f_index = find_element_index(text_list, t)
                        if f_index and len(text_list) - 1 > f_index:
                            tmp[t] = text_list[f_index + 1]
                    if isinstance(t, list):
                        f_index = find_element_index(text_list, t[1])
                        if f_index and len(text_list) - 1 > f_index:
                            tmp[t[0]] = text_list[f_index + 1]
                print(tmp)


if __name__ == '__main__':
    p = Process(r"I:\Project\safety-quality-department\4\扫描",
                "172.28.2.102",
                "50000",
                "15263", )
    p.pdf_list = [{"source": r"I:\Project\safety-quality-department\4\扫描\W00698 蔡嘉豪、.pdf"}]
    p.get_ocr_table()
    # p.get_ocr_text()
