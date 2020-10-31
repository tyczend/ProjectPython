import os

# 경로
CFG_PATH_DATA = 'c:\label_test\data'
CFG_PATH_IMAGES = 'images'

# coco 이미지 목록 생성
def create_image_list(label_file_name ,path_data, path_images):

    # 이미지 리스트 가져오기
    image_path = os.path.join(path_data, path_images)
    file_list = os.listdir(image_path)

    # 저장할 이미지 리스트 파일 경로
    image_list_file = os.path.join(path_data, label_file_name)

    # 기존 파일 목록 삭제
    os.remove(image_list_file)

    # 파일 목록
    for file_name in file_list:
        file_name = os.path.join('.', path_images, file_name)
        print(file_name)

        # 파일쓰기
        with open(image_list_file, 'a') as f:
            f.write(file_name+'\n')


if __name__ == '__main__':
    create_image_list("train.txt", CFG_PATH_DATA, CFG_PATH_IMAGES)
    create_image_list("test.txt", CFG_PATH_DATA, CFG_PATH_IMAGES)
