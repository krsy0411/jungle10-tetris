# Jungle Tetris Backend

실시간 대전 및 랭킹 시스템이 포함된 웹 기반 테트리스 게임의 백엔드 API 서버입니다.

## 🚀 주요 기능

### 핵심 시스템

- **사용자 인증**: JWT 기반 회원가입/로그인/로그아웃
- **방 관리**: 1대1 대전을 위한 게임 룸 생성/참가
- **게임 플레이**: 솔로 플레이 및 실시간 대전 모드
- **랭킹 시스템**: 점수 및 승리 횟수 기반 랭킹
- **실시간 통신**: Socket.IO를 통한 실시간 게임 상태 동기화

### 보안 및 성능

- JWT 토큰 기반 인증 (액세스 토큰 15분, 리프레시 토큰 3시간)
- 요청 속도 제한 (Rate Limiting)
- MongoDB 기반 데이터 저장
- CORS 설정 및 입력 검증

## 📁 프로젝트 구조

```
backend/
├── app/                          # 메인 애플리케이션 패키지
│   ├── __init__.py              # Flask 앱 팩토리
│   ├── config.py                # 애플리케이션 설정
│   ├── models/                  # 데이터 모델
│   │   ├── user.py             # 사용자 모델
│   │   ├── game_room.py        # 게임 방 모델
│   │   └── game_record.py      # 게임 기록 모델
│   ├── routes/                  # API 라우트
│   │   ├── auth.py             # 인증 API
│   │   ├── rooms.py            # 방 관리 API
│   │   ├── game.py             # 게임 API
│   │   └── ranking.py          # 랭킹 API
│   ├── socket_events/           # Socket.IO 이벤트 핸들러
│   │   └── handlers.py         # 실시간 이벤트 처리
│   ├── middleware/              # 미들웨어
│   │   └── auth.py             # 인증 및 보안 미들웨어
│   └── utils/                   # 유틸리티
│       ├── database.py         # MongoDB 연결
│       └── jwt_utils.py        # JWT 토큰 유틸리티
├── docs/                        # API 문서
│   ├── product-requirements.md  # 제품 요구사항 명세서
│   ├── openapi.yaml            # OpenAPI 3.0 스펙
│   └── websocket-api.md        # Socket.IO API 문서
├── tests/                       # 테스트 코드
│   └── test_api.py             # API 테스트 스크립트
├── requirements.txt             # Python 패키지 의존성
├── .env.example                # 환경변수 예시
├── .gitignore                  # Git 무시 파일
├── run.py                      # 프로덕션 서버 실행
├── dev_server.py               # 개발 서버 실행
└── README.md                   # 프로젝트 문서
```

## 🛠 기술 스택

- **Framework**: Flask 3.0.0
- **Real-time**: Flask-SocketIO 5.3.6
- **Database**: MongoDB + PyMongo 4.6.1
- **Authentication**: Flask-JWT-Extended 4.6.0
- **Security**: Werkzeug, bcrypt
- **CORS**: Flask-CORS 4.0.0
- **Deployment**: Gunicorn, Eventlet

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

## 🔗 API 엔드포인트

### 기본 정보

- **Base URL**: `http://localhost:8000`
- **Health Check**: `GET /health`
- **API 정보**: `GET /`

### 인증 (Authentication)

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃 (JWT 필요)
- `POST /api/auth/refresh` - 토큰 갱신
- `GET /api/auth/me` - 현재 사용자 정보 (JWT 필요)

### 방 관리 (Rooms)

- `POST /api/rooms` - 방 생성 (JWT 필요)
- `POST /api/rooms/join` - 방 참가 (JWT 필요)
- `DELETE /api/rooms/{id}` - 방 삭제 (JWT 필요)
- `POST /api/rooms/{id}/leave` - 방 나가기 (JWT 필요)
- `GET /api/rooms/{id}` - 방 정보 조회 (JWT 필요)
- `GET /api/rooms` - 대기 중인 방 목록

### 게임 (Game)

- `POST /api/game/solo/start` - 솔로 게임 시작 (JWT 필요)
- `POST /api/game/solo/end` - 솔로 게임 종료 (JWT 필요)
- `POST /api/game/versus/start` - 대전 게임 시작 (JWT 필요)
- `POST /api/game/versus/end` - 대전 게임 종료 (JWT 필요)
- `GET /api/game/history` - 게임 기록 조회 (JWT 필요)

### 랭킹 (Ranking)

- `GET /api/ranking/score` - 점수 랭킹
- `GET /api/ranking/wins` - 승리 횟수 랭킹
- `GET /api/ranking/recent-games` - 최근 게임 기록

## 🌐 Socket.IO 이벤트

### 연결 관리

- `connect` - 클라이언트 연결
- `disconnect` - 클라이언트 연결 해제
- `error` - 오류 처리

### 방 관리

- `room:join` - 방 참가 알림
- `room:leave` - 방 나가기 알림
- `room:update` - 방 정보 업데이트

### 게임 플레이

- `game:start` - 게임 시작 알림
- `game:score_update` - 실시간 점수 업데이트
- `game:game_over` - 게임 종료 처리
- `game:disconnect` - 연결 끊김 처리

### Socket.IO 연결 예시 (JavaScript)

```javascript
import { io } from "socket.io-client";

const socket = io("http://localhost:8000", {
	auth: {
		token: localStorage.getItem("access_token"),
	},
});

// 연결 성공
socket.on("connect", () => {
	console.log("서버에 연결되었습니다");
});

// 방 참가
socket.emit("room:join", {
	room_id: 123,
	user_name: "사용자명",
});

// 실시간 점수 업데이트
socket.emit("game:score_update", {
	room_id: 123,
	user_name: "사용자명",
	score: 1500,
});
```

## 🧪 테스트

### API 테스트 실행

```bash
# 서버가 실행 중인 상태에서
python tests/test_api.py
```

### 수동 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 회원가입
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"user_id":"testuser","name":"테스트","password":"Test123!","password_confirm":"Test123!"}'

# 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"testuser","password":"Test123!"}'
```

## 📊 데이터베이스 스키마

### Users Collection

```javascript
{
  _id: ObjectId,
  user_id: String,           // 로그인 ID (unique)
  name: String,              // 사용자 이름
  hashed_password: String,   // 해시된 비밀번호
  total_score: Number,       // 총 점수
  games_played: Number,      // 플레이한 게임 수
  wins: Number,              // 승리 횟수
  losses: Number,            // 패배 횟수
  solo_high_score: Number,   // 솔로 최고 점수
  refresh_token_version: Number, // 리프레시 토큰 버전
  created_at: Date          // 계정 생성일
}
```

### Game Rooms Collection

```javascript
{
  _id: ObjectId,
  room_id: String,          // 방 번호 (unique)
  host_user_id: String,     // 방장 ID
  host_name: String,        // 방장 이름
  status: String,           // 'waiting' | 'playing' | 'finished'
  participants: Array,      // 참가자 목록
  created_at: Date,         // 방 생성 시간
  game_start_time: Date,    // 게임 시작 시간
  game_end_time: Date       // 게임 종료 시간
}
```

### Game Records Collection

```javascript
{
  _id: ObjectId,
  game_id: String,          // 게임 ID
  room_id: String,          // 방 번호 (멀티플레이어만)
  game_type: String,        // 'solo' | 'multiplayer'
  players: Array,           // 플레이어 정보
  scores: Object,           // 점수 정보
  winner_id: String,        // 승자 ID
  duration: Number,         // 게임 지속 시간 (초)
  created_at: Date         // 게임 일시
}
```

## 🔐 인증 시스템

### JWT 토큰 구조

- **액세스 토큰**: 15분 만료, API 요청 인증용
- **리프레시 토큰**: 3시간 만료, 액세스 토큰 갱신용
- **토큰 버전 관리**: 로그아웃 시 기존 토큰 무효화

### 인증 플로우

1. 회원가입/로그인 → 액세스 토큰 + 리프레시 토큰 발급
2. API 요청 시 `Authorization: Bearer {access_token}` 헤더 사용
3. 토큰 만료 5분 전 자동 갱신 (클라이언트 구현 필요)
4. 로그아웃 시 리프레시 토큰 버전 증가로 기존 토큰 무효화

## 🚀 배포

### 환경별 설정

- **개발**: `FLASK_ENV=development`, MongoDB 로컬
- **스테이징**: `FLASK_ENV=production`, MongoDB Atlas
- **프로덕션**: `FLASK_ENV=production`, MongoDB Atlas + Redis

## 📖 API 문서

상세한 API 문서는 다음 파일들을 참조하세요:

- **OpenAPI 스펙**: [`docs/openapi.yaml`](docs/openapi.yaml)
- **Socket.IO API**: [`docs/websocket-api.md`](docs/websocket-api.md)
- **제품 요구사항**: [`docs/product-requirements.md`](docs/product-requirements.md)

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.
