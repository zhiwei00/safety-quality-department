import array
import hashlib
import mimetypes
import os
import string
import sys
from pathlib import Path
import random
import copy
import execjs
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class CloudDisk:
    def __init__(self, nari_base: str, nari_user: str, nari_pwd: str, file: str):
        self.nari_url = f"https://{nari_base}"
        self.nari_user = nari_user
        self.nari_pwd = nari_pwd
        self.file = file
        self.base_body = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        self.cookies = None
        self.symbolic_link_id = None
        self.file_id = None
        self.status = None
        self.get_cookies()

    def spark_md5_hash(self, file_path):
        with open(file_path, "rb") as file:
            arraybuffer = bytearray(file.read())
        bytes_data = array.array("B", arraybuffer).tobytes()
        md5_hash = hashlib.md5(bytes_data).hexdigest()
        return md5_hash

    def get_body(self):
        mime_type, _ = mimetypes.guess_type(self.file)
        p_file = Path(self.file)
        self.base_body = {"appId": "YUNPAN",
                          "storeLocation": "ALL",
                          "docLevel": "2",
                          "id": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)),
                          "name": p_file.name,
                          "relativePath": "",
                          "lastModified": int(p_file.stat().st_ctime * 1000),
                          "mimeType": mime_type,
                          "fileSize": p_file.stat().st_size,
                          "fileName": p_file.name,
                          "md5": self.spark_md5_hash(self.file)}

    def get_execjs(self, file, *args):
        if getattr(sys, 'frozen', False):
            # 在打包后的应用程序中
            js_dir = Path(sys._MEIPASS).joinpath('js')
        else:
            js_dir: Path = Path(Path(os.path.dirname(os.path.realpath(sys.argv[0])))).joinpath('js')
        print(js_dir)
        with open(js_dir.joinpath(file), "r", encoding='utf-8') as file:
            js_code = file.read()
        js_engine = execjs.compile(js_code)
        js_result = js_engine.call(*args)
        return js_result

    def get_cookies(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": self.user_agent
        }
        rsa = requests.get(f"{self.nari_url}/auth/username/rsa", headers=headers)
        if rsa.status_code != 200 or rsa.json().get('code', None) != 0:
            raise Exception(f"rsa err: {rsa.text}")
        rsa_parameter = rsa.json()['result']
        v_pwd = self.get_execjs("v.js", "getV", self.nari_pwd)
        r = str(v_pwd) + "," + str(rsa_parameter['requestId']) + "," + str(self.nari_pwd)
        rsa_pwd = self.get_execjs("RsaUtils.js", "getEncryptedString",
                                  rsa_parameter['exponent'], "", rsa_parameter['modulus'], r)
        login = requests.post(f"{self.nari_url}/auth/username/login",
                              data={"username": self.nari_user,
                                    "password": rsa_pwd,
                                    "requestId": rsa_parameter['requestId'],
                                    "verificationCode": None},
                              headers=headers)
        if login.status_code == 200 and login.json()['code'] == 0:
            self.cookies = login.cookies
        else:
            raise Exception(f"login err: {login.text}")
        return

    def start(self):
        body = copy.deepcopy(self.base_body)
        body["chunkCount"] = 1
        start = requests.post(f"{self.nari_url}/dfs-ui/dfs/v2/file/upload/chunk/start",
                              json=body,
                              headers={
                                  "Content-Type": "application/json",
                                  "User-Agent": self.user_agent
                              },
                              cookies=self.cookies)
        if start.status_code == 200 and start.json()['code'] == 0:
            self.symbolic_link_id = start.json()['result']['data']['symbolicLinkId']
            self.file_id = start.json()['result']['data']['fileId']
            self.status = start.json()['result']['status']
            print("start", start.json())
        else:
            raise Exception(f"start err: {start.text}")

    def upload(self):
        if not self.file_id or not self.status:
            raise Exception(f"upload err: fileId-{self.file_id} status-{self.status}")
        if self.status != "chunks":
            return
        # 随机16位
        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        data = MultipartEncoder(fields={
            "appId": "YUNPAN",
            "storeLocation": "ALL",
            "docLevel": "2",
            "id": self.base_body['id'],
            "name": self.base_body['name'],
            "relativePath": None,
            "lastModified": str(self.base_body['lastModified']),
            "fileId": str(self.file_id),
            "chunkCount": "1",
            "index": "0",
            "chunk": ("blob", open(self.file, 'rb'), 'application/octet-stream'),
            "md5": self.base_body['md5'],
        }, boundary=boundary)
        response = requests.post(f"{self.nari_url}/dfs-ui/dfs/v2/file/upload/chunk/upload",
                                 data=data,
                                 headers={
                                     "Content-Type": data.content_type,
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200 and response.json()['code'] == 0:
            print("upload", response.json())
        else:
            raise Exception(f"upload err: {response.text}")

    def upload_submit(self):
        if not self.symbolic_link_id:
            raise Exception(f"uploadSubmit err: symbolicLinkId-{self.symbolic_link_id}")
        body = copy.deepcopy(self.base_body)
        del body['mimeType']
        body['symbolicLinkId'] = self.symbolic_link_id
        response = requests.post(f"{self.nari_url}/ydyy-clouddisk-ui/ui/myFile/uploadSubmit",
                                 json=body,
                                 headers={
                                     "Content-Type": "application/json",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200 and response.json()['code'] == 0:
            print("uploadSubmit", response.json())
        else:
            raise Exception(f"uploadSubmit err: {response.text}")

    def finish(self):
        if not self.file_id:
            raise Exception(f"finish err: fileId-{self.file_id}")
        if self.status != "chunks":
            return
        body = copy.deepcopy(self.base_body)
        del body['mimeType']
        del body['fileSize']
        del body['md5']
        body['fileId'] = self.file_id
        body['chunkCount'] = 1
        response = requests.post(f"{self.nari_url}/dfs-ui/dfs/v2/file/upload/chunk/finish",
                                 json=body,
                                 headers={
                                     "Content-Type": "application/json",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200 and response.json()['code'] == 0:
            print("finish", response.json())
        else:
            raise Exception(f"finish err: {response.text}")

    def upload_num(self):
        response = requests.post(f"{self.nari_url}/ydyy-clouddisk-ui/uds/uploadNum",
                                 headers={
                                     "Content-Type": "application/x-www-form-urlencoded",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200:
            print("uploadNum", response.text)
        else:
            raise Exception(f"uploadNum err: {response.text}")

    def get_doc_count_by_name_and_format_and_parent_id(self):
        def request(body, n=None):
            n = n if n else ""
            response = requests.post(
                f"{self.nari_url}/ydyy-clouddisk-ui/ui/myFile/getDocCountByNameAndFormatAndParentId{n}",
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": self.user_agent
                },
                cookies=self.cookies)
            if response.status_code == 200:
                print(response.text)
                return response.json()
            else:
                raise Exception(f"getDocCountByNameAndFormatAndParentId err: {response.text}")

        def get_name(prefix: str, suffix: str, n: int):
            return f"{prefix}({n + 1}).{suffix}"

        fname, ext = self.base_body['fileName'].rsplit(".", 1)
        first = request({"fileName": self.base_body['fileName'], "parentId": "0"})
        if first['result'] != 0:
            second = request({"fileName1": fname, "fileFormat1": ext, "fileFormat": ext, "parentId": "0"}, 2)
            print({"fileName1": fname, "fileFormat1": ext, "fileFormat": ext, "parentId": "0"})
            if second['result'] == 0:
                self.base_body['fileName'] = get_name(fname, ext, 0)
            else:
                third = request({"fileName": fname, "fileName1": fname, "fileFormat1": ext, "fileFormat": ext,
                                 "parentId": "0"}, 3)
                self.base_body['fileName'] = get_name(fname, ext, int(third['result']))

    def create_document(self):
        if not self.symbolic_link_id:
            raise Exception(f"upload err: symbolicLinkId-{self.symbolic_link_id}")
        response = requests.post(f"{self.nari_url}/ydyy-clouddisk-ui/ui/doc/createDocument",
                                 json={"id": self.symbolic_link_id,
                                       "docName": self.base_body['fileName'],
                                       "isMyFile": 0,
                                       "docSize": self.base_body['fileSize'],
                                       "docLevel": "2",
                                       "folderId": "0",
                                       "folderName": "我的文档"},
                                 headers={
                                     "Content-Type": "application/json",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200 and response.json()['code'] == 0:
            print("createDocument", response.json())
        else:
            raise Exception(f"createDocument err: {response.text}")

    def run(self):
        self.get_body()
        self.start()
        self.upload()
        self.upload_submit()
        self.finish()
        self.upload_num()
        self.get_doc_count_by_name_and_format_and_parent_id()
        self.create_document()


if __name__ == '__main__':
    c = CloudDisk("d-nari.sgepri.sgcc.com.cn", "4611210148", "Lzw721..",
                  r"I:\Project\safety-quality-department\part4\需求.png")
    c.run()
