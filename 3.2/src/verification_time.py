# -*- coding: utf-8 -*-
import datetime
import time
import ntplib
import requests
# from PyQt5.QtWidgets import QMessageBox
# from win32gui import MessageBox


class VerificationTime:
    @staticmethod
    def get_beijin_time():
        try:
            url = 'https://beijing-time.org/'
            request_result = requests.get(url=url)
            if request_result.status_code == 200:
                headers = request_result.headers
                net_date = headers.get("date")
                gmt_time = time.strptime(net_date[5:25], "%d %b %Y %H:%M:%S")
                bj_timestamp = int(time.mktime(gmt_time) + 8 * 60 * 60)
                return datetime.datetime.fromtimestamp(bj_timestamp)
        except Exception as exc:
            return None

    @staticmethod
    def get_ntp_time():
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        return datetime.datetime.fromtimestamp(response.tx_time)

    @classmethod
    def verification(cls, expiration_time: str):
        try:
            now_time = cls.get_beijin_time()
            if not now_time:
                now_time = cls.get_ntp_time()
        except Exception as e:
            now_time = datetime.datetime.now()
        if now_time < datetime.datetime.strptime(expiration_time, '%Y-%m-%d %H:%M:%S'):
            return True
        else:
            return False

# if __name__ == '__main__':
#     msg_box = QMessageBox(QMessageBox.Information, '标题', '我很喜欢python')
#     msg_box.exec_()
#     VerificationTime.verification()
