# Jungle Tetris - Socket.IO API Documentation

## 개요

이 문서는 Jungle Tetris 게임의 실시간 통신을 위한 Socket.IO 이벤트를 정의합니다.

### 연결 정보

- **개발 서버**: `ws://localhost:5000`
- **프로덕션 서버**: `wss://api.jungletetris.com`
- **네임스페이스**: `/` (기본)

### 인증

Socket.IO 연결 시 JWT 액세스 토큰을 통한 인증이 필요합니다.

```javascript
const socket = io("ws://localhost:5000", {
	auth: {
		token: "your_jwt_access_token_here",
	},
});
```

## 연결 상태 이벤트

### `connect`

**Direction**: Server → Client  
**Description**: 소켓 연결 성공

```javascript
socket.on("connect", () => {
	console.log("Connected to server");
});
```

### `disconnect`

**Direction**: Server → Client  
**Description**: 소켓 연결 해제

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
});
```

## 방 관리 이벤트

### `room:join`

**Direction**: Client → Server  
**Description**: 특정 방에 참가

**Client Request**:

```javascript
socket.emit("room:join", {
	room_id: 123,
	user_name: "홍길동",
});
```

**Server Broadcast** (방 내 모든 사용자에게):

```javascript
socket.on('room:join', (data) => {
  // data 구조
  {
    room_id: 123,
    user_name: "홍길동",
    message: "홍길동님이 방에 참가했습니다"
  }
});
```

### `room:leave`

**Direction**: Client → Server  
**Description**: 방에서 나가기

**Client Request**:

```javascript
socket.emit("room:leave", {
	room_id: 123,
	user_name: "홍길동",
});
```

**Server Broadcast** (방 내 남은 사용자에게):

```javascript
socket.on('room:leave', (data) => {
  // data 구조
  {
    room_id: 123,
    user_name: "홍길동",
    message: "홍길동님이 방을 나갔습니다"
  }
});
```

### `room:update`

**Direction**: Server → Client  
**Description**: 방 정보 업데이트 (플레이어 변경, 상태 변경 등)

```javascript
socket.on('room:update', (data) => {
  // data 구조
  {
    room_id: 123,
    status: "waiting", // "waiting" | "playing" | "finished"
    players: ["홍길동", "김철수"]
  }
});
```

## 게임 이벤트

### `game:start`

**Direction**: Server → Client  
**Description**: 게임 시작 알림 (방장이 게임 시작 시 자동 발송)

```javascript
socket.on('game:start', (data) => {
  // data 구조
  {
    room_id: 123,
    players: [
      { name: "홍길동", score: 0 },
      { name: "김철수", score: 0 }
    ],
    game_time: 60  // 게임 시간 60초 (클라이언트가 카운트다운 처리)
  }
});
```

### `game:score_update`

**Direction**: Client ↔ Server  
**Description**: 실시간 점수 업데이트

**Client Request** (점수 변경 시):

```javascript
socket.emit("game:score_update", {
	room_id: 123,
	user_name: "홍길동",
	score: 1500,
});
```

**Server Broadcast** (방 내 모든 사용자에게):

```javascript
socket.on('game:score_update', (data) => {
  // data 구조
  {
    room_id: 123,
    players: [
      { name: "홍길동", score: 1500 },
      { name: "김철수", score: 800 }
    ]
  }
});
```

### `game:game_over`

**Direction**: Client → Server & Server → Client  
**Description**: 게임 종료 처리

**Client Request** (게임 오버 시):

```javascript
socket.emit("game:game_over", {
	room_id: 123,
	user_name: "홍길동",
	final_score: 2500,
});
```

**Server Broadcast** (방 내 모든 사용자에게):

```javascript
socket.on('game:game_over', (data) => {
  // data 구조
  {
    room_id: 123,
    game_over: true,
    winner: "김철수",
    loser: "홍길동",
    final_scores: {
      "홍길동": 2500,
      "김철수": 3200
    }
  }
});
```

### `game:disconnect`

**Direction**: Server → Client  
**Description**: 상대방 연결 끊김 알림

```javascript
socket.on('game:disconnect', (data) => {
  // data 구조
  {
    room_id: 123,
    disconnected_player: "홍길동",
    message: "상대방의 연결이 끊어졌습니다. 잠시 후 재연결을 시도합니다.",
    wait_time: 30  // 재연결 대기 시간 (초)
  }
});
```

## TypeScript 인터페이스

### 서버에서 클라이언트로 보내는 이벤트

```typescript
interface ServerToClientEvents {
	// 방 관리
	"room:join": (data: {
		room_id: number;
		user_name: string;
		message: string;
	}) => void;

	"room:leave": (data: {
		room_id: number;
		user_name: string;
		message: string;
	}) => void;

	"room:update": (data: {
		room_id: number;
		status: "waiting" | "playing" | "finished";
		players: string[];
	}) => void;

	// 게임
	"game:start": (data: {
		room_id: number;
		players: Array<{ name: string; score: number }>;
		game_time: number;
	}) => void;

	"game:score_update": (data: {
		room_id: number;
		players: Array<{ name: string; score: number }>;
	}) => void;

	"game:game_over": (data: {
		room_id: number;
		game_over: boolean;
		winner: string;
		loser: string;
		final_scores: Record<string, number>;
	}) => void;

	"game:disconnect": (data: {
		room_id: number;
		disconnected_player: string;
		message: string;
		wait_time: number;
	}) => void;
}
```

### 클라이언트에서 서버로 보내는 이벤트

```typescript
interface ClientToServerEvents {
	// 방 관리
	"room:join": (data: { room_id: number; user_name: string }) => void;

	"room:leave": (data: { room_id: number; user_name: string }) => void;

	// 게임
	"game:score_update": (data: {
		room_id: number;
		user_name: string;
		score: number;
	}) => void;

	"game:game_over": (data: {
		room_id: number;
		user_name: string;
		final_score: number;
	}) => void;
}
```

## 클라이언트 구현 예시

### 기본 연결 설정

```javascript
import { io } from "socket.io-client";

const socket = io("ws://localhost:5000", {
	auth: {
		token: localStorage.getItem("access_token"),
	},
});

// 연결 상태 관리
socket.on("connect", () => {
	console.log("서버에 연결되었습니다");
});

socket.on("disconnect", () => {
	console.log("서버와의 연결이 끊어졌습니다");
});

socket.on("error", (error) => {
	console.error("소켓 오류:", error);
	// 토큰 만료 등의 경우 localStorage에서 토큰 삭제 후 재로그인 처리
	if (error.type === "AUTH_ERROR") {
		localStorage.removeItem("access_token");
		localStorage.removeItem("refresh_token");
		// 로그인 페이지로 리다이렉트
		window.location.href = "/login";
	}
});
```

### 방 참가

```javascript
function joinRoom(roomId, userName) {
	socket.emit("room:join", {
		room_id: roomId,
		user_name: userName,
	});
}

// 방 참가 알림 수신
socket.on("room:join", (data) => {
	console.log(data.message);
	updatePlayerList(data.players);
});
```

### 게임 플레이

```javascript
// 게임 시작 이벤트 수신
socket.on("game:start", (data) => {
	console.log("게임이 시작되었습니다!");
	startCountdown(data.game_time); // 60초 카운트다운 시작
	initializeGame(data.players);
});

// 점수 업데이트 전송
function updateScore(roomId, userName, newScore) {
	socket.emit("game:score_update", {
		room_id: roomId,
		user_name: userName,
		score: newScore,
	});
}

// 상대방 점수 업데이트 수신
socket.on("game:score_update", (data) => {
	updateScoreDisplay(data.players);
});

// 게임 오버 처리
function gameOver(roomId, userName, finalScore) {
	socket.emit("game:game_over", {
		room_id: roomId,
		user_name: userName,
		final_score: finalScore,
	});
}

socket.on("game:game_over", (data) => {
	showGameResult(data.winner, data.final_scores);
});
```

## 오류 처리

### 일반적인 오류 응답

```javascript
socket.on("error", (error) => {
	switch (error.type) {
		case "AUTH_ERROR":
			// JWT 토큰 만료 또는 유효하지 않음
			localStorage.removeItem("access_token");
			localStorage.removeItem("refresh_token");
			redirectToLogin();
			break;
		case "ROOM_NOT_FOUND":
			// 존재하지 않는 방
			showError("방을 찾을 수 없습니다");
			break;
		case "ROOM_FULL":
			// 방이 가득 참
			showError("방이 가득 차서 참가할 수 없습니다");
			break;
		case "GAME_IN_PROGRESS":
			// 이미 게임이 진행 중
			showError("게임이 이미 진행 중입니다");
			break;
		default:
			showError("알 수 없는 오류가 발생했습니다");
	}
});
```

## 성능 최적화

### 이벤트 throttling

점수 업데이트와 같은 빈번한 이벤트는 throttling을 적용하여 성능을 최적화합니다.

```javascript
import { throttle } from "lodash";

// 점수 업데이트를 100ms마다 한 번만 전송
const throttledScoreUpdate = throttle((roomId, userName, score) => {
	socket.emit("game:score_update", {
		room_id: roomId,
		user_name: userName,
		score: score,
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

---

**문서 버전**: 1.0  
**작성일**: 2025년 7월 8일  
**관련 문서**: product-requirements.md, openapi.yaml
