import os
from pathlib import Path
from typing import List
import requests
import dotenv


class Part4:
    def __init__(self, input_dir: str, output_dir: str, ip: str, text_port: str, table_port: str):
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(output_dir)
        self.root_path: Path = Path(__file__).parent
        # dotenv.load_dotenv(self.root_path.joinpath("env"))
        self.ocr_text = f"http://{ip}:{text_port}/ysocr/ocr"
        self.ocr_table = f"http://{ip}:{table_port}/api/table/task"

    def get_pdf(self):
        pdf_list = []
        if self.input_dir.is_dir():
            for item in self.input_dir.iterdir():
                if item.is_file() and item.suffix.lower() == ".pdf":
                    pdf_list.append({"name": item.name, "path": item})
        else:
            raise Exception("输入的扫描路径不是一个文件夹.")
        return pdf_list

    def get_ocr_text(self, pdf_list: List[dict]):
        for pdf_info in pdf_list:
            response = requests.post(self.ocr_text, files={"file": open(pdf_info['path'], "rb"),
                                                           "active_desalt_signet": True})
            print(response.json())
            return

    def get_ocr_table(self, pdf_list: List[dict]):
        for pdf_info in pdf_list:
            response = requests.post(self.ocr_table, files={"file": open(pdf_info['path'], "rb"),
                                                            "active_desalt_signet": True})
            print(response.json())
            return
        # try:
        #     ocr_url = f"http://{self.ocr_url}/ysocr/ocr"
        #     response = requests.post(ocr_url, files={"file": open(os.path.join(self.pdf_root_path, pdf['path']), "rb"),
        #                                              "active_desalt_signet": True})
        #     try:
        #         response_json = response.json()
        #         print(response_json)
        #     except Exception as err:
        #         return False, f"{pdf['name']}识别失败：{response.text}"
        #     pdf_text = []
        #     for index, row in enumerate(response_json["img_data_list"]):
        #         text = ''
        #         text_list = [i['text_string'] for i in row['text_info']]
        #         split_text_list = text_list
        #         if len(text_list) > 2 and index > 2:
        #             split_text_list = text_list[2:]
        #         for i in split_text_list:
        #             text += str(i).replace(' ', '')
        #         pdf_text.append(text)
        #     pdf['text'] = pdf_text
        #     return True, pdf
        # except Exception as ex:
        #     print(ex)
        #     return False, pdf


if __name__ == '__main__':
    p = Part4("./扫描", "", "172.28.2.102", "50000", "15263")
    print(p.get_pdf())
    p.get_ocr_data(p.get_pdf())
