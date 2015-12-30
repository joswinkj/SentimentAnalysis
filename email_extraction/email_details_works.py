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

from email_details import username, password

# from utils.crawl.bs_crawl import BeautifulsoupCrawl

#http://www.email-validator.net/ upto 100 emails
#http://www.briteverify.com/ - 0.01$ per email
#https://www.emailverifierapp.com/ starting $35/month
#http://www.inteligator.com/home/index.php?tab=11
#https://www.google.com/settings/security/lesssecureapps : turn off
#enable imap https://support.google.com/mail/answer/77695?hl=en

def check_emails_from_gmailid(emails):
    '''
    :param emails:
    :return:
    '''
    #sending mails
    start_time = datetime.datetime.now()
    #all the mails together
    # fromaddr = 'joswin.ideas2it@gmail.com'
    # toaddrs = emails
    # subject = 'Test Spam Message'
    # text = 'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X. This is a test of the email system.\
    #  This is not a real spam message, but rather one that is trying to purposely get into the spam folder of another \
    #  account. This is so that I can ensure that my Gmail filters are setup correctly.'
    # msg = "\r\n".join([
    #           "From: "+fromaddr,
    #           "To: "+", ".join(toaddrs),
    #           "Subject: "+subject,
    #           "",
    #           text
    #           ])
    # username = 'joswin.ideas2it@gmail.com'
    # password = 'D!vyaJ0se'
    # server = smtplib.SMTP('smtp.gmail.com:587')
    # server.ehlo()
    # server.starttls()
    # server.login(username,password)
    # server.sendmail(fromaddr, toaddrs, msg)
    # server.quit()

    #sending mails separately for each id
    toaddrs = emails
    subject = 'Test Spam Message'
    text = 'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X. This is a test of the email system.\
     This is not a real spam message, but rather one that is trying to purposely get into the spam folder of another \
     account. This is so that I can ensure that my Gmail filters are setup correctly.'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    for mail_id in toaddrs:
        msg = "\r\n".join([
              "From: "+username,
              "To: "+mail_id,
              "Subject: "+subject,
              "",
              text
              ])
        server.sendmail(username, mail_id, msg)
    server.quit()
    print('completed sending mails in {0} seconds'.format(str((datetime.datetime.now()-start_time).seconds)))
    # #wait for 45 seconds
    # print('waiting for x seconds')
    # time.sleep(60)
    # print('executing after wait')

    #looking at inbox
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    mail.list()
    mail.select("Unrecieved") # connect to inbox.
    from_date = (datetime.date.today()- datetime.timedelta(1)).strftime("%d-%b-%Y")
    actual_addresses = toaddrs.copy()
    start_time = datetime.datetime.now()
    while len(actual_addresses) > 1 and (datetime.datetime.now()-start_time).seconds < 45:
        # print(len(actual_addresses))
        # time.sleep(3)
        try:
            result, data = mail.uid('search', '(FROM "mailer-daemon@googlemail.com")', '(SENTSINCE {date})'.format(date=from_date))
            # uids = data[0].split()
            uids = data[0].decode('ascii').split()
            #fetching uids one by one
            # for ind in range(len(uids)):
            #     try:
            #         email_uid = uids[ind]
            #         result_1, data_1 = mail.uid('fetch', email_uid, '(RFC822)')
            #         raw_email = data_1[0][1]
            #         email_message = email.message_from_string(raw_email.decode('ascii'))
            #         if email.utils.parseaddr(email_message['Subject']) == ('Failure', 'Delivery') :
            #             if email.utils.parseaddr(email_message['X-Failed-Recipients'])[1] in actual_addresses:
            #                 actual_addresses.remove(email.utils.parseaddr(email_message['X-Failed-Recipients'])[1])
            #     except:
            #         continue

            #fetching all uids togother
            fetch_ids = ','.join([i for i in reversed(uids)][0:len(toaddrs)*2])
            result_all, data_all = mail.uid('fetch', fetch_ids, '(RFC822.HEADER BODY.PEEK[1])')
            for ind in range(int(len(data_all)/3)):
                if len(actual_addresses) <= 1:
                    break
                raw_email = data_all[ind*3][1]+data_all[ind*3+1][1]
                email_message = email.message_from_string(raw_email.decode('ascii'))
                if email.utils.parseaddr(email_message['Subject']) == ('Failure', 'Delivery') :
                    if email.utils.parseaddr(email_message['X-Failed-Recipients'])[1] in actual_addresses:
                        actual_addresses.remove(email.utils.parseaddr(email_message['X-Failed-Recipients'])[1])
            # print('yielding')
            # yield str(actual_addresses)
        except Exception as inst:
            print(inst)
            continue
    mail.logout()
    print('completed retrieving inbox in {0} seconds'.format(str((datetime.datetime.now()-start_time).seconds)))
    return actual_addresses


class EmailFinderService:
    def __init__(self,separators = ['.','','_']):
        self.separators = separators
        self.finder_link = 'https://tools.verifyemailaddress.io/'

    def find_combinations(self,first_name,*second_names):
        '''
        :param first_name:
        :param second_names:
        :return:
        '''
        if not second_names: #for only first name, give name and first letter as possibilities
            return [first_name]
        else:
            name_pos = [first_name]+list(second_names)
            # name_pos_first = [i[0] for i in name_pos]
            possible_combinations = []
            for ind in range(len(name_pos)):
                for poss in itertools.permutations(name_pos,ind+1):
                    for sep in self.separators:
                        possible_combinations.append(sep.join(poss))
                        if len(poss) > 1:
                            for ind1 in range(len(poss)):
                                for poss1 in itertools.permutations(poss[1:],ind1+1):
                                    poss1_first_letter = [i[0] for i in poss1]
                                    possible_combinations.append(poss[0]+sep+sep.join(poss1_first_letter))
                                    possible_combinations.append(sep.join(poss1_first_letter)+sep+poss[0])
            return list(set(possible_combinations))

    # def _test_emails(self):
    #     '''
    #     :return:
    #     '''
        ##following part for using threads..not needed
        # def test_fun(q):
        #     while True:
        #         mailids = q.get()
        #         self.good_urls += check_emails_from_gmailid(mailids)
        #         q.task_done()
        #
        # q = Queue(maxsize=0)
        # num_threads = 10
        # for i in range(num_threads):
        #     worker = Thread(target=test_fun, args=(q,))
        #     worker.setDaemon(True)
        #     worker.start()
        # # for mail in self.poss_emails:
        # #     q.put(mail)
        # q.put(self.poss_emails)
        # q.join()


    def find_emails_single(self,domain,first_name,*args):
        '''
        :param domain:
        :param first_name:
        :param last_name:
        :return:
        '''
        # self.good_urls = []
        combs = self.find_combinations(first_name,*args)
        poss_emails = [i+'@'+domain for i in combs]
        # self._test_emails()
        # return self.good_urls
        # for emails_list in check_emails_from_gmailid(poss_emails):
            # yield emails_list
        return check_emails_from_gmailid(poss_emails)

    def find_emails_multiple(self,domain,list_of_names):
        '''
        :param list_of_names: [['first','middle','last'],['first2','last2']]
        :return:
        '''
        assert type(list_of_names) == list
        # good_urls = []
        poss_emails = []
        for comb in list_of_names:
            assert type(comb) == list
            combs = self.find_combinations(*comb)
            poss_emails += [i+'@'+domain for i in combs]
        for emails_list in check_emails_from_gmailid(poss_emails):
            yield emails_list


