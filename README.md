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

### 7/8(화)

- 무조건 정상적으로 돌아가는게 목표
- 와이어프레임과 디자인 단계에서 '어떤 버튼을 클릭했을 때 이런 상황이 생긴다. 알람이 발생한다면, 알람이 어떠한 식으로 UI에 반영된다' 등의 구체적인 내용이 없으면 셋이서 구현하고보니 의도와 다른 식으로 구현될 가능성이 높음. 따라서 최대한 구체적으로 설계를 해야할 것.
- SSR을 쓸 수 있는 부분이 메인에서는 힘들 것 같아서 다른 페이지들에서 최대한 SSR을 사용하셔야함
- 소켓io에 대한 숙련도가 우려됨
- 소켓io는 시영님만 써봤고 백엔드 역할도 시영님이 하시는 만큼, 아무래도 다른 분들은 소켓이 뭔지도 모르고 그냥 사용만 해보고 끝날 가능성이 높아보임. 이를 조심해서 역할 분배를 너무 백/프론트로 안 나누는 게 좋아보임.
