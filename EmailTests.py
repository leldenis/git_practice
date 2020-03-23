# coding=utf-8
import re
import imaplib
import traceback
import sys
from time import sleep


class EmailTests(object):
    def __init__(self, login, password, server, port=993):
        self.port = port
        self.login = login
        self.password = password
        self.server = server
        self.connection = None

    def connect_to_server(self):
        self.connection = imaplib.IMAP4_SSL(self.server, self.port)
        self.connection.login(self.login, self.password)

    def fetch_email(self):
        self.connect_to_server()
        self.connection.list()
        self.connection.select("Inbox")  # connect to inbox.
        result, data = self.connection.search(None, 'UNSEEN')
        ids = data[0]  # data is a list.
        id_list = ids.split()  # ids is a space separated string
        try:
            latest_email_id = id_list[-1]  # get the latest
        except IndexError:
            sleep(5)
            latest_email_id = id_list[-1]
        result, data = self.connection.fetch(latest_email_id,
                                             "(RFC822)")  # fetch the email body (RFC822)             for the given ID
        return data

    def parse_email(self, url_chapter, lang=None):
        try:
            data = self.fetch_email()
            urls = re.findall('<a href="?\'?([^"\'>]*)',
                              data[0][1])
            if url_chapter == 'invoice' and lang == 'en':
                assert r'Invoice from the shop' in data[0][1]
            if url_chapter == 'invoice' and lang == 'ru':
                assert r'Счет от магазина' in data[0][1]
            for i in urls:
                if url_chapter in i:
                    return i
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise
        finally:
            self.delete_all_messages()

    def delete_all_messages(self):
        self.connect_to_server()
        self.connection.list()
        self.connection.select("Inbox")
        result, data = self.connection.search(None, 'ALL')
        for num in data[0].split():
            self.connection.store(num, '+FLAGS', '\\Deleted')
        self.connection.close()
        self.connection.logout()


# c = EmailTests('autotest@fondy.eu', 'Qs!q66W1A3R5t', 'imappro.zoho.com')
# c.delete_all_messages()
