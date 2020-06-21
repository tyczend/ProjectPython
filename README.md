# ProjectPython
파이썬 모듈 프로젝트 저장소에 오신것을 환경합니다. 

모든 Python 코드는 학습 목적 및 공유를 위해 제작되었습니다.

감사합니다.


## GuideLines
각 폴더는 독립적으로 동작이 가능한 모듈로 구성되어 있습니다.


- ### getemail

  IMAP4을 이용하여 메일 제목을 HTML 파일로 생성하는 모듈입니다.<br>
  HTML 템플릿, 스케줄링, FTP 업로드, 메일함 별 파일 저장 기능을 가지고 있습니다.<br>
  
- #### 파일 설명
  - getmail.py : 실행 코드
  - getmail.conf : 설정 파일
  - template_main.html : HTML 템플릿 - 메인
  - template_table.html : HTML 템플릿 - 테이블
    
- #### HTML 템플릿의 tag 정의
    | HTML tag          | 설명               |
    | :---------------- | :----------------: |
    | \##No##           | 번호               |
    | \##Date##         | 수신일자           |
    | \##FromName##     | 발신자 이름        |
    | \##FromEmail##    | 발신자 메일        |
    | \##Subject##      | 메일 제목          |

      









