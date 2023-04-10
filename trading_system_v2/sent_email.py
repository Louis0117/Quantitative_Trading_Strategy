#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:04:12 2023

@author: welcome870117
"""

import smtplib


# system sent mail to user 
def sent_mail(system_mail_address, app_pwd, client_mail_address , msg):
    '''

    Parameters
    ----------
    system_mail_address : str
        the trading system mail address        
    app_pwd : str
        the trading system mail pwd       
    client_mail_address : str
        client mail address
    msg : str
        system notification letter content

    Returns
    -------
    None.

    '''
    
    # create a smtp object, use TLS security credentials
    smtp=smtplib.SMTP('smtp.gmail.com', 587)
    # Register identity with server
    smtp.ehlo()
    # Call startttles() to start TLS encryption mode
    smtp.starttls()
    # login
    smtp.login(system_mail_address, app_pwd)
    # set senting mail address
    from_addr = system_mail_address
    to_addr = client_mail_address
    # sent mail
    status=smtp.sendmail(from_addr, to_addr, msg)
    if status=={}:
        print("Email sent successfully!")
    else:
        print("Mail delivery failed.....")
    smtp.quit()