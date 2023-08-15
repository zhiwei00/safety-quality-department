import array
import hashlib
import mimetypes
import string
from pathlib import Path
import random
import copy
import execjs
import requests


class CloudDisk:
    def __init__(self, nari_base: str, nari_user: str, nari_pwd: str, file: str):
        self.nari_url = f"https://{nari_base}"
        self.nari_user = nari_user
        self.nari_pwd = nari_pwd
        self.file = file
        self.base_body = self.get_body()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        self.cookies = None
        self.symbolic_link_id = None
        self.file_id = None
        self.status = None

    def spark_md5_hash(self, file_path):
        with open(file_path, "rb") as file:
            arraybuffer = bytearray(file.read())
        bytes_data = array.array("B", arraybuffer).tobytes()
        md5_hash = hashlib.md5(bytes_data).hexdigest()
        return md5_hash

    def get_body(self):
        mime_type, _ = mimetypes.guess_type(self.file)
        p_file = Path(self.file)
        return {"appId": "YUNPAN",
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
        with open(Path("js").joinpath(file), "r") as file:
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
        r = v_pwd + "," + rsa_parameter['requestId'] + "," + self.nari_pwd
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
            print(start.json())
        else:
            raise Exception(f"start err: {start.text}")

    def upload(self):
        if not self.file_id or not self.status:
            raise Exception(f"upload err: fileId-{self.file_id} status-{self.status}")
        if self.status != "chunks":
            return
        body = copy.deepcopy(self.base_body)
        del body['mimeType']
        del body['fileSize']
        del body['fileName']
        body["chunkCount"] = 1
        with open(self.file, "rb") as f:
            body["chunk"] = f.read()
        body['fileId'] = self.file_id
        body['index'] = 0
        response = requests.post(f"{self.nari_url}/dfs-ui/dfs/v2/file/upload/chunk/upload",
                                 files=body,
                                 headers={
                                     "Content-Type": "multipart/form-data;boundary=----WebKitFormBoundaryURZ1YFAAcSBUNHKK",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200 and response.json()['code'] == 0:
            print(response.json())
        else:
            raise Exception(f"upload err: {response.text}")

    def upload_submit(self):
        if not self.symbolic_link_id:
            raise Exception(f"upload err: symbolicLinkId-{self.symbolic_link_id}")
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
            print(response.json())
        else:
            raise Exception(f"upload err: {response.text}")

    def finish(self):
        if not self.file_id:
            raise Exception(f"upload err: fileId-{self.file_id}")
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
            print(response.json())
        else:
            raise Exception(f"upload err: {response.text}")

    def upload_num(self):
        response = requests.post(f"{self.nari_url}/ydyy-clouddisk-ui/uds/uploadNum",
                                 headers={
                                     "Content-Type": "application/x-www-form-urlencoded",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200:
            print(response.text)
        else:
            raise Exception(f"upload err: {response.text}")

    def get_doc_count_by_name_and_format_and_parent_id(self):
        response = requests.post(f"{self.nari_url}/ydyy-clouddisk-ui/ui/myFile/getDocCountByNameAndFormatAndParentId",
                                 json={"fileName": self.base_body['fileName'], "parentId": "0"},
                                 headers={
                                     "Content-Type": "application/json",
                                     "User-Agent": self.user_agent
                                 },
                                 cookies=self.cookies)
        if response.status_code == 200:
            print(response.text)
        else:
            raise Exception(f"upload err: {response.text}")

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
            print(response.json())
        else:
            raise Exception(f"upload err: {response.text}")

    def main(self):
        self.get_cookies()
        self.get_body()
        self.start()
        self.upload()
        self.upload_submit()
        self.finish()
        self.upload_num()
        self.get_doc_count_by_name_and_format_and_parent_id()
        self.create_document()


if __name__ == '__main__':
    c = CloudDisk("d-nari.sgepri.sgcc.com.cn", "4611210148", "Lzw721..", r"I:\Project\safety-quality-department\part4\需求.png")
    c.main()
