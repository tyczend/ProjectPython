import cv2

# 얼굴 인식 캐스케이드 파일 읽는다
detector = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')

# create an instance of the Facial landmark Detector with the model
landmark_detector = cv2.face.createFacemarkLBF()
landmark_detector.loadModel("lbfmodel.yaml")

while True:
    cap = cv2.VideoCapture('http://192.168.219.114/capture')
    ret, frame = cap.read()

    if ret is True:
        # frame_resize = cv2.resize(frame, dsize=(0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces using the haarcascade classifier on the "grayscale image"
        faces = detector.detectMultiScale(gray)

        # 인식된 얼굴 갯수를 출력
        print("Faces:", len(faces))

        # 인식된 얼굴에 사각형을 출력한다
        for (x, y, w, h) in faces:
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Detect landmarks on "image_gray"
            _, landmarks = landmark_detector.fit(gray, faces)

            for landmark in landmarks:
                for x, y in landmark[0]:
                    # display landmarks on "image_cropped"
                    # with white colour in BGR and thickness 1
                    cv2.circle(frame, (x, y), 1, (255, 255, 255), 1)

        cv2.imshow('Video', frame)
    cv2.waitKey(2)
    # if cv2.waitKey(1) == 27:
    #   exit(0)
