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
        for pdf_info in self.pdf_list:
            response = requests.post(self.ocr_text, files={"file": open(pdf_info['source'], "rb"),
                                                           "active_desalt_signet": True})
            if response.status_code == 200 and response.json()['code'] == 200:
                for index, row in enumerate(response.json()['img_data_list']):
                    text_list = [i['text_string'].strip() for i in row['text_info'] if i['text_string'].strip()]
                    text = ''.join(text_list).replace(' ', '')
                    if len(text_list):
                        pdf_info['header'] = text_list[0]
                    print(text_list)
                    print(text)
                    break
        return

    def get_ocr_table(self):
        for pdf_info in self.pdf_list:
            response = requests.post(self.ocr_table,
                                     files={"file": open(pdf_info['source'], "rb"),},
                                     data={"feature_type_id": 89,
                                           "async_task": False},
                                     )
            if response.status_code == 200 and response.json()['message'] == "任务创建成功":
                print(response.json())


if __name__ == '__main__':
    p = Process(r"I:\Project\safety-quality-department\4\扫描",
                "172.28.2.102",
                "50000",
                "15263", )
    p.pdf_list = [{"source": r"I:\Project\safety-quality-department\4\扫描\W00698 蔡嘉豪、.pdf"}]
    # p.get_ocr_table()
    p.get_ocr_text()
