"""
File : email_finder.py
Created On: 23-Sep-2015
Author: ideas2it
"""
import datetime
import email
import imaplib
import itertools
import smtplib
import time
from queue import Queue
from threading import Thread

from email_details import username, password,imap_server,inbox_folder


class EmailConnectionService(object):
    def __init__(self):
        self.connect()
        self.mails = []

    def connect(self):
        self.conn = imaplib.IMAP4_SSL(imap_server)
        self.conn.login(username, password)
        if inbox_folder is None:
            self.conn.select()
        else:
            self.conn.select(inbox_folder,readonly=1)

    def disconnect(self):
        self.conn.close()
        self.conn.logout()

    def reconnect(self):
        try:
            self.conn.check()
        except:
            self.connect()

    # def read_mails(self):
    #     try:
    #         result, data = self.conn.uid('search', None, '(UNSEEN)')
    #         # uids = data[0].split()
    #         uids = data[0].decode('ascii').split()
    #
    #         #fetching all uids together
    #         fetch_ids = ','.join([i for i in uids])
    #         result_all, data_all = self.conn.uid('fetch', fetch_ids, '(RFC822.HEADER BODY.PEEK[1])')
    #         for ind in range(int(len(data_all)/3)):
    #             raw_email = data_all[ind*3][1]+data_all[ind*3+1][1]
    #             email_message = email.message_from_string(raw_email.decode('ascii'))
    #             print(email_message)
    #         # print('yielding')
    #         # yield str(actual_addresses)
    #     except Exception as inst:
    #         print('Exception:',inst)


    def read_mails(self):
        self.reconnect()
        # n = 0
        (retcode, messages) = self.conn.search(None, '(UNSEEN)')
        unread_msg_nums = messages[0].split()
        if retcode == 'OK':
            try:
                for num in messages[0].split():
                    # n += 1
                    typ, data = self.conn.fetch(num,'(RFC822)')
                    # print(data)
                    for response_part in data:
                        if isinstance(response_part, tuple):
                            original = email.message_from_string(response_part[1].decode('ascii'))
                            # print('XXXX message from: XXXX',original['From'])
                            # print('XXXX subject XXXX',original['Subject'])
                            if original.get_content_maintype() == 'multipart': #If message is multi part we only want the text version of the body, this walks the message and gets the body.
                                for part in original.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True)
                                        # print('XXXX body XXXX',body)
                                        self.mails.append((original['From'],original['Subject'],body))
                                    else:
                                        continue
                    # typ, data = self.conn.store(num,'-FLAGS','\\Seen') ##not working

            except Exception as inst:
                print('Exception:',inst)
        # print('making read')
        for e_id in unread_msg_nums:
            # print(e_id)
            # self.conn.store(e_id, '+FLAGS', '\Seen')
            self.conn.store(e_id, '-FLAGS','\\Seen')
        # print(self.mails)
        self.disconnect()

if __name__== '__main__':
    ecs = EmailConnectionService()
    ecs.read_mails()
