import sys
sys.path.insert(0, 'email_extraction')
sys.path.insert(0, 'sentiment')

import email_finder
import email_text_functions as etf

def run_remove_mail(mail_text):
    '''
    :param mail_text:
    :return:
    '''
    assert type(mail_text) == str
    return etf.get_regex_rejection(mail_text)

def run_email_analysis():
    '''
    :return:
    '''
    ecs = email_finder.EmailConnectionService()
    ecs.read_mails()
    mails = ecs.mails
    print(mails)

    email_dict = {}

    for dets in mails:
        remove = run_remove_mail(str(dets[2]))
        if dets[0] in email_dict:
            remove = remove or email_dict[dets[0]]['remove_mail']
        email_dict.update({dets[0]:{'remove_mail':remove}})
    print(email_dict)

if __name__ == '__main__':
    run_email_analysis()