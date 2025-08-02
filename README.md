# 🏴‍☠️ 행맨 보물찾기 게임 🏴‍☠️

## 📖 게임 소개
영어 단어를 맞추는 행맨 스타일의 웹 게임입니다. 알파벳을 하나씩 입력하거나 전체 단어를 한 번에 입력할 수 있으며, 정답을 맞추면 퀴즈를 통해 점수를 획득할 수 있습니다.

## 🎮 게임 특징
- **단어 추측**: 알파벳 하나씩 또는 전체 단어 입력 가능
- **시각적 피드백**: 캐릭터가 다리를 건너며 보물로 이동
- **다리 시스템**: 틀릴 때마다 다리가 무너지는 시스템
- **퀴즈 시스템**: 단어 완성 후 한국어 뜻 맞추기
- **점수 시스템**: 정답 시 점수 획득
- **진행 상황**: 현재 문제 번호와 총 문제 수 표시

## 🚀 실행 방법

### 로컬 실행
```bash
# 1. Python 설치 (3.8 이상)
# 2. 필요한 패키지 설치
pip install Flask

# 3. 게임 실행
python new.py

# 4. 브라우저에서 접속
# http://127.0.0.1:5000 (로컬)
# http://192.168.219.115:5000 (같은 WiFi 네트워크)
```

### 배포 준비
```bash
# 배포 파일 생성
python deploy.py

# Git 초기화 (선택사항)
git init
git add .
git commit -m "Initial commit"
```

## 🌐 온라인 배포

### Heroku 배포 (무료)
1. [Heroku CLI 설치](https://devcenter.heroku.com/articles/heroku-cli)
2. 터미널에서 실행:
```bash
heroku login
heroku create your-app-name
git push heroku main
```
3. 브라우저에서 `https://your-app-name.herokuapp.com` 접속

### Railway 배포 (무료)
1. [Railway](https://railway.app) 가입
2. GitHub 저장소 연결
3. 자동 배포 완료

### Render 배포 (무료)
1. [Render](https://render.com) 가입
2. GitHub 저장소 연결
3. Web Service 생성 후 배포

## 📁 파일 구조
```
cusor/
├── new.py              # 메인 Flask 앱
├── deploy.py           # 배포 준비 스크립트
├── templates/
│   └── index.html      # 게임 UI
├── static/
│   └── images/         # 게임 이미지들
│       ├── 다리1.png ~ 다리5.png
│       ├── 사람.gif
│       └── 보물.png
└── README.md           # 이 파일
```

## 🎯 게임 규칙
1. **단어 추측**: 알파벳 하나씩 또는 전체 단어 입력
2. **캐릭터 이동**: 정답 시 캐릭터가 오른쪽으로 이동
3. **다리 무너짐**: 틀릴 때마다 다리가 무너짐 (최대 4번)
4. **퀴즈**: 단어 완성 후 한국어 뜻 맞추기
5. **점수**: 퀴즈 정답 시 +1점
6. **게임 종료**: 모든 문제 완료 또는 기회 소진

## 🔧 기술 스택
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **이미지**: PNG, GIF
- **배포**: Heroku/Railway/Render

## 📞 지원
문제가 있거나 개선 사항이 있으면 이슈를 등록해주세요!

---

**즐거운 게임 되세요! 🎮✨** 