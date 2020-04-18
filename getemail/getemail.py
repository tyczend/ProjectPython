import imaplib
import email
import datetime
import schedule
import time
import paramiko
import configparser
import imap_tools.imap_utf7 as imap_utf7

# 스케줄러 상태
gb_login_status = True
gb_count = 0


# 인코딩된 데이터 획득
def get_encoding_msg(txt):
    data, encode = find_encoding_info(txt)

    try:
        if encode is None:
            msg = str(data)
        else:
            msg = str(data, encode)

        # 필터처리
        msg = msg.replace('"', '')

    except Exception as ex:
        msg = None
        print('[Encoding] :', ex)

    # print('encoding:', encode, msg)

    return msg


# 문자열의 인코딩 정보 추출 후, 문자열, 인코딩 얻기
def find_encoding_info(txt):
    info = email.header.decode_header(txt)
    s, encoding = info[0]
    return s, encoding


# 메일을 생성 (imap4)
def create_email_imap(imap_srv, imap_port, imap_id, imap_pw, mail_box, get_count, output_file):

    # define mail config
    config_email = dict()
    config_email['imap_srv'] = imap_srv
    config_email['imap_port'] = imap_port
    config_email['id'] = imap_id
    config_email['pw'] = imap_pw
    config_email['mail_box'] = mail_box
    config_email['get_count'] = get_count
    config_email['output_file'] = output_file

    try:
        # imap server 접속
        imapsrv = config_email['imap_srv']
        imapserver = imaplib.IMAP4_SSL(imapsrv, int(config_email['imap_port']))
        imapserver.login(config_email['id'], config_email['pw'])

        # mail box 폴더 목록 얻기
        root_folders = []
        res, mail_boxs = imapserver.list('""', '*')
        for mbox in mail_boxs:
            flags, separator, name = parse_mailbox(bytes.decode(mbox))
            # print(f'{name_decodeing} {name}    : [Flags = {flags}; Separator = {separator}')

            # imap utf7 타입으로 디코딩
            name_decodeing = imap_utf7.decode(name.encode())
            if len(name.split('/')) > 1:
                continue
            else:
                root_folders.append(name_decodeing)

        # 메일 박스 리스트 출력 확인
        # print(root_folders)

        # 메일 박스 확인
        if config_email['mail_box'] == '전체메일':
            selected_mail_box = 'INBOX'
        else:
            if config_email['mail_box'] not in root_folders:
                print(f"[EMAIL] \"{config_email['mail_box']}\" 메일함이 없습니다.")
                return False
            else:
                selected_mail_box = imap_utf7.encode(config_email['mail_box'])

        # 획득 할 메일 폴더 설정
        imapserver.select(selected_mail_box)

        # 메일 리스트 획득
        res, unseen_data = imapserver.search(None, 'ALL')
        ids = unseen_data[0]
        id_list = ids.split()
        email_count = -int(config_email['get_count'])
        latest_email_id = id_list[email_count:]
        latest_email_id.reverse()

    except Exception as ex:
        print('[메일 서버 오류] : ', ex)
        return True

    # 이메일 수량 확인
    if len(latest_email_id) == 0:
        print('수신된 메일이 없습니다.')
        return True

    # 메일 리스트 리스트
    email_list = ""

    # 템플릿 로드
    f = open("./template_table.html", 'r', encoding="utf-8")
    template_table_html = f.read()
    f.close()

    # 카운트
    cnt = 1

    # 메일리스트를 받아서 내용을 파일로 저장하는 함수
    for each_mail in latest_email_id:
        # 메일 raw 데이터 수신 처리
        # fetch the email body (RFC822) for the given ID
        result, data = imapserver.fetch(each_mail, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # 메일의 key 값 출력
        # print(list(email_message.keys()))
        # print(email_message['Received'])

        # 메일 데이터
        email_decoding = dict()

        # 수신자 데이터 파싱
        try:
            to_data = email_message['To'].replace('"', '')
            to_data = to_data.split("<")
            to_data[0] = to_data[0].strip()

            if len(to_data) > 1:
                to_data[1] = to_data[1].replace(">", "")
            else:
                to_data.append("")
        except Exception as ex:
            print('[EMAIL] :', ex, 'email data[To]', email_message['To'])
            to_data = ['', '']

        # 발신자 데이터 파싱
        try:
            from_data = email_message['From'].replace('"', '')
            from_data = from_data.split("<")
            from_data[0] = from_data[0].strip()

            if len(from_data) > 1:
                from_data[1] = from_data[1].replace(">", "")
            else:
                from_data.append("")
        except Exception as ex:
            print('[EMAIL] :', ex, 'email data[From] > ', email_message['From'])
            from_data = ['', '']

        # print('email To:',  email_message['To'])
        # print('email to data0:', to_data[0], 'email to data1:', to_data[1])
        # print('')
        # print('email from:',  email_message['From'])
        # print('email from data0:', from_data[0], 'email from data1:', from_data[1])
        # print('email Date', email_message['Date'])
        # print(from_data[0])
        # print(from_data[1])

        # 메일 데이터 재정의
        email_decoding['FromName'] = get_encoding_msg(from_data[0])
        email_decoding['FromEmail'] = from_data[1]
        email_decoding['ToName'] = get_encoding_msg(to_data[0])
        email_decoding['ToEmail'] = to_data[1]
        email_decoding['Subject'] = get_encoding_msg(email_message['Subject'])
        email_decoding['Date'] = email_message['Date']

        # print('ToName:', email_decoding['ToName'])
        # print('Subject:', email_decoding['Subject'])
        # print('Date:', email_decoding['Date'])
        # print('=============================')

        # 시간 데이터 구조 문자열 배열화
        if email_decoding['Date'] is not None:
            date_type1 = email_message['Date'].split(" ")
            date_type2 = [s.replace(',', '') for s in date_type1]
            date_myformat = f'{date_type2[1]} {date_type2[2]} {date_type2[3]} {date_type2[4]}'

            # 시간 포멧 데이터 변환
            try:
                email_decoding['Date'] = f"{datetime.datetime.strptime(date_myformat, '%d %b %Y %H:%M:%S')}"
            except Exception as ex:
                email_decoding['Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print('[EMAIL] :', ex)
        else:
            email_decoding['Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 출력 테스트
        # email_data = email_decoding['Date'] + " / "
        # email_data = email_data + email_decoding['FromName'] + email_decoding['FromEmail'] + " / "
        # email_data = email_data + email_decoding['Subject']
        # print(email_data)
        # print(email_decoding['Date'])

        # HTML 변환
        data_table = ''
        if email_decoding['Date'] is not None and \
                email_decoding['FromName'] is not None and \
                email_decoding['FromEmail'] is not None and \
                email_decoding['Subject'] is not None:
            data_table = template_table_html
            data_table = data_table.replace("##No##", str(cnt))
            data_table = data_table.replace("##Date##", email_decoding['Date'])
            data_table = data_table.replace("##FromName##", email_decoding['FromName'])
            data_table = data_table.replace("##FromEmail##", email_decoding['FromEmail'])
            data_table = data_table.replace("##Subject##", email_decoding['Subject'])
            # print(data_table)

        # 메일 리스트 추가
        email_list = email_list + data_table + "\n"

        # 카운트
        cnt = cnt + 1

    # email HTML 생성
    # read template
    f = open("./template_main.html", 'r', encoding="utf-8")
    data_main = f.read()
    f.close()

    # 메인 HTML 적용
    data_main = data_main.replace("##table_list##", email_list)

    # 최종 결과 출력
    # print(data_main)

    # 파일 저장
    f = open(config_email['output_file'], "w", encoding="utf-8")
    f.write(data_main)
    f.close()

    # 메일 연결 종료
    imapserver.close()
    imapserver.logout()

    return True


def parse_mailbox(data):
    flags, b, c = data.partition(' ')
    separator, b, name = c.partition(' ')
    return flags, separator.replace('"', ''), name.replace('"', '')


"""
def subdirectory(folders):
    #For directories 'Deleted Items', 'Sent Items', etc. with whitespaces,
    #the name of the directory needs to be passed with double quotes, hence '"' + name + '"'
    # obj를 imap 서버를 입력으로 받아야함

    test, folders = obj.list('""', '"' + name + '/*"')
    if(folders is not None):
        print('Subdirectory exists') # you can also call parse_mailbox to find the name of sub-directory
"""


def upload_ftp(ftp_ip, ftp_port, ftp_id, ftp_pw, local_file_name, upload_file_name):

    try:
        # Open a transport
        transport = paramiko.Transport((ftp_ip, ftp_port))

        # Auth
        transport.connect(username=ftp_id, password=ftp_pw)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # upload
        print(local_file_name, upload_file_name)
        sftp.put(local_file_name, upload_file_name)

        # Close
        sftp.close()
        transport.close()

    except Exception as ex:
        print('[FTP] :', ex)

    # 일반 FTP
    # ftp = ftplib.FTP()
    # ftp.connect(ftp_ip, ftp_port)
    # ftp.login(ftp_id, ftp_pw)
    # ftp.cwd(upload_dir)
    # os.chdir("./")
    # fd = open(target_file_name, 'rb')
    # ftp.storbinary('STOR ' + upload_file_name, fd)
    # fd.close()
    # ftp.close()


def load_conf(type_name):
    # 설정 로드
    config_data = configparser.ConfigParser()
    config_data.read('./getemail.conf', encoding='utf-8')
    return config_data[type_name]


def job():
    # 설정 로드
    config_email = load_conf('EMAIL')
    config_ftp = load_conf('FTP')

    # 전역 변수 정의
    global gb_count
    global gb_login_status
    gb_count = gb_count + 1

    # 스케줄러 카운트
    print(f'[{datetime.datetime.today()}] 생성횟수 : {gb_count}', sep='')

    # 메일 박스 목록 생성
    mail_box_list = config_email['mail_box'].split(',')
    cnt = 0
    for mail_box in mail_box_list:
        # 카운트
        cnt = cnt + 1

        # 파일명 정의
        output_file_path = f"{config_email['output_folder']}{config_email['output_file']}_{cnt}.html"

        # 메일 조회
        gb_login_status = create_email_imap(config_email['imap_srv'],
                                            config_email['imap_port'],
                                            config_email['id'],
                                            config_email['pw'],
                                            mail_box,
                                            config_email['get_count'],
                                            output_file_path)

        # email 파일 복사
        if int(config_ftp['use']) == 1:
            # ftp 설정 로드
            ftp_ip = config_ftp['ip']
            ftp_port = int(config_ftp['port'])
            ftp_id = config_ftp['id']
            ftp_pw = config_ftp['pw']

            # 파일명 정의
            upload_file_path = f"{config_ftp['upload_folder']}{config_email['output_file']}_{cnt}.html"
            upload_ftp(ftp_ip, ftp_port, ftp_id, ftp_pw, output_file_path, upload_file_path)


if __name__ == '__main__':
    # 시작
    print("이메일 목록 생성을 시작합니다.")
    job()

    # 설정 로드
    config = load_conf('SCHEDULE')

    # 스케줄러 등록
    if config['unit'] == 's':
        schedule.every(int(config['interval'])).seconds.do(job)
    elif config['unit'] == 'm':
        schedule.every(int(config['interval'])).minutes.do(job)
    elif config['unit'] == 'h':
        schedule.every(int(config['interval'])).hours.do(job)

    # 스케줄링
    while True:
        schedule.run_pending()
        time.sleep(1)

        # 종료 처리
        if not gb_login_status:
            print("오류로 인하여 스케줄링을 종료 합니다.")
            break
