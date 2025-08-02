import os
import shutil

def setup_project():
    """프로젝트 설정 및 이미지 파일 이동"""
    
    # 필요한 폴더 생성
    folders = ['templates', 'static', 'static/images']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ {folder} 폴더 생성 완료")
    
    # 이미지 파일 이동
    image_files = ['다리1.png', '다리2.png', '다리3.png', '다리4.png', '다리5.png', '사람.gif']
    
    for image_file in image_files:
        if os.path.exists(image_file):
            destination = os.path.join('static', 'images', image_file)
            shutil.move(image_file, destination)
            print(f"✓ {image_file} → static/images/ 이동 완료")
        else:
            print(f"⚠ {image_file} 파일을 찾을 수 없습니다.")
    
    print("\n🎮 웹앱 설정이 완료되었습니다!")
    print("다음 명령어로 서버를 실행하세요:")
    print("python new.py")
    print("\n그 후 브라우저에서 http://localhost:5000 으로 접속하세요.")

if __name__ == "__main__":
    setup_project() 