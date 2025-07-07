# 테트리스 게임 PRD (Product Requirements Document)

## 1. 프로젝트 개요

### 1.1 제품명

Jungle Tetris - 멀티플레이어 테트리스 게임

### 1.2 제품 비전

실시간 대전 및 랭킹 시스템이 포함된 웹 기반 테트리스 게임으로, 사용자들이 솔로 플레이와 1대1 경쟁을 통해 즐길 수 있는 플랫폼

### 1.3 핵심 목표

- 클래식 테트리스 게임 구현
- 실시간 멀티플레이어 대전 기능
- 사용자 성과 추적 및 랭킹 시스템
- 직관적이고 반응성 있는 사용자 인터페이스

## 2. 기술 스택

### 2.1 백엔드

- **프레임워크**: Flask
- **실시간 통신**: Flask-SocketIO
- **데이터베이스**: MongoDB
- **템플릿 엔진**: Jinja2
- **인증 시스템**: JWT (JSON Web Token)
- **배포 환경**: AWS EC2

### 2.2 클라이언트 게임 로직

- **시간 관리**: 클라이언트에서 1분 카운트다운 타이머 처리
- **점수 동기화**: 서버와 실시간 점수 동기화
- **게임 상태**: 클라이언트가 게임 오버 조건 판단 후 서버로 결과 전송

## 3. 핵심 기능 요구사항

### 3.1 사용자 인증 시스템

#### 3.1.1 회원가입

**기능 설명**: 새로운 사용자 계정 생성

- **입력 필드**:
  - 아이디 (ID): 5-20자, 영문 및 숫자 조합, 중복 불가
  - 이름 (Name): 2-10자, 한글/영문 허용
  - 비밀번호 (Password): 8-20자, 영문/숫자/특수문자 포함
  - 비밀번호 확인: 비밀번호와 일치 검증
- **유효성 검증**:
  - 아이디 중복 확인
  - 비밀번호 강도 검증
  - 모든 필드 필수 입력
- **성공 시**: 자동 로그인 후 메인 페이지 이동
- **실패 시**: 구체적인 오류 메시지 표시

#### 3.1.2 로그인

**기능 설명**: 기존 사용자 계정 인증

- **입력 필드**:
  - 아이디 (ID)
  - 비밀번호 (Password)
- **기능**:
  - JWT 토큰 기반 인증
  - 액세스 토큰 (15분 만료) + 리프레시 토큰 (3시간 만료)
  - 자동 토큰 갱신
  - 로그인 실패 시 횟수 제한 (5회)
- **성공 시**: 메인 대시보드로 이동
- **실패 시**: 오류 메시지 및 재시도 옵션

#### 3.1.3 로그아웃

**기능 설명**: 사용자 세션 종료

- 클라이언트에서 JWT 토큰 삭제
- 서버에서 리프레시 토큰 무효화 (해당 사용자 ID의 새 토큰 발급 시 이전 토큰 거부)
- 진행 중인 게임이 있을 경우 경고 메시지
- 로그인 페이지로 리다이렉트

#### 3.1.4 토큰 갱신

**기능 설명**: JWT 액세스 토큰 자동 갱신

- 리프레시 토큰을 이용한 새 액세스 토큰 발급
- 토큰 만료 5분 전 자동 갱신
- 리프레시 토큰 만료 시 재로그인 요구

### 3.2 방 관리 시스템

#### 3.2.1 방 생성

**기능 설명**: 1대1 대전을 위한 게임 룸 생성

- **방 설정 옵션**:
  - 방 제목: 1-30자, 특수문자 제한
- **방 관리**:
  - 방장 권한 (게임 시작, 방 설정 변경, 강제 퇴장)
  - 최대 인원: 2명 (방장 + 참가자 1명)
  - 방 상태: 대기중/게임중/비공개
- **자동 기능**:
  - 방장 나가면 자동 방 삭제
  - 10분간 비활성 시 자동 삭제

#### 3.2.2 방 참가

**기능 설명**: 방 번호를 입력하여 방에 참가

- **방 참가 방식**:
  - 사용자가 방 번호(room_id) 직접 입력
  - 방 번호가 존재하고 참가 가능한 경우 즉시 입장
  - 방 번호가 존재하지 않거나 이미 가득 찬 경우 오류 메시지 표시
- **입력 검증**:
  - 방 번호 형식 확인
  - 방 존재 여부 확인
  - 방 상태 확인 (대기중인지, 게임중인지)
  - 방 인원 확인 (최대 2명)

### 3.3 게임 플레이 시스템

#### 3.3.1 솔로 플레이 테트리스

**기능 설명**: 단독 플레이 모드의 클래식 테트리스

- **게임 mechanics**:
  - 7가지 테트로미노 (I, O, T, S, Z, J, L)
  - 블록 회전 (시계방향/반시계방향)
  - 좌우 이동
  - 라인 클리어 (1~4줄 동시 제거)
- **시간 제한**:
  - 게임 시간: 1분 (60초)
  - 서버는 게임 시작 시 game_time(60초)만 전달
  - 클라이언트가 카운트다운 타이머 처리
  - 시간 종료 시 자동으로 게임 종료
- **게임 오버 조건**:
  - 1분 시간 종료
  - 새로운 블록이 생성될 공간이 없을 때
  - 최종 점수 및 통계 표시

#### 3.3.2 1대1 경쟁 테트리스

**기능 설명**: 실시간 대전 모드

- **솔로 플레이 기능 + 추가 요소**:
  - 상대방 점수 실시간 표시
  - 상대방 이름 표시
- **시간 제한**:
  - 게임 시간: 1분 (60초)
  - 서버는 게임 시작 시 game_time(60초)만 전달
  - 클라이언트가 카운트다운 타이머 처리
  - 양쪽 플레이어 동시에 시간 종료
- **승부 결정**:
  - 1분 후 점수가 높은 사람이 승리
  - 게임 오버된 플레이어가 있으면 상대방 승리
  - 승리 시 점수 및 승리 횟수 기록
- **동기화**:
  - 게임 시작 카운트다운 (3-2-1)
  - 연결 끊김 시 대기 및 재연결

### 3.4 랭킹 시스템

#### 3.4.1 개인 통계

**기능 설명**: 개별 사용자의 성과 추적

- **솔로 플레이 기록**:
  - 최고 점수 (개인 베스트)
  - 평균 점수 (최근 10게임)
  - 총 플레이 횟수
  - 최고 레벨 도달 기록
- **대전 기록**:
  - 총 승리 횟수
  - 총 경기 수

#### 3.4.2 전체 랭킹

**기능 설명**: 모든 사용자 간 순위 비교

- **최고 점수 랭킹**:
  - 전체 사용자 중 최고 점수 TOP 100
  - 사용자명, 점수 표시
- **승리 횟수 랭킹**:
  - 대전 모드 승리 횟수 TOP 100
  - 사용자명, 승리 횟수 표시

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
  level: Number,              // 도달 레벨
  lines_cleared: Number,      // 제거한 라인 수
  play_time: Number,          // 플레이 시간(초) - 최대 60초
  opponent_id: String,        // 대전 상대 ID (versus만)
  is_winner: Boolean,         // 승리 여부 (versus만)
  played_at: Date            // 게임 플레이 일시
}
```

### 4.3 방 정보 컬렉션 (rooms)

```javascript
{
  _id: ObjectId,
  room_id: String(unique),    // 방 번호 (사용자 입력용)
  room_title: String,         // 방 제목
  host_id: String,           // 방장 ID
  status: String,            // "waiting" | "playing" | "finished"
  players: Array,            // 참가자 목록
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

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인 (JWT 토큰 발급)
- `POST /api/auth/logout` - 로그아웃 (리프레시 토큰 무효화)
- `POST /api/auth/refresh` - 액세스 토큰 갱신
- `GET /api/auth/profile` - 사용자 프로필 조회 (인증 필요)

### 5.2 방 관리 API

- `POST /api/rooms` - 방 생성
- `POST /api/rooms/join` - 방 참가 (방 번호로)
- `DELETE /api/rooms/:id` - 방 삭제

### 5.3 게임 API

- `POST /api/game/solo/start` - 솔로 게임 시작
- `POST /api/game/solo/end` - 솔로 게임 종료
- `POST /api/game/versus/start` - 대전 게임 시작
- `POST /api/game/versus/end` - 대전 게임 종료

### 5.4 랭킹 API

- `GET /api/ranking/score` - 점수 랭킹
- `GET /api/ranking/wins` - 승리 랭킹
- `GET /api/stats/:user_id` - 개인 통계

## 6. Socket.IO 이벤트

### 6.1 방 관리 이벤트

- `room:join` - 방 참가

  ```javascript
  // 클라이언트 → 서버
  { room_id: "room123", user_name: "홍길동" }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  { room_id: "room123", user_name: "홍길동", message: "홍길동님이 방에 참가했습니다" }
  ```

- `room:leave` - 방 나가기

  ```javascript
  // 클라이언트 → 서버
  { room_id: "room123", user_name: "홍길동" }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  { room_id: "room123", user_name: "홍길동", message: "홍길동님이 방을 나갔습니다" }
  ```

- `room:update` - 방 정보 업데이트
  ```javascript
  // 서버 → 클라이언트
  { room_id: "room123", status: "waiting", players: ["홍길동", "김철수"] }
  ```

### 6.2 게임 이벤트

- `game:start` - 게임 시작

  ```javascript
  // 서버 → 클라이언트 (방 내 모든 사용자)
  {
    room_id: "room123",
    players: [
      { name: "홍길동", score: 0 },
      { name: "김철수", score: 0 }
    ],
    game_time: 60              // 게임 시간 60초 (클라이언트가 카운트다운 처리)
  }
  ```

- `game:score_update` - 점수 업데이트

  ```javascript
  // 클라이언트 → 서버
  { room_id: "room123", user_name: "홍길동", score: 1500 }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  {
    room_id: "room123",
    players: [
      { name: "홍길동", score: 1500 },
      { name: "김철수", score: 800 }
    ]
  }
  ```

- `game:game_over` - 게임 오버

  ```javascript
  // 클라이언트 → 서버
  { room_id: "room123", user_name: "홍길동", final_score: 2500 }

  // 서버 → 클라이언트 (방 내 모든 사용자)
  {
    room_id: "room123",
    game_over: true,
    winner: "김철수",
    loser: "홍길동",
    final_scores: {
      "홍길동": 2500,
      "김철수": 3200
    }
  }
  ```

- `game:disconnect` - 연결 끊김 처리
  ```javascript
  // 서버 → 클라이언트 (상대방에게)
  {
    room_id: "room123",
    disconnected_player: "홍길동",
    message: "상대방의 연결이 끊어졌습니다. 잠시 후 재연결을 시도합니다.",
    wait_time: 30
  }
  ```

## 7. 성능 및 보안 요구사항

### 7.1 성능 목표

- 게임 프레임 레이트: 60 FPS
- 네트워크 지연: 100ms 이하
- 동시 접속자: 1000명
- 응답 시간: 2초 이내

### 7.2 보안 요구사항

- **JWT 보안**:
  - JWT 서명 알고리즘: HS256 또는 RS256
  - 비밀 키 환경변수 관리
  - 액세스 토큰 만료: 15분
  - 리프레시 토큰 만료: 3시간
  - 간단한 토큰 무효화 (리프레시 토큰 발급 시간 기반)
- **비밀번호 보안**: bcrypt 해싱
- **웹 보안**:
  - NoSQL 인젝션 방지
  - XSS 공격 방지
  - CSRF 토큰 사용
  - CORS 정책 설정
- **HTTPS 적용**: SSL/TLS 인증서 필수

### 7.3 JWT 토큰 구조 및 처리

#### 7.3.1 액세스 토큰 (Access Token)

```javascript
// JWT Payload 구조
{
  "user_id": "user123",           // 사용자 ID
  "name": "홍길동",               // 사용자 이름
  "iat": 1625097600,             // 발급 시간
  "exp": 1625098500,             // 만료 시간 (15분)
  "type": "access"               // 토큰 타입
}
```

#### 7.3.2 리프레시 토큰 (Refresh Token)

```javascript
// JWT Payload 구조
{
  "user_id": "user123",           // 사용자 ID
  "iat": 1625097600,             // 발급 시간
  "exp": 1625108400,             // 만료 시간 (3시간)
  "type": "refresh"              // 토큰 타입
}
```

#### 7.3.3 토큰 인증 미들웨어

- **헤더 형식**: `Authorization: Bearer <access_token>`
- **토큰 검증 순서**:
  1. 토큰 형식 검증
  2. 서명 검증
  3. 만료 시간 확인
  4. 사용자 존재 여부 확인
- **리프레시 토큰 검증**:
  - 토큰 발급 시간이 사용자의 `refresh_token_issued_at` 이후인지 확인
  - 로그아웃 시 `refresh_token_issued_at`을 현재 시간으로 업데이트하여 이전 토큰 무효화
- **인증 실패 시**: 401 Unauthorized 응답

#### 7.3.4 Socket.IO JWT 인증

- **연결 시 인증**: `socket.handshake.auth.token`으로 JWT 전달
- **토큰 검증**: 액세스 토큰 유효성 확인
- **인증 실패 시**: 소켓 연결 해제

---

**문서 버전**: 1.3  
**작성일**: 2025년 7월 8일  
**최종 수정**: 2025년 7월 8일 (리프레시 토큰 만료시간 3시간으로 조정, 불필요한 섹션 제거)  
**최종 검토**: 개발 시작 전 재검토 필요
