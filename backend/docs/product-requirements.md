# Jungle Tetris - 테트리스 게임 PRD (Product Requirements Document)

## 1. 프로젝트 개요

### 1.1 제품명
Jungle Tetris - 멀티플레이어 테트리스 게임

### 1.2 제품 비전
실시간 대전 및 랭킹 시스템이 포함된 웹 기반 테트리스 게임으로, JWT 기반 쿠키 인증과 Socket.IO를 통한 실시간 상호작용을 제공하는 플랫폼

### 1.3 핵심 목표
- 클래식 테트리스 게임 구현
- JWT 쿠키 기반의 안전한 인증 시스템
- Socket.IO를 통한 실시간 멀티플레이어 대전 기능
- 사용자 성과 추적 및 랭킹 시스템
- 직관적이고 반응성 있는 사용자 인터페이스

## 2. 기술 스택

### 2.1 백엔드
- **프레임워크**: Flask
- **실시간 통신**: Flask-SocketIO
- **데이터베이스**: MongoDB
- **템플릿 엔진**: Jinja2
- **인증 시스템**: JWT (JSON Web Token) - 쿠키 기반
- **개발 환경**: localhost:8000
- **배포 환경**: AWS EC2

### 2.2 프론트엔드
- **기본 구조**: HTML5, CSS3, JavaScript (ES6+)
- **실시간 통신**: Socket.IO 클라이언트
- **인증**: JWT 토큰 쿠키 자동 처리

### 2.3 실시간 통신
- **개발 환경 엔드포인트**: `ws://localhost:8000`
- **배포 환경 엔드포인트**: EC2 서버의 WebSocket 엔드포인트
- **인증 방식**: 쿠키의 JWT 토큰으로 자동 인증
- **주요 기능**:
  - 실시간 방 관리 (입장/퇴장 알림)
  - 게임 중 실시간 점수 동기화
  - 게임 시작/종료 이벤트 (멀티플레이어 모드)
  - 연결 상태 관리

## 3. 핵심 기능 요구사항

### 3.1 사용자 인증 시스템

#### 3.1.1 JWT 기반 쿠키 인증
**기능 설명**: JWT 토큰을 쿠키로 관리하는 안전한 인증 시스템

- **인증 방식**:
  - 로그인 시 `access_token`과 `refresh_token`이 쿠키로 설정
  - 모든 인증이 필요한 API는 쿠키의 JWT 토큰을 확인
  - Socket.IO 연결도 쿠키의 JWT 토큰으로 인증
- **토큰 관리**:
  - 액세스 토큰: 15분 만료
  - 리프레시 토큰: 3시간 만료
  - 자동 토큰 갱신 시스템
- **보안**:
  - HttpOnly 쿠키로 XSS 공격 방지
  - SameSite 설정으로 CSRF 공격 방지

#### 3.1.2 토큰 재발급
**API**: `POST /api/auth/refresh`

**기능 설명**: 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급

- **입력**:
  - `refresh_token`: 리프레시 토큰 (문자열)
- **출력**:
  - `access_token`: 새로운 액세스 토큰
  - `expires_in`: 만료 시간 (초 단위)
- **오류 처리**:
  - 400: 잘못된 요청
  - 401: 유효하지 않은 토큰

### 3.2 방 관리 시스템

#### 3.2.1 방 생성
**API**: `POST /api/rooms/create`

**기능 설명**: 1대1 대전을 위한 게임 룸을 생성합니다

- **인증 방식**:
  - 쿠키의 JWT 토큰에서 사용자 정보를 자동 추출
  - 요청 바디 불필요, 토큰만으로 방 생성
- **자동 생성**:
  - 방 ID: 8자리 랜덤 문자열 (예: "a1b2c3d4")
  - 호스트: JWT 토큰에서 추출된 사용자
- **응답 데이터**:
  - `room_id`: 생성된 방 ID
  - `host_user_id`: 방장 사용자 ID
  - `host_name`: 방장 이름
  - `status`: 방 상태 (waiting/playing/finished)
  - `participants`: 참가자 목록
  - `participant_count`: 현재 참가자 수
  - `max_participants`: 최대 참가자 수 (2명)
  - `created_at`: 방 생성 시간
- **실시간 연동**: 방 생성 후 Socket.IO를 통해 실시간 방 관리 가능

#### 3.2.2 방 참가
**API**: `POST /api/rooms/join`

**기능 설명**: 방 ID를 입력하여 방에 참가합니다

- **입력 데이터**:
  - `room_id`: 참가할 방 ID (문자열)
- **검증 사항**:
  - 방 존재 여부 확인
  - 방 상태 확인 (대기중인지 확인)
  - 방 인원 확인 (최대 2명)
  - JWT 토큰을 통한 사용자 인증
- **성공 응답**:
  - `message`: 성공 메시지
  - `room_id`: 참가한 방 ID
  - `participants`: 현재 참가자 목록 (사용자 ID, 이름, 점수, 상태)
- **오류 처리**:
  - 400: 잘못된 요청 (방 ID 누락 등)
  - 401: 인증 실패
  - 404: 방을 찾을 수 없음
  - 409: 방이 가득 참 또는 게임 진행 중
- **실시간 연동**: 방 참가 후 Socket.IO `room:join` 이벤트를 통해 실시간 상호작용 시작

### 3.3 게임 플레이 시스템

#### 3.3.1 솔로 플레이 테트리스

**게임 시작 API**: `POST /api/game/solo/start`
**게임 종료 API**: `POST /api/game/solo/end`

**기능 설명**: 단독 플레이 모드의 클래식 테트리스

- **게임 시작**:
  - JWT 토큰을 통한 자동 인증
  - 응답: `game_time` (60초), 성공 메시지
- **게임 mechanics**:
  - 7가지 테트로미노 (I, O, T, S, Z, J, L)
  - 블록 회전, 좌우 이동, 하드 드롭
  - 라인 클리어 (1~4줄 동시 제거)
- **게임 종료**:
  - 입력: `score` (획득 점수, 0 이상)
  - 응답: 성공 메시지, 최종 점수, 개인 최고 기록 갱신 여부, 현재 최고 점수
  - 사용자 통계 자동 업데이트
- **오류 처리**:
  - 400: 잘못된 점수 입력
  - 401: 인증 실패
  - 500: 서버 내부 오류

#### 3.3.2 멀티플레이어 게임 로직

**기능 설명**: Socket.IO를 통한 실시간 대전 모드

- **게임 시작 조건**:
  - 방에 2명이 참가하면 `game:start` 이벤트가 자동으로 발생
  - 서버에서 `game_time` (60초) 제공
  - 클라이언트가 카운트다운 타이머 처리
- **게임 진행**:
  - `game:score_update` 이벤트를 통한 실시간 점수 동기화
  - 상대방 점수 실시간 표시
  - 상대방 이름 표시
- **게임 종료**:
  - 각 플레이어가 `game:end` 이벤트로 최종 점수 제출
  - 모든 플레이어가 점수를 제출하면 승부 결과 계산
  - 1분 후 점수가 높은 사람이 승리
  - 게임 오버된 플레이어가 있으면 상대방 승리
- **결과 처리**:
  - 승리 시 점수 및 승리 횟수 기록
  - 게임 기록 데이터베이스에 저장

### 3.4 랭킹 시스템

#### 3.4.1 점수 랭킹
**API**: `GET /api/ranking/score`

**기능 설명**: 전체 사용자 중 최고 점수 순위를 조회합니다

- **인증**: 인증 불필요 (퍼블릭 API)
- **응답 데이터**:
  - `ranking`: 랭킹 배열 (최대 15명)
    - `rank`: 순위 (정수)
    - `name`: 사용자명 (문자열)
    - `score`: 최고 점수 (정수)
- **정렬**: 점수 높은 순으로 정렬
- **오류 처리**: 500 (서버 내부 오류)

#### 3.4.2 승리 횟수 랭킹
**API**: `GET /api/ranking/wins`

**기능 설명**: 대전 모드 승리 횟수 순위를 조회합니다

- **인증**: 인증 불필요 (퍼블릭 API)
- **응답 데이터**:
  - `ranking`: 랭킹 배열 (최대 15명)
    - `rank`: 순위 (정수)
    - `name`: 사용자명 (문자열)
    - `wins`: 승리 횟수 (정수)
- **정렬**: 승리 횟수 높은 순으로 정렬
- **오류 처리**: 500 (서버 내부 오류)

## 4. 데이터베이스 설계

### 4.1 사용자 컬렉션 (users)

```javascript
{
  _id: ObjectId,
  user_id: String(unique),     // 로그인 ID
  name: String,                // 사용자 이름
  password_hash: String,       // 해시된 비밀번호
  refresh_token_issued_at: Date, // 리프레시 토큰 발급 시간 (토큰 무효화용)
  created_at: Date,           // 계정 생성일
  last_login: Date,           // 마지막 로그인
  is_active: Boolean          // 계정 활성화 상태
}
```

### 4.2 게임 기록 컬렉션 (game_records)

```javascript
{
  _id: ObjectId,
  user_id: String,            // 플레이어 ID
  game_type: String,          // "solo" | "versus"
  score: Number,              // 획득 점수
  opponent_id: String,        // 대전 상대 ID (versus만)
  is_winner: Boolean,         // 승리 여부 (versus만)
  played_at: Date            // 게임 플레이 일시
}
```

### 4.3 방 정보 컬렉션 (rooms)

```javascript
{
  _id: ObjectId,
  room_id: String(unique),    // 방 ID (8자리)
  host_user_id: String,      // 방장 사용자 ID
  host_name: String,         // 방장 이름
  status: String,            // "waiting" | "playing" | "finished"
  participants: Array,       // 참가자 목록
  participant_count: Number, // 현재 참가자 수
  max_participants: Number,  // 최대 참가자 수 (2명)
  created_at: Date,          // 방 생성 시간
  updated_at: Date           // 마지막 업데이트
}
```

### 4.4 사용자 통계 컬렉션 (user_stats)

```javascript
{
  _id: ObjectId,
  user_id: String(unique),    // 사용자 ID
  solo_best_score: Number,       // 최고 점수
  versus_total_wins: Number,       // 총 승리 수
  updated_at: Date           // 마지막 업데이트
}
```

## 5. API 설계

### 5.1 인증 API

- `POST /api/auth/refresh` - 액세스 토큰 재발급
  - 리프레시 토큰을 사용하여 새로운 액세스 토큰 발급
  - 입력: `refresh_token` (문자열)
  - 출력: `access_token`, `expires_in`

### 5.2 방 관리 API

- `POST /api/rooms/create` - 방 생성
  - JWT 토큰 기반으로 방 생성 (요청 바디 불필요)
  - 출력: 방 정보 (room_id, host 정보, 참가자 목록 등)

- `POST /api/rooms/join` - 방 참가
  - 방 ID를 입력하여 방에 참가
  - 입력: `room_id` (문자열)
  - 출력: 성공 메시지, 방 정보, 참가자 목록

### 5.3 게임 API

- `POST /api/game/solo/start` - 솔로 게임 시작
  - JWT 토큰 기반 인증
  - 출력: `game_time` (60초), 성공 메시지

- `POST /api/game/solo/end` - 솔로 게임 종료
  - 솔로 게임 최종 결과 제출
  - 입력: `score` (정수, 0 이상)
  - 출력: 성공 메시지, 점수, 최고 기록 갱신 여부

### 5.4 랭킹 API

- `GET /api/ranking/score` - 점수 랭킹 조회
  - 전체 사용자 최고 점수 순위 (최대 15명)
  - 인증 불필요
  - 출력: 랭킹 배열 (rank, name, score)

- `GET /api/ranking/wins` - 승리 횟수 랭킹 조회
  - 대전 모드 승리 횟수 순위 (최대 15명)
  - 인증 불필요
  - 출력: 랭킹 배열 (rank, name, wins)

## 6. Socket.IO 이벤트

### 6.1 연결 및 인증

- **연결 시 인증**: 쿠키의 JWT 토큰으로 자동 인증
- **개발 환경 엔드포인트**: `ws://localhost:8000`
- **배포 환경 엔드포인트**: EC2 서버의 WebSocket 엔드포인트
- **인증 실패 시**: 소켓 연결 해제

### 6.2 방 관리 이벤트

- `room:join` - 방 참가

  ```javascript
  // 클라이언트 → 서버
  { room_id: "a1b2c3d4" }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  { 
    room_id: "a1b2c3d4", 
    user_name: "홍길동", 
    message: "홍길동님이 방에 참가했습니다" 
  }
  ```

- `room:leave` - 방 나가기

  ```javascript
  // 클라이언트 → 서버
  { room_id: "a1b2c3d4" }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  { 
    room_id: "a1b2c3d4", 
    user_name: "홍길동", 
    message: "홍길동님이 방을 나갔습니다" 
  }
  ```

### 6.3 게임 이벤트

- `game:start` - 게임 시작 (2명 참가 시 자동 발생)

  ```javascript
  // 서버 → 클라이언트 (방 내 모든 사용자)
  {
    room_id: "a1b2c3d4",
    players: [
      { name: "홍길동", score: 0 },
      { name: "김철수", score: 0 }
    ],
    game_time: 60              // 게임 시간 60초
  }
  ```

- `game:score_update` - 점수 업데이트

  ```javascript
  // 클라이언트 → 서버
  { room_id: "a1b2c3d4", score: 1500 }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  {
    room_id: "a1b2c3d4",
    players: [
      { name: "홍길동", score: 1500 },
      { name: "김철수", score: 800 }
    ]
  }
  ```

- `game:end` - 게임 종료 (각 플레이어가 최종 점수 제출)

  ```javascript
  // 클라이언트 → 서버
  { room_id: "a1b2c3d4", final_score: 2500 }

  // 서버 → 클라이언트 (모든 플레이어가 점수 제출 시)
  {
    room_id: "a1b2c3d4",
    game_over: true,
    winner: "김철수",
    loser: "홍길동",
    final_scores: {
      "홍길동": 2500,
      "김철수": 3200
    }
  }
  ```

## 7. 성능 및 보안 요구사항

### 7.1 성능 목표

- **게임 프레임 레이트**: 60 FPS
- **네트워크 지연**: 100ms 이하  
- **동시 접속자**: 1000명
- **응답 시간**: 2초 이내

### 7.2 보안 요구사항

#### 7.2.1 JWT 보안
- **JWT 서명 알고리즘**: HS256 또는 RS256
- **비밀 키 환경변수 관리**: 환경 변수로 안전하게 관리
- **토큰 만료 시간**:
  - 액세스 토큰: 15분
  - 리프레시 토큰: 3시간
- **쿠키 보안 설정**:
  - HttpOnly: XSS 공격 방지
  - SameSite: CSRF 공격 방지

#### 7.2.2 인증 및 권한
- **Socket.IO 인증**: 쿠키의 JWT 토큰으로 연결 시 자동 인증
- **API 인증**: 모든 보호된 엔드포인트에서 JWT 토큰 검증
- **토큰 무효화**: 리프레시 토큰 발급 시간 기반 간단한 무효화

#### 7.2.3 웹 보안
- **비밀번호 보안**: bcrypt 해싱
- **NoSQL 인젝션 방지**: 입력 데이터 검증 및 파라미터화된 쿼리
- **XSS 공격 방지**: 입력 데이터 이스케이프 처리
- **CORS 정책 설정**: 허용된 도메인만 접근 가능
