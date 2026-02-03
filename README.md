# jungle10-tetris

크래프톤 정글 10기 | 정글 테트리스

## 팀

| 이름 | [이시영](https://github.com/krsy0411)| [박중섭](https://github.com/crucial-sub) | [이정호](https://github.com/JGLeejungHo) |
| :-: | :-: | :-: | :-: |
| 프로필 | ![이시영](https://avatars.githubusercontent.com/u/90031820?v=4) | ![박중섭](https://avatars.githubusercontent.com/u/87363422?v=4) | ![이정호](https://avatars.githubusercontent.com/u/117905423?v=4) |
| 분류 | 백엔드 | 프론트엔드 | 프론트엔드 |
| 역할 | 인증, 소켓 통신 설계, 게임 시스템 설계, 배포 | 테트리스, 솔로/멀티 모드, 모달, 소켓 연동 | Jinja 템플릿 작성, QA 및 오류 수정 |

## 아키텍처

|        AWS 아키텍처        |        사용자 플로우        |
| :-------------------------: | :-------------------------: |
| ![](/assets/jungle-tetris-awsdiagram.png) | ![](/assets/jungle-tetris-userflow.png) |

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

---

## 참고

- [기획 및 발표 피드백](./FEEDBACK.md)
- [피그마 디자인 작업](https://www.figma.com/design/FxC29DfcYJ9lPCmcHUrRAS/%EC%A0%95%EA%B8%8010%EA%B8%B0-%EB%AF%B8%EB%8B%88%ED%94%8C%EC%A0%9D?node-id=0-1&t=xoCzRPc7qwgFMR0b-1)
- [기능 요구사항 문서](./backend/docs/product-requirements.md)
- [REST API 문서](./backend/docs/openapi.yaml)
- [WebSocket API 문서](./backend/docs/websocket-api.md)
