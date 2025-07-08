# Jungle Tetris Backend

실시간 대전 및 랭킹 시스템이 포함된 웹 기반 테트리스 게임의 백엔드 API 서버입니다.

## 📁 프로젝트 구조

```
backend/
├── app/                          # 메인 애플리케이션 패키지
│   ├── models/                  # 데이터 모델
│   │   ├── user.py             # 사용자 모델
│   │   ├── game_room.py        # 게임 방 모델
│   │   └── game_record.py      # 게임 기록 모델
│   ├── routes/                  # 통합 라우트
│   │   └── main.py             # 모든 API 엔드포인트 (인증, 방, 게임, 랭킹)
│   ├── socket_events/           # Socket.IO 이벤트 핸들러
│   │   └── handlers.py         # 실시간 이벤트 처리 (JWT 인증 포함)
│   ├── utils/                   # 유틸리티
│   │   ├── database.py         # MongoDB 연결
│   │   └── jwt_utils.py        # JWT 토큰 유틸리티
│   └── __init__.py              # Flask 앱 팩토리
├── docs/                        # API 문서
│   ├── product-requirements.md  # 제품 요구사항 명세서
│   ├── openapi.yaml            # OpenAPI 3.0 스펙 (최신 업데이트)
│   ├── websocket-api.md        # Socket.IO API 문서 (JWT 인증)
│   ├── jwt-auth-guide.md       # JWT 인증 가이드
│   └── api-endpoints-guide.md  # API 엔드포인트 가이드
├── templates/                   # HTML 템플릿 (SSR용)
│   ├── main.html               # 메인 페이지
│   ├── login.html              # 로그인 페이지 (JWT 사용)
│   └── rooms.html              # 방 목록 페이지 (JWT 사용)
├── tests/                       # 테스트 코드
│   └── test_api.py             # API 테스트 스크립트
├── requirements.txt             # Python 패키지 의존성
├── .env.example                # 환경변수 예시
├── .gitignore                  # Git 무시 파일
├── run.py                      # 프로덕션 서버 실행
├── dev_server.py               # 개발 서버 실행
└── README.md                   # 프로젝트 문서
```

## 📋 설치 및 실행

### 1. 환경 준비

```bash
# Python 3.8+ 필요
python --version

# MongoDB 설치 및 실행 (로컬 개발용)
# macOS: brew install mongodb-community
# Ubuntu: apt-get install mongodb
# Windows: MongoDB 공식 설치 프로그램 사용

# MongoDB 실행
mongod --dbpath /your/db/path
```

### 2. 프로젝트 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정
```

### 3. 환경변수 설정 (.env)

```env
# Flask 설정
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 서버 설정
HOST=0.0.0.0
PORT=8000

# 데이터베이스
MONGODB_URI=mongodb://localhost:27017/jungle_tetris

# CORS 설정
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. 서버 실행

#### 개발 서버 (권장)

```bash
python dev_server.py
```

#### 프로덕션 서버

```bash
python run.py
```

#### Gunicorn 사용 (프로덕션)

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8000 run:app
```

### ⚠️ 문제 해결

#### 템플릿 경로 오류 (`TemplateNotFound: login.html`)

Flask가 템플릿 파일을 찾지 못하는 경우, `app/__init__.py`에서 템플릿 폴더 경로가 올바르게 설정되어 있는지 확인하세요:

```python
# app/__init__.py의 create_app() 함수에서
import os
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)
```

#### MongoDB 연결 오류

MongoDB가 실행 중이지 않은 경우:

```bash
# MongoDB 실행 확인
sudo systemctl status mongod  # Linux
brew services list | grep mongodb  # macOS

# MongoDB 시작
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```
