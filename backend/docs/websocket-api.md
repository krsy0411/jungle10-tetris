# Jungle Tetris - Socket.IO API Documentation

## 개요

이 문서는 Jungle Tetris 게임의 실시간 통신을 위한 Socket.IO 이벤트를 정의합니다.

### 연결 정보

- **개발 서버**: `ws://localhost:8000`
- **프로덕션 서버**: `wss://api.jungletetris.com`
- **네임스페이스**: `/` (기본)

### 인증

Socket.IO 연결 시 **쿠키 기반** JWT 액세스 토큰을 통한 인증이 필요합니다.
쿠키에 `access_token`이 설정되어 있어야 하며, 연결 시 자동으로 검증됩니다.

```javascript
// 쿠키에 JWT 토큰이 설정되어 있다면 추가 인증 정보 없이 연결 가능
const socket = io("ws://localhost:8000");

// 또는 fallback으로 auth 파라미터 사용 가능
const socket = io("ws://localhost:8000", {
	auth: {
		token: "your_jwt_access_token_here",
	},
});
```

## 연결 상태 이벤트

### `connect`

**Direction**: Server → Client  
**Description**: 소켓 연결 성공 (기본 Socket.IO 이벤트)

```javascript
socket.on("connect", () => {
	console.log("Connected to server");
});
```

### `connect_success`

**Direction**: Server → Client  
**Description**: JWT 인증 성공 후 연결 확인

```javascript
socket.on('connect_success', (data) => {
  console.log(`${data.name}님, ${data.message}`);
  // data 구조
  {
    user_id: "user123",
    name: "홍길동",
    message: "서버에 연결되었습니다"
  }
});
```

### `disconnect`

**Direction**: Server → Client  
**Description**: 소켓 연결 해제 (기본 Socket.IO 이벤트)

```javascript
socket.on("disconnect", (reason) => {
	console.log("Disconnected:", reason);
});
```

### `error`

**Direction**: Server → Client  
**Description**: 인증 실패 또는 기타 오류

```javascript
socket.on("error", (error) => {
	console.error("Socket error:", error);
	// error 구조
	{
		type: "AUTH_ERROR" | "VALIDATION_ERROR" | "ROOM_NOT_FOUND" | "SERVER_ERROR",
		message: "오류 메시지"
	}
});
```

## 방 관리 이벤트

### `room:join`

**Direction**: Client → Server  
**Description**: 특정 방에 참가 (쿠키 기반 JWT 인증)

**Client Request**:

```javascript
socket.emit("room:join", {
	room_id: 123
});
```

**특별 동작**: 
- 방에 2명의 플레이어가 모이면 자동으로 `game:start` 이벤트가 브로드캐스트됩니다.
- 인증은 쿠키의 `access_token`을 통해 자동으로 처리됩니다.

### `room:leave`

**Direction**: Client → Server  
**Description**: 방에서 나가기 (쿠키 기반 JWT 인증)

**Client Request**:

```javascript
socket.emit("room:leave", {
	room_id: 123
});
```

**Server Broadcast** (방 내 남은 사용자에게):

```javascript
socket.on('room:leave', (data) => {
  // data 구조
  {
    user_name: "홍길동",
    message: "홍길동님이 방을 나갔습니다"
  }
});
```

**특별 동작**:
- 방을 나간 후 해당 클라이언트의 소켓 연결이 자동으로 끊어집니다.

## 게임 이벤트

### `game:start`

**Direction**: Server → Client (자동 발생)  
**Description**: 게임 시작 (방에 2명이 참가하면 자동으로 발생)

**Server Broadcast** (방 내 모든 사용자에게):

```javascript
socket.on('game:start', (data) => {
  // data 구조
  {
    players: [
      { name: "홍길동", user_id: "user123", score: 0 },
      { name: "김철수", user_id: "user456", score: 0 }
    ],
    game_time: 60  // 게임 시간 60초
  }
});
```

### `game:score_update`

**Direction**: Client ↔ Server  
**Description**: 실시간 점수 업데이트 (쿠키 기반 JWT 인증)

**Client Request** (점수 변경 시):

```javascript
socket.emit("game:score_update", {
	room_id: 123,
	score: 1500
});
```

**Server Broadcast** (방 내 모든 사용자에게):

```javascript
socket.on('game:score_update', (data) => {
  // data 구조
  {
    players: [
      { user_id: "user123", score: 1500 },
      { user_id: "user456", score: 800 }
    ]
  }
});
```

### `game:end`

**Direction**: Client → Server & Server → Client  
**Description**: 게임 종료 처리 (플레이어가 게임 완료 시 호출)

**Client Request** (게임 완료 시):

```javascript
socket.emit("game:end", {
	room_id: 123,
	score: 2500
});
```

**Server Response**:

#### 상대방 대기 중인 경우 (개인에게만 응답):

```javascript
socket.on('game:end', (data) => {
  // data 구조
  {
    room_id: 123,
    your_score: 2500,
    all_finished: false,
    message: "상대방이 게임을 완료하기를 기다리는 중...",
    status: "waiting"
  }
});
```

#### 모든 플레이어 완료 시 (방 내 모든 사용자에게 브로드캐스트):

```javascript
socket.on('game:end', (data) => {
  // data 구조
  {
    room_id: 123,
    your_score: 2500,
    all_finished: true,
    message: "게임이 종료되었습니다",
    status: "finished",
    final_scores: {
      "user123": 2500,
      "user456": 3200
    },
    winner: "user456",
    is_draw: false
  }
});
```

## TypeScript 인터페이스

### 서버에서 클라이언트로 보내는 이벤트

```typescript
interface ServerToClientEvents {
	// 연결 관리
	connect_success: (data: {
		user_id: string;
		name: string;
		message: string;
	}) => void;

	error: (data: {
		type: "AUTH_ERROR" | "VALIDATION_ERROR" | "ROOM_NOT_FOUND" | "SERVER_ERROR";
		message: string;
	}) => void;

	// 방 관리
	"room:leave": (data: {
		user_name: string;
		message: string;
	}) => void;

	// 게임
	"game:start": (data: {
		players: Array<{ 
			name: string; 
			user_id: string; 
			score: number; 
		}>;
		game_time: number;
	}) => void;

	"game:score_update": (data: {
		players: Array<{ 
			user_id: string; 
			score: number; 
		}>;
	}) => void;

	"game:end": (data: {
		room_id: number;
		your_score: number;
		all_finished: boolean;
		message: string;
		status: "waiting" | "finished";
		final_scores?: Record<string, number>;
		winner?: string;
		is_draw?: boolean;
	}) => void;
}
```

### 클라이언트에서 서버로 보내는 이벤트

```typescript
interface ClientToServerEvents {
	// 방 관리
	"room:join": (data: { room_id: number }) => void;
	"room:leave": (data: { room_id: number }) => void;

	// 게임
	"game:score_update": (data: {
		room_id: number;
		score: number;
	}) => void;
	"game:end": (data: { 
		room_id: number; 
		score: number; 
	}) => void;
}
```

## 클라이언트 구현 예시

### 기본 연결 설정

```javascript
import { io } from "socket.io-client";

// JWT 토큰이 쿠키에 설정되어 있다면 추가 인증 정보 없이 연결
const socket = io("ws://localhost:8000");

// 연결 상태 관리
socket.on("connect", () => {
	console.log("서버에 연결되었습니다");
});

socket.on("connect_success", (data) => {
	console.log(`${data.name}님, 환영합니다!`);
	console.log(`사용자 ID: ${data.user_id}`);
});

socket.on("disconnect", () => {
	console.log("서버와의 연결이 끊어졌습니다");
});

socket.on("error", (error) => {
	console.error("소켓 오류:", error);
	// 토큰 만료 등의 경우 재로그인 처리
	if (error.type === "AUTH_ERROR") {
		// 로그인 페이지로 리다이렉트
		window.location.href = "/login";
	}
});
```

### 방 참가

```javascript
function joinRoom(roomId) {
	socket.emit("room:join", {
		room_id: roomId
	});
}

// 방 나가기 알림 수신
socket.on("room:leave", (data) => {
	console.log(data.message);
	// UI에서 해당 플레이어 제거
});

// 게임 자동 시작 수신 (2명 참가 시)
socket.on("game:start", (data) => {
	console.log("게임이 시작되었습니다!");
	console.log("플레이어:", data.players);
	startCountdown(data.game_time); // 60초 카운트다운 시작
	initializeGame(data.players);
});
```

### 게임 플레이

```javascript
// 점수 업데이트 전송
function updateScore(roomId, newScore) {
	socket.emit("game:score_update", {
		room_id: roomId,
		score: newScore
	});
}

// 상대방 점수 업데이트 수신
socket.on("game:score_update", (data) => {
	updateScoreDisplay(data.players);
});

// 게임 종료 처리
function gameEnd(roomId, finalScore) {
	socket.emit("game:end", {
		room_id: roomId,
		score: finalScore
	});
}

// 게임 종료 결과 수신
socket.on("game:end", (data) => {
	if (data.status === "waiting") {
		// 상대방 대기 중
		showWaitingMessage(data.message, data.your_score);
	} else if (data.status === "finished") {
		// 게임 완료
		showGameResult(data.winner, data.final_scores, data.is_draw);
	}
});
```

## 오류 처리

### 일반적인 오류 응답

```javascript
socket.on("error", (error) => {
	switch (error.type) {
		case "AUTH_ERROR":
			// JWT 토큰 만료 또는 유효하지 않음
			console.error("인증 오류:", error.message);
			redirectToLogin();
			break;
		case "ROOM_NOT_FOUND":
			// 존재하지 않는 방
			showError("방을 찾을 수 없습니다");
			break;
		case "VALIDATION_ERROR":
			// 유효성 검증 실패 (필수 파라미터 누락 등)
			showError(error.message);
			break;
		case "SERVER_ERROR":
			// 서버 내부 오류
			showError("서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
			break;
		default:
			showError("알 수 없는 오류가 발생했습니다");
	}
});
```

### 주요 오류 시나리오

1. **인증 실패**: 쿠키에 `access_token`이 없거나 만료된 경우
2. **방 찾기 실패**: 존재하지 않는 `room_id`로 참가 시도
3. **유효성 검증 실패**: 필수 파라미터 (`room_id`, `score` 등) 누락
4. **서버 오류**: 데이터베이스 연결 실패, 예상치 못한 서버 에러

## 성능 최적화

### 이벤트 throttling

점수 업데이트와 같은 빈번한 이벤트는 throttling을 적용하여 성능을 최적화합니다.

```javascript
import { throttle } from "lodash";

// 점수 업데이트를 100ms마다 한 번만 전송
const throttledScoreUpdate = throttle((roomId, score) => {
	socket.emit("game:score_update", {
		room_id: roomId,
		score: score
	});
}, 100);
```

### 연결 재시도

```javascript
socket.on("disconnect", () => {
	// 자동 재연결 시도
	setTimeout(() => {
		if (!socket.connected) {
			socket.connect();
		}
	}, 1000);
});
```

## 주요 구현 특징

### 1. 쿠키 기반 인증
- JWT 토큰을 쿠키의 `access_token`에서 자동으로 추출
- 클라이언트에서 별도의 토큰 관리 불필요
- Fallback으로 `auth.token` 파라미터도 지원

### 2. 자동 게임 시작
- 방에 2명이 참가하면 자동으로 `game:start` 이벤트 발생
- 별도의 게임 시작 요청 불필요

### 3. 통합된 게임 종료 처리
- `game:end` 이벤트 하나로 대기/완료 상태 모두 처리
- `status` 필드로 현재 상태 구분 (`waiting` | `finished`)

### 4. 자동 연결 해제
- 방을 나가면 해당 클라이언트의 소켓 연결 자동 해제
- 리소스 정리 자동화

---

**문서 버전**: 3.0  
**작성일**: 2025년 7월 14일  
**업데이트**: handlers.py 실제 구현에 맞게 전면 개편  
**관련 문서**: product-requirements.md, openapi.yaml
