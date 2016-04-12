class Mail(object):
    """
    Mail.send('jinlingw@jumei.com', '测试而已', '是的只是测试')
    """
    url = 'http://email.jumeird.com/send?' 

    @classmethod
    def send(cls, to, subject, content):
        values = {'email_destinations': to, 'email_subject': subject, 'email_content': content}
        r = requests.post(cls.url, data=values)
        return r
