# jungle10-tetris

크래프톤 정글 10기 | 정글 테트리스

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

### 7/8(화)

- 무조건 정상적으로 돌아가는게 목표
- 와이어프레임과 디자인 단계에서 '어떤 버튼을 클릭했을 때 이런 상황이 생긴다. 알람이 발생한다면, 알람이 어떠한 식으로 UI에 반영된다' 등의 구체적인 내용이 없으면 셋이서 구현하고보니 의도와 다른 식으로 구현될 가능성이 높음. 따라서 최대한 구체적으로 설계를 해야할 것.
- SSR을 쓸 수 있는 부분이 메인에서는 힘들 것 같아서 다른 페이지들에서 최대한 SSR을 사용하셔야함
- 소켓io에 대한 숙련도가 우려됨
- 소켓io는 시영님만 써봤고 백엔드 역할도 시영님이 하시는 만큼, 아무래도 다른 분들은 소켓이 뭔지도 모르고 그냥 사용만 해보고 끝날 가능성이 높아보임. 이를 조심해서 역할 분배를 너무 백/프론트로 안 나누는 게 좋아보임.
