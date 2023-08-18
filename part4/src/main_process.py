import datetime
import re
import shutil
from pathlib import Path
from typing import List
import requests
from .cloud_disk import CloudDisk


class MainProcess:
    def __init__(self, input_dir: str, ocr_ip: str, text_port: str,
                 nari_base: str, nari_user: str, nari_pwd: str):
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path("缓存")
        self.run_time = datetime.datetime.today().strftime("%Y年%m月%d日%H时%M分%S秒")
        self.root_path: Path = Path(__file__).parent
        self.ocr_text = f"http://{ocr_ip}:{text_port}/ysocr/ocr"
        self.nari_base = nari_base
        self.pdf_list: List[dict] = self.get_pdf()
        self.zip_path = None
        self.nari_user = nari_user
        self.nari_pwd = nari_pwd
        self.cookies = None

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
                    find_wbs = re.findall(r"WBS号([A-Za-z0-9]{12})", text)
                    if find_wbs:
                        pdf_info['wbs'] = find_wbs[0]
                    find_department = re.findall(r"项目部门(.*?)项目经理", text)
                    if find_department:
                        pdf_info['department'] = find_department[0]
                    print(pdf_info)
                    break
        return

    def move_and_mkdir(self, pdf_info):
        file_path = self.output_dir.joinpath(self.run_time, pdf_info['department'], pdf_info['wbs'],
                                             f"{pdf_info['header']}.pdf")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_info['source'], file_path)
        pdf_info['target'] = file_path.__str__()
        return pdf_info

    def filing(self):
        for index, pdf_info in enumerate(self.pdf_list):
            if pdf_info['header'] and pdf_info['wbs'] and pdf_info['department']:
                self.pdf_list[index] = self.move_and_mkdir(pdf_info)
        return

    def packing(self):
        base_name = self.output_dir / self.run_time
        self.zip_path = shutil.make_archive(base_name.__str__(),
                                            'zip',
                                            self.output_dir)
        return

    def run(self):
        cloud_disk = CloudDisk(self.nari_base, self.nari_user, self.nari_pwd, "")
        self.get_ocr_text()
        self.filing()
        self.packing()
        print(self.zip_path)
        cloud_disk.file = self.zip_path
        cloud_disk.run()
        return self.output_dir


if __name__ == '__main__':
    p = MainProcess("./扫描",
                    "172.28.2.102",
                    "50000",
                    "d-nari.sgepri.sgcc.com.cn",
                    "4611210148",
                    "Lzw721..")
    p.run()
