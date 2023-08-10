import os
from pathlib import Path
import requests
import dotenv


class Part4:
    def __init__(self, work_dir: str, output_dir: str, ocr_url: str):
        self.work_dir: Path = Path(work_dir)
        self.output_dir: Path = Path(output_dir)
        self.root_path: Path = Path(__file__).parent
        # dotenv.load_dotenv(self.root_path.joinpath("env"))
        self.ocr_url = ocr_url

    def get_pdf(self):
        pass

    def get_ocr_data(self, pdf: dict):
        pdf['text'] = []
        try:
            ocr_url = f"http://{self.ocr_url}/ysocr/ocr"
            response = requests.post(ocr_url, files={"file": open(os.path.join(self.pdf_root_path, pdf['path']), "rb"),
                                                     "active_desalt_signet": True})
            try:
                response_json = response.json()
                print(response_json)
            except:
                return False, f"{pdf['name']}识别失败：{response.text}"
            pdf_text = []
            for index, row in enumerate(response_json["img_data_list"]):
                text = ''
                text_list = [i['text_string'] for i in row['text_info']]
                split_text_list = text_list
                if len(text_list) > 2 and index > 2:
                    split_text_list = text_list[2:]
                for i in split_text_list:
                    text += str(i).replace(' ', '')
                pdf_text.append(text)
            pdf['text'] = pdf_text
            return True, pdf
        except Exception as ex:
            print(ex)
            return False, pdf


if __name__ == '__main__':
    pass
