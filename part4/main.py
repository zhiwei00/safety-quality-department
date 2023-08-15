import array
import datetime
import hashlib
import json
import os
import random
import re
import shutil
import string
import zipfile
from pathlib import Path
from typing import List
import requests
import dotenv
import execjs
import mimetypes


class Part4:
    def __init__(self, input_dir: str, output_dir: str, ocr_ip: str, text_port: str, table_port: str,
                 nari_base: str, nari_user: str, nari_pwd: str):
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(output_dir)
        self.root_path: Path = Path(__file__).parent
        # dotenv.load_dotenv(self.root_path.joinpath("env"))
        self.ocr_text = f"http://{ocr_ip}:{text_port}/ysocr/ocr"
        self.ocr_table = f"http://{ocr_ip}:{table_port}/api/table/task"
        self.nari_url = f"https://{nari_base}"
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
        file_path = self.output_dir.joinpath(pdf_info['department'], pdf_info['wbs'],
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
        base_name = self.output_dir.parent / datetime.datetime.today().strftime("%Y%m%d")
        self.zip_path = shutil.make_archive(base_name.__str__(),
                                            'zip',
                                            self.output_dir)
        return

    def get_execjs(self, file, *args):
        with open(Path("js").joinpath(file), "r") as file:
            js_code = file.read()
        js_engine = execjs.compile(js_code)
        js_result = js_engine.call(*args)
        return js_result

    def get_cookies(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        rsa = requests.get("https://d-nari.sgepri.sgcc.com.cn/auth/username/rsa", headers=headers)
        if rsa.status_code != 200 or rsa.json().get('code', None) != 0:
            raise Exception("rsa错误")
        rsa_parameter = rsa.json()['result']
        v_pwd = self.get_execjs("v.js", "getV", self.nari_pwd)
        r = v_pwd + "," + rsa_parameter['requestId'] + "," + self.nari_pwd
        rsa_pwd = self.get_execjs("RsaUtils.js", "getEncryptedString",
                                  rsa_parameter['exponent'], "", rsa_parameter['modulus'], r)
        login = requests.post("https://d-nari.sgepri.sgcc.com.cn/auth/username/login",
                              data={"username": self.nari_user,
                                    "password": rsa_pwd,
                                    "requestId": rsa_parameter['requestId'],
                                    "verificationCode": None},
                              headers=headers)
        if login.status_code == 200 and login.json()['code'] == 0:
            self.cookies = login.cookies
            print(login.json())
            print(login.cookies)


    def main(self):
        # self.get_ocr_text()
        # self.filing()
        # self.packing()
        # print(self.zip_path)
        # self.get_cookies()
        self.upload("I:\Project\safety-quality-department\part4\扫描\项目计划书B2462323012900ZM000000.pdf")


if __name__ == '__main__':
    p = Part4("./扫描", "./输出", "172.28.2.102", "50000", "15263", "d-nari.sgepri.sgcc.com.cn",
              "4611210148", "Lzw721..")
    p.main()
