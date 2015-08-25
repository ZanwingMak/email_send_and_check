#coding:utf-8

import msvcrt

def pwd_input():
        chars = []
        while True:
            try:
                newChar = msvcrt.getch().decode(encoding="utf-8")
            except:
                print
                print u"你很可能不是在cmd命令行下运行，密码输入将不能隐藏:",
                return raw_input()
            if newChar in '\r\n': # 如果是换行，则输入结束
                 print
                 break
            elif newChar == '\b': # 如果是退格，则删除密码末尾一位并且删除一个星号
                 if chars:
                     del chars[-1]
                     msvcrt.putch('\b'.encode(encoding='utf-8')) # 光标回退一格
                     msvcrt.putch( ' '.encode(encoding='utf-8')) # 输出一个空格覆盖原来的星号
                     msvcrt.putch('\b'.encode(encoding='utf-8')) # 光标回退一格准备接受新的输入
            else:
                chars.append(newChar)
                msvcrt.putch('*'.encode(encoding='utf-8')) # 显示为星号
        return (''.join(chars) )

def check_email(): #查看邮件也可以用IMAP服务来实现，这里用POP3 =。=
    import poplib
    import email
    from email.parser import Parser
    from email.header import decode_header
    from email.utils import parseaddr
    def guess_charset(msg):
        # 先从msg对象获取编码:
        charset = msg.get_charset()
        # 如果获取不到，再从Content-Type字段获取:
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    #邮件的Subject或者Email中包含的名字都是经过编码后的str，要正常显示，就必须decode
    def decode_str(s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    #这个Message对象本身可能是一个MIMEMultipart对象，即包含嵌套的其他MIMEBase对象，嵌套可能还不止一层。
    #所以我们要递归地打印出Message对象的层次结构：
    # indent用于缩进显示:
    def print_info(msg, indent=0):
        if indent == 0:
            # 邮件的From, To, Subject存在于根对象上:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    # 需要解码Subject字符串:
                    if header=='Subject':
                        value = decode_str(value)
                    # 需要解码Email地址:
                    else:
                        hdr, addr = parseaddr(value)
                        name = decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                if header == 'From':
                    print(u'%s发件人：%s' % ('  ' * indent, value))
                elif header == 'To':
                    print(u'%s收件人：%s' % ('  ' * indent, value))
                elif header == 'Subject':
                    print(u'%s主题：%s' % ('  ' * indent, value))

        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                print('%spart %s' % ('  ' * indent, n))
                print('%s--------------------' % ('  ' * indent))
                # 递归打印每一个子对象:
                print_info(part, indent + 1)
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        else:
            content_type = msg.get_content_type()
            if content_type=='text/plain' or content_type=='text/html':
                # 纯文本或HTML内容:
                content = msg.get_payload(decode=True)
                # 要检测文本编码:
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                print(u'%s正文: %s' % ('  ' * indent, content + '...'))
            # 不是文本,作为附件处理:
            else:
                print(u'%s附件: %s' % ('  ' * indent, content_type))

    # 输入邮件地址,密码和POP3服务器地址:
    print u'请输入邮箱地址：',
    email = raw_input().strip()
    print u'请输入密码：',
    password = pwd_input()

    mail_check = (email.split('@'))[-1].split('.')[0]
    pop_check = 'pop.%s.com' % mail_check
    print u'已检测到您使用的是%s邮箱,已为您自动填写POP服务器地址:[%s]\n是否需要修改?[y/n]' % (mail_check,pop_check),
    ifchange = raw_input()
    if ifchange == 'y' or ifchange == 'Y':
        print u'好的,请修改POP服务器地址'
        print u'请输入POP服务器地址：',
        pop_server = raw_input().strip()
    else:
        pop_server = pop_check

    print u'是否使用SSL加密传输方式?[y/n]',
    ifuserssl = raw_input()
    if ifuserssl == 'y' or ifuserssl == 'Y':
        print u'好的,正在使用SSL加密服务...'
    else:
        print u'好的,不使用SSL加密服务...'

    k = 0
    while True:
        try:
            # 连接到POP3服务器:
            if ifuserssl == 'y' or ifchange == 'Y':
                server = poplib.POP3_SSL(pop_server)
            else:
                server = poplib.POP3(pop_server)
            # 可以打开或关闭调试信息:
            #server.set_debuglevel(1)
            # 可选:打印POP3服务器的欢迎文字:
            #print(server.getwelcome())

            # 身份认证:
            print u'正在进行身份认证...'
            server.user(email)
            server.pass_(password)

            print u'正在获取邮箱信息...'
            # stat()返回邮件数量和占用空间:
            print(u'邮件数量: %s  占用空间: %s' % server.stat())

            # list()返回所有邮件的编号:
            resp, mails, octets = server.list()

            # 可以查看返回的列表类似['1 82923', '2 2184', ...]
            #print(mails)

            print u'正在获取最新一封邮件...'
            # 获取最新一封邮件, 注意索引号从1开始:
            resp, lines, octets = server.retr(len(mails))
            #index = len(mails)
            #resp,lines,octets = server.retr(index)

            # lines存储了邮件的原始文本的每一行,
            # 可以获得整个邮件的原始文本:
            #msg_content = '\r\n'.join(lines)#
            # 解析邮件:
            #msg = Parser().parsestr(msg_content)#
            msg = Parser().parsestr('\r\n'.join(lines))

            #用POP3获取邮件其实很简单，要获取所有邮件，只需要循环使用retr()把每一封邮件内容拿到即可。
            #真正麻烦的是把邮件的原始内容解析为可以阅读的邮件对象。

            # 打印邮件内容:
            print_info(msg)

            # 慎重:可以根据邮件索引号直接从服务器删除邮件:
            # server.dele(len(mails))

            # 关闭连接:
            server.quit()
            print u'读取成功...'
            print u'正在返回菜单...'
            break
        except:
            print u'获取失败...'
            k+=1
            if k != 4:
                print u'正在重试(第%s次)...' % str(k)
            else:
                print u'重试次数已达到3次,正在返回菜单...'
                break


def send_email():
    from email import encoders
    from email.header import Header
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart,MIMEBase
    from email.utils import parseaddr,formataddr
    import smtplib
    import os
    import mimetypes
    import easygui

    def format_address(s):
        name,address = parseaddr(s)
        return formataddr((Header(name,'utf-8').encode(),\
                           address.encode('utf-8') if isinstance(address,unicode) else address))

    ##登录
    #发件人
    print u'请输入发件人邮箱：',
    from_address = raw_input().strip()
    #密码
    print u'请输入密码：',
    password = pwd_input()
    #SMTP服务器
    mail_check = (from_address.split('@'))[-1].split('.')[0]
    smtp_check = 'smtp.%s.com' % mail_check
    print u'已检测到您使用的是%s邮箱,已为您自动填写SMTP服务器地址:[%s]\n是否需要修改?[y/n]' % (mail_check,smtp_check),
    ifchange = raw_input()
    if ifchange == 'y' or ifchange == 'Y':
        print u'好的,请修改SMTP服务器地址'
        print u'请输入SMTP服务器地址：',
        smtp_server = raw_input().strip()
    else:
        smtp_server = smtp_check
    print u'是否使用SSL加密传输方式?[y/n]',
    ifuserssl = raw_input()
    if ifuserssl == 'y' or ifchange == 'Y':
        print u'请输入SSL端口号：',
        smtp_port = raw_input().strip()
        print u'好的,正在使用SSL加密服务...'
    else:
        print u'好的,不使用SSL加密服务...'
    #收件人
    print u'请输入收件人邮箱：',
    to_address = raw_input().strip()

    ###
    #如果我们发送HTML邮件，收件人通过浏览器或者Outlook之类的软件是可以正常浏览邮件内容的，
    #但是，如果收件人使用的设备太古老，查看不了HTML邮件怎么办？
    #办法是在发送HTML的同时再附加一个纯文本，如果收件人无法查看HTML格式的邮件，就可以自动降级查看纯文本邮件。
    #利用MIMEMultipart就可以组合一个HTML和Plain，要注意指定subtype是alternative

    # 邮件对象:
    msg = MIMEMultipart('alternative') #如果不支持就会自动降级

    print u'请输入发件人昵称：',
    from_text = raw_input().decode('GBK') + u' <%s>' % from_address
    msg['From'] = format_address(from_text)

    print u'请输入收件人昵称：',
    to_text = raw_input().decode('GBK') + u' <%s>' % to_address
    msg['To'] = format_address(to_text)

    print u'请输入邮件主题：',
    subject_text = raw_input().decode('GBK')
    msg['Subject'] = Header(subject_text,'utf-8').encode()

    print u'您的邮件需要上传附件?(注意：文本插入图片需要上传图片附件,然后引用)[y/n]'
    iffujian = raw_input()
    if iffujian == 'y' or iffujian == 'Y':
        cid = 0
        filelist = []
        while True:
            print u'请选择要上传的附件'
            filepath = easygui.fileopenbox(msg=u"请选择要上传的附件",title=u"浏览",default=os.getcwd())
            filename = os.path.basename(filepath)

            from email.mime.application import MIMEApplication
            fujian = MIMEApplication(open(filepath,'rb').read())
            fujian.add_header('Content-Disposition', 'attachment', filename=filename.encode('gb2312'))
            fujian.add_header('Content-ID', '<%s>' % str(cid))
            msg.attach(fujian)

            filelist.append('[CID] '+str(cid)+'  -->  [FileName] '+filename)
            print u'您添加了[%s]附件'%filename
            print u'是否继续添加附件??[y/n]'
            ifgoon = raw_input()
            if ifgoon != 'y' and ifgoon != 'Y':
                break
            cid+=1
        print u'附件列表如下[请注意CID号!]：'
        for i in range(len(filelist)):
            print filelist[i]

    print u'=========================='
    print u'1.plain形式(普通文本形式)\n2.html形式(网页形式,老旧设备不兼容)\n3.两者都输入(自动兼容设备)'
    print u'=========================='
    print u'请选择邮件正文的发送形式(注意：如需插入图片请选择html形式)：'
    print u'插入图片的形式为 <img src="cid:CID号">\n[CID号]在上方的附件列表中可以看到(数字部分(从0开始~))'
    select = input()
    if select == 1:
        print u'请在下方输入正文：'
        print u'您目前输入的是plain形式：'
        text = raw_input().decode('GBK')
        msg.attach(MIMEText(text,'plain','utf-8'))
    if select == 2:
        print u'请在下方输入正文：'
        print u'您目前输入的是html形式：'
        print u'<html><body>您只需要编写这个地方</body></html>'
        html_text = raw_input().decode('GBK')
        msg.attach(MIMEText('<html><body>%s</body></html>'%html_text,'html','utf-8'))
    if select == 3:
        print u'请在下方输入正文：'
        print u'您目前先输入的是plain形式：'
        text = raw_input().decode('GBK')
        msg.attach(MIMEText(text,'plain','utf-8'))
        print u'您目前输入的是html形式：'
        print u'<html><body>您只需要编写这个地方</body></html>'
        html_text = raw_input().decode('GBK')
        msg.attach(MIMEText('<html><body>%s</body></html>'%html_text,'html','utf-8'))

    print u'正在发送邮件...'
    j = 0
    while True:
        try:
            if ifuserssl == 'y' or ifuserssl == 'Y':
                server = smtplib.SMTP(smtp_server,smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_server,25)
            server.set_debuglevel(1)
            server.login(from_address,password)
            server.sendmail(from_address,[to_address],msg.as_string())
            print u'发送成功...'
            server.quit()
            print u'正在返回菜单...'
            break
        except:
            print u'发送失败...'
            j+=1
            if j != 4:
                print u'正在重试(第%s次)...' % str(j)
            else:
                print u'重试次数已达到3次,正在返回菜单...'
                break

if __name__ == '__main__':
    while True:
        print u'============================================='
        print u'||   1.查看最新一封邮件 2.发送邮件 3.退出  ||'
        print u'============================================='
        print u'请选择：',
        select = raw_input()
        if select == '1':
            check_email()
        if select == '2':
            send_email()
        if select == '3':
            quit()
