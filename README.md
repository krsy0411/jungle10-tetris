# jungle10-tetris

크래프톤 정글 10기 | 정글 테트리스
- [기획 및 발표 피드백](./FEEDBACK.md)
- [피그마 디자인 작업](https://www.figma.com/design/FxC29DfcYJ9lPCmcHUrRAS/%EC%A0%95%EA%B8%8010%EA%B8%B0-%EB%AF%B8%EB%8B%88%ED%94%8C%EC%A0%9D?node-id=0-1&t=xoCzRPc7qwgFMR0b-1)

## 👨‍💻 팀

| 이름 | [이시영](https://github.com/krsy0411)| [박중섭](https://github.com/crucial-sub) | [이정호](https://github.com/JGLeejungHo) |
| :-: | :-: | :-: | :-: |
| 프로필 | ![이시영](https://avatars.githubusercontent.com/u/90031820?v=4) | ![박중섭](https://avatars.githubusercontent.com/u/87363422?v=4) | ![이정호](https://avatars.githubusercontent.com/u/117905423?v=4) |
| 분류 | 백엔드 | 프론트엔드 | 프론트엔드 |
| 역할 | 인증, 소켓 통신 설계, 게임 시스템 설계, 배포 | 테트리스, 솔로/멀티 모드, 모달, 소켓 연동 | Jinja 템플릿 작성, QA 및 오류 수정 |

## 🛠️ 기술 스택

### 프론트엔드
<p style="display:flex; gap:10px">
    <img src="https://www.vectorlogo.zone/logos/javascript/javascript-icon.svg" alt="JavaScript" width="40px" height="40px">
    <img src="https://www.vectorlogo.zone/logos/tailwindcss/tailwindcss-icon.svg" alt="TailwindCSS" width="40px" height="40px">
    <img src="https://www.vectorlogo.zone/logos/socketio/socketio-icon.svg" alt="TailwindCSS" width="40px" height="40px">
</p>

### 백엔드
<p style="display:flex; gap:10px">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="40px" height="40px">
    <img src="https://www.vectorlogo.zone/logos/palletsprojects_flask/palletsprojects_flask-icon~v2.svg" alt="Flask" width="40px" height="40px">
    <img src="https://www.vectorlogo.zone/logos/socketio/socketio-icon.svg" alt="Socket.IO" width="40px" height="40px">
    <img src="https://www.vectorlogo.zone/logos/pocoo_jinja/pocoo_jinja-icon.svg" alt="Jinja2" width="40px" height="40px">
</p>

### 데이터베이스
<p style="display:flex; gap:10px">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" alt="MongoDB" width="40px" height="40px">
</p>

### 배포
<p style="display:flex; gap:10px">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/amazonwebservices/amazonwebservices-plain-wordmark.svg" alt="AWS" width="40px" height="40px">
</p>

## 아키텍처
```markdown
┌────────────────────────────────────────────────────────────────────────────────┐
│                            AWS EC2 (우분투) 배포 환경                              │
│                                                                                │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │                           FRONTEND (브라우저)                                │ │
│ │                                                                            │ │
│ │  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐ │ │
│ │  │login.html│  │ main.html │  │ solo.html │  │ multi.html│  │ranking.html│ │ │
│ │  │          │  │           │  │           │  │           │  │            │ │ │
│ │  │ SSR 렌더링 │  │ SSR 렌더링 │  │  테트리스    │  │ 멀티플레이  │   │ SSR 렌더링  │ │ │
│ │  │ JWT 쿠키  │  │ Socket.IO │  │ 게임 로직   │  │ 대전 게임   │   │ 랭킹 조회    │ │ │
│ │  │ 인증      │  │ 연결       │  │ Canvas    │  │ Socket.IO │  │            │ │ │
│ │  └──────────┘  └───────────┘  └───────────┘  └───────────┘  └───────────┘  │ │
│ │                     │               │              │                       │ │
│ │              ┌──────┴──────┐        │              │                       │ │
│ │              │ JavaScript  │        │              │                       │ │
│ │              │ + Socket.IO │        │              │                       │ │
│ │              │ + TailwindCSS│       │              │                       │ │
│ │              └─────────────┘        │              │                       │ │
│ └─────────────────────────────────────┼──────────────┼───────────────────────┘ │
│                                       │              │                         │
│    ┌──────────────────────────────────┼──────────────┼─────────────────────┐   │
│    │  HTTPS/WSS (Socket.IO 4.7.2)     │              │                     │   │
│    └──────────────────────────────────┼──────────────┼─────────────────────┘   │
│                                       │              │                         │
│ ┌─────────────────────────────────────┼──────────────┼───────────────────────┐ │
│ │                    BACKEND (Flask + Socket.IO)                             │ │
│ │                                     │              │                       │ │
│ │  ┌────────────────┐  ┌─────────────┼──────────────┼────────────┐          │ │
│ │  │ Flask App      │  │             │              │            │          │ │
│ │  │ (run.py)       │  │        main.py (라우트 통합)               │          │ │
│ │  │                │  │             │              │            │          │ │
│ │  │ ├─ Jinja2      │  │  ┌──────────┴──────────────┴─────────┐  │          │ │
│ │  │ ├─ Flask-CORS  │  │  │       라우트 핸들러                  │  │           │ │
│ │  │ ├─ JWT         │  │  │                                   │  │          │ │
│ │  │ └─ Socket.IO   │  │  │ ├─ GET /login, /register (SSR)    │  │          │ │
│ │  └────────────────┘  │  │ ├─ POST /login, /register (Form)  │  │          │ │
│ │                      │  │ ├─ GET /main, /solo, /multi (SSR) │  │          │ │
│ │  ┌────────────────┐  │  │ ├─ GET /ranking (SSR)             │  │          │ │
│ │  │ Socket.IO      │  │  │ ├─ POST /api/auth/refresh         │  │          │ │
│ │  │ Handlers       │  │  │ ├─ POST /api/rooms/create         │  │          │ │
│ │  │                │  │  │ ├─ POST /api/rooms/join           │  │          │ │
│ │  │ ├─ connect     │  │  │ ├─ POST /api/game/solo/start      │  │          │ │
│ │  │ ├─ room:join   │  │  │ ├─ POST /api/game/solo/end        │  │          │ │
│ │  │ ├─ room:leave  │  │  │ ├─ GET  /api/ranking/score        │  │          │ │
│ │  │ ├─ game:start  │  │  │ └─ GET  /api/ranking/wins         │  │          │ │
│ │  │ ├─ game:score  │  │  └───────────────────────────────────┘  │          │ │
│ │  │ └─ game:end    │  │                                         │          │ │
│ │  └────────────────┘  └─────────────────────────────────────────┘          │ │
│ │                                                                           │ │
│ │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│ │  │                            모델 레이어                                  │ │ │
│ │  │                                                                      │ │ │
│ │  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐              │ │ │
│ │  │  │ User       │  │ GameRoom     │  │ GameRecord       │              │ │ │
│ │  │  │ Model      │  │ Model        │  │ Model            │              │ │ │
│ │  │  │            │  │              │  │                  │              │ │ │
│ │  │  │├─user_id   │  │├─room_id     │  │├─user_id         │              │ │ │
│ │  │  │├─name      │  │├─host_id     │  │├─game_type       │              │ │ │
│ │  │  │├─password  │  │├─status      │  │├─score           │              │ │ │
│ │  │  │├─wins      │  │├─players[]   │  │├─opponent_id     │              │ │ │
│ │  │  │├─high_score│  │├─created_at  │  │├─is_winner       │              │ │ │
│ │  │  │└─created_at│  │└─updated_at  │  │└─played_at       │              │ │ │
│ │  │  └────────────┘  └──────────────┘  └──────────────────┘              │ │ │
│ │  └──────────────────────────────────────────────────────────────────────┘ │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                       │
│ ┌─────────────────────────────────────┼─────────────────────────────────────┐ │
│ │                           DATABASE  │                                     │ │
│ │                                     │                                     │ │
│ │  ┌──────────────────────────────────┼──────────────────────────────────┐  │ │
│ │  │             MongoDB (로컬 또는 원격)                                   │  │ │
│ │  │                                  │                                  │  │ │
│ │  │  ┌─────────────┐  ┌─────────────┐┌─────────────┐                    │  │ │
│ │  │  │  users      │  │   rooms     ││game_records │                    │  │ │
│ │  │  │ Collection  │  │ Collection  ││ Collection  │                    │  │ │
│ │  │  │             │  │             ││             │                    │  │ │
│ │  │  │ - user_id   │  │ - room_id   ││ - user_id   │                    │  │ │
│ │  │  │ - name      │  │ - host_id   ││ - game_type │                    │  │ │
│ │  │  │ - password  │  │ - status    ││ - score     │                    │  │ │
│ │  │  │ - wins      │  │ - players[] ││ - opponent  │                    │  │ │
│ │  │  │ - high_score│  │ - created_at││ - is_winner │                    │  │ │
│ │  │  │ - jwt_info  │  │ - updated_at││ - played_at │                    │  │ │
│ │  │  └─────────────┘  └─────────────┘└─────────────┘                    │  │ │
│ │  └─────────────────────────────────────────────────────────────────────┘  │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│ ┌───────────────────────────────────────────────────────────────────────────┐ │
│ │                              인증 시스템                                     │ │
│ │                                                                           │ │
│ │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│ │  │                     JWT 기반 쿠키 인증                                  │  │ │
│ │  │                                                                      │  │ │
│ │  │  ┌─────────────────┐    ┌─────────────────┐                          │  │ │
│ │  │  │ Access Token    │    │ Refresh Token   │                          │  │ │
│ │  │  │ - 2시간 만료      │    │ - 7일 만료        │                          │  │ │
│ │  │  │ - httpOnly 쿠키  │    │ - httpOnly 쿠키  │                          │  │ │
│ │  │  │ - HS256 서명     │    │ - HS256 서명     │                          │  │ │
│ │  │  └─────────────────┘    └─────────────────┘                          │  │ │
│ │  └──────────────────────────────────────────────────────────────────────┘  │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │                           실시간 통신 플로우                                    │ │
│ │                                                                             │ │
│ │ 1. 브라우저 → 쿠키의 JWT 토큰으로 Socket.IO 연결                                   │ │
│ │ 2. 방 생성/참가 → Socket 이벤트로 실시간 알림                                       │ │
│ │ 3. 게임 시작 → 2명 참가 시 자동으로 game:start 이벤트                                │ │
│ │ 4. 게임 중 → 점수 변경 시 game:score_update 실시간 동기화                           │ │
│ │ 5. 게임 종료 → game:end 이벤트로 승부 결과 전송                                     │ │
│ │ 6. 연결 해제 → 자동 방 정리 및 상대방에게 알림                                        │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 페이지

|        로그인         |        회원가입        |
| :------------------: | :--------------------: |
| ![](/assets/login2.png) | ![](/assets/join.png) |

|        메인         |       랭킹       |
| :-----------------: | :-------------: |
| ![](/assets/main.png) | ![](/assets/ranking.png) |

|     키 설명 모달     |     방 찾기 모달     |
| :------------------: | :------------------: |
| ![](/assets/keyexplain_modal.png) | ![](/assets/findroom_modal1.png) |

---

## 테트리스 - 솔로플레이

|     혼자하기 입장      |        블럭 이동         |
| :-------------------: | :---------------------: |
| ![](/assets/solo_enter.gif) | ![](/assets/block_move.gif) |

|       블럭 회전       |        하드 드롭         |
| :-------------------: | :---------------------: |
| ![](/assets/block_rotate.gif) | ![](/assets/hard_drop.gif) |

|       줄 지우기        |   솔로 게임 종료 및 결과 창   |
| :-------------------: | :---------------------: |
| ![](/assets/erase_line.gif) | ![](/assets/game_end_solo.gif) |

---

## 테트리스 - 멀티플레이

|   방 생성 및 대기   | (상대방 시점) 방 찾아서 입장 |
| :----------------: | :--------------------------: |
| ![](/assets/create_room.gif) | ![](/assets/join_room.gif) |

| 실시간 상대 점수 상승 |         먼저 사망 시 대기         |
| :------------------: | :----------------------: |
| ![](/assets/opponent_score.gif) | ![](/assets/waiting_end.png) |

| 멀티 게임 종료 및 결과 창 |
| :-----: |
| ![](/assets/game_end_multi.gif)

| 결과 모달(승리) | 결과 모달(패배) | 결과 모달(무승부) |
| :-------------: | :-------------: | :---------------: |
| ![](/assets/result_win.png) | ![](/assets/result_lose.png) | ![](/assets/result_draw.png) |
