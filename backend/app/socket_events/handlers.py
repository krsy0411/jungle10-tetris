from flask_socketio import emit, join_room, leave_room, disconnect
from flask import current_app, request
from flask_jwt_extended import decode_token, get_jwt_identity
from app.models.user import User
from app.models.game_room import GameRoom


def authenticate_socket_jwt(token):
    """Socket.IO 연결 시 JWT 기반 인증"""
    try:
        if not token:
            return None, "인증 토큰이 필요합니다"
        
        # JWT 토큰 검증
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']  # JWT subject claim
        except Exception as e:
            return None, "유효하지 않은 토큰입니다"
        
        # 사용자 존재 여부 확인
        user = User.find_by_user_id(user_id)
        if not user:
            return None, "사용자를 찾을 수 없습니다"
        
        return user, None
        
    except Exception as e:
        current_app.logger.error(f"Socket JWT authentication error: {str(e)}")
        return None, "인증 실패"


<<<<<<< HEAD
def get_current_user_from_jwt(token):
    """JWT 토큰에서 현재 사용자 정보 조회"""
    try:
=======
def get_current_user_from_socket():
    """Socket.IO 요청에서 쿠키의 JWT 토큰으로 사용자 정보 조회"""
    try:
        # 쿠키에서 JWT 토큰 추출
        token = None
        if hasattr(request, 'cookies'):
            token = request.cookies.get('access_token_cookie')
        
>>>>>>> front
        if not token:
            return None, "인증 토큰이 필요합니다"
        
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        user = User.find_by_user_id(user_id)
        if not user:
            return None, "사용자를 찾을 수 없습니다"
        
        return user, None
        
    except Exception as e:
<<<<<<< HEAD
        current_app.logger.error(f"Get user from JWT error: {str(e)}")
=======
        current_app.logger.error(f"Get user from socket error: {str(e)}")
>>>>>>> front
        return None, "인증 실패"


def register_connection_events(socketio):
    """연결 관련 이벤트 등록"""
    
    @socketio.on('connect')
    def handle_connect(auth):
<<<<<<< HEAD
        """클라이언트 연결 시 (JWT 기반 인증)"""
        try:
            # JWT 토큰에서 인증 정보 추출
            token = None
            if auth and isinstance(auth, dict) and 'token' in auth:
=======
        """클라이언트 연결 시 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰 추출
            token = None
            
            # request.cookies에서 access_token_cookie 추출
            if hasattr(request, 'cookies'):
                token = request.cookies.get('access_token_cookie')
            
            # 쿠키에서 토큰을 찾지 못한 경우 auth 파라미터 확인 (fallback)
            if not token and auth and isinstance(auth, dict) and 'token' in auth:
>>>>>>> front
                token = auth['token']
            
            # JWT 기반 인증 확인
            user, error = authenticate_socket_jwt(token)
            
            if error:
                current_app.logger.warning(f"Socket connection denied: {error}")
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                disconnect()
                return False
            
            # 연결 성공
            current_app.logger.info(f"User {user.user_id} connected via socket")
            emit('connect_success', {
                'user_id': user.user_id,
                'name': user.name,
                'message': '서버에 연결되었습니다'
            })
            
        except Exception as e:
            current_app.logger.error(f"Socket connect error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '연결 중 오류가 발생했습니다'})
            disconnect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """클라이언트 연결 해제 시"""
        # JWT 정보는 연결 시에만 확인하므로 disconnect에서는 단순 로그
        current_app.logger.info(f"Socket disconnected")


def register_room_events(socketio):
    """방 관련 이벤트 등록"""
    
    @socketio.on('room:join')
    def handle_room_join(data):
<<<<<<< HEAD
        """방 참가 (JWT 인증)"""
        try:
            # JWT 토큰 인증
            token = data.get('token')
            user, error = get_current_user_from_jwt(token)
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
=======
        """방 참가 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
>>>>>>> front
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
<<<<<<< HEAD
            
=======
>>>>>>> front
            # 방 조회
            room = GameRoom.find_by_room_id(room_id)
            if not room:
                emit('error', {'type': 'ROOM_NOT_FOUND', 'message': '존재하지 않는 방입니다'})
                return
<<<<<<< HEAD
            
            # Socket.IO 방에 참가
            join_room(room_id)
            
            # 방 참가 알림을 방 내 모든 사용자에게 브로드캐스트
            socketio.emit('room:join', {
                'room_id': room_id,
                'user_name': user.name,
                'message': f'{user.name}님이 방에 참가했습니다'
            }, room=room_id)
            
            # 방 정보 업데이트 알림
            socketio.emit('room:update', {
                'room_id': room_id,
                'status': room.status,
                'players': [p['name'] for p in room.participants]
            }, room=room_id)
            
=======
            # Socket.IO 방에 참가
            join_room(room_id)

            # 참가자 수가 2명이 되면 서버가 자동으로 게임 시작 알림을 브로드캐스트
            if len(room.participants) == 2:
                # 게임 시작 처리 (room.start_game() 등 필요시 호출)
                if hasattr(room, 'start_game'):
                    room.start_game()
                players = [{'name': p['name'], 'score': 0} for p in room.participants]
                socketio.emit('game:start', {
                    'room_id': room_id,
                    'players': players,
                    'game_time': 60  # 60초 게임
                }, room=room_id)
>>>>>>> front
        except Exception as e:
            current_app.logger.error(f"Room join error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '방 참가 중 오류가 발생했습니다'})
    
    @socketio.on('room:leave')
    def handle_room_leave(data):
<<<<<<< HEAD
        """방 나가기 (JWT 인증)"""
        try:
            # JWT 토큰 인증
            token = data.get('token')
            user, error = get_current_user_from_jwt(token)
=======
        """방 나가기 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
>>>>>>> front
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
            
            # 방 나가기 알림을 방 내 다른 사용자에게 브로드캐스트
            socketio.emit('room:leave', {
                'room_id': room_id,
                'user_name': user.name,
                'message': f'{user.name}님이 방을 나갔습니다'
            }, room=room_id)
            
            # Socket.IO 방에서 나가기
            leave_room(room_id)
            
        except Exception as e:
            current_app.logger.error(f"Room leave error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '방 나가기 중 오류가 발생했습니다'})


def register_game_events(socketio):
    """게임 관련 이벤트 등록"""
    
<<<<<<< HEAD
    @socketio.on('game:start')
    def handle_game_start(data):
        """게임 시작 (방장이 실행, JWT 인증)"""
        try:
            # JWT 토큰 인증
            token = data.get('token')
            user, error = get_current_user_from_jwt(token)
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
            
            # 방 조회
            room = GameRoom.find_by_room_id(room_id)
            if not room:
                emit('error', {'type': 'ROOM_NOT_FOUND', 'message': '존재하지 않는 방입니다'})
                return
            
            # 방장 권한 확인
            if not room.is_host(user.user_id):
                emit('error', {'type': 'PERMISSION_DENIED', 'message': '방장만 게임을 시작할 수 있습니다'})
                return
            
            # 게임 시작
            success, message = room.start_game()
            if not success:
                emit('error', {'type': 'GAME_START_FAILED', 'message': message})
                return
            
            # 게임 시작 알림을 방 내 모든 사용자에게 브로드캐스트
            players = [{'name': p['name'], 'score': 0} for p in room.participants]
            
            socketio.emit('game:start', {
                'room_id': room_id,
                'players': players,
                'game_time': 60  # 60초 게임
            }, room=room_id)
            
        except Exception as e:
            current_app.logger.error(f"Game start error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '게임 시작 중 오류가 발생했습니다'})
    
    @socketio.on('game:score_update')
    def handle_score_update(data):
        """실시간 점수 업데이트 (JWT 인증)"""
        try:
            # JWT 토큰 인증
            token = data.get('token')
            user, error = get_current_user_from_jwt(token)
=======
    # 게임 시작은 방장이 아닌, 두 명이 모두 입장하면 서버가 자동으로 알림을 보냄

    # 기존 game:start 이벤트 핸들러는 제거

    # 방 참가 이벤트에서 참가자 수가 2명이 되면 게임 시작 알림을 브로드캐스트
    # (room:join 이벤트 내부에서 처리)
    
    @socketio.on('game:score_update')
    def handle_score_update(data):
        """실시간 점수 업데이트 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
>>>>>>> front
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            score = data.get('score', 0)
            
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
            
            # 방 조회 및 점수 업데이트
            room = GameRoom.find_by_room_id(room_id)
            if room:
                room.update_participant_score(user.user_id, score)
                
                # 업데이트된 플레이어 점수를 방 내 모든 사용자에게 브로드캐스트
                players = [
                    {'name': p['name'], 'score': p.get('score', 0)} 
                    for p in room.participants
                ]
                
                socketio.emit('game:score_update', {
                    'room_id': room_id,
                    'players': players
                }, room=room_id)
            
        except Exception as e:
            current_app.logger.error(f"Score update error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '점수 업데이트 중 오류가 발생했습니다'})
    
    @socketio.on('game:end')
    def handle_game_end(data):
<<<<<<< HEAD
        """게임 종료 처리 (JWT 인증) - 플레이어가 게임 완료 시 호출"""
        try:
            # JWT 토큰 인증
            token = data.get('token')
            user, error = get_current_user_from_jwt(token)
=======
        """게임 종료 처리 (쿠키 기반 JWT 인증) - 플레이어가 게임 완료 시 호출"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
>>>>>>> front
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            final_score = data.get('score', 0)
            
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
            
            if not isinstance(final_score, int) or final_score < 0:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '유효하지 않은 점수입니다'})
                return
            
            # 방 조회
            room = GameRoom.find_by_room_id(room_id)
            if not room:
                emit('error', {'type': 'ROOM_NOT_FOUND', 'message': '존재하지 않는 방입니다'})
                return
            
            # 최종 점수 업데이트
            room.update_participant_score(user.user_id, final_score)
            
            # 모든 플레이어가 게임을 마쳤는지 확인
            all_finished = all(p.get('score', 0) > 0 for p in room.participants)
            
            if all_finished:
                # 승자 결정 (점수가 가장 높은 플레이어)
                winner = max(room.participants, key=lambda p: p.get('score', 0))
                scores = {p['user_id']: p.get('score', 0) for p in room.participants}
                
                # 게임 종료
                room.end_game(scores)
                
                # 게임 기록 저장
                from app.models.game_record import GameRecord
                players_data = [
                    {'user_id': p['user_id'], 'name': p['name'], 'score': p.get('score', 0)}
                    for p in room.participants
                ]
                
                GameRecord.create_multiplayer_record(
                    room_id, players_data, scores, winner['user_id'], 60
                )
                
                # 사용자 통계 업데이트
                for participant in room.participants:
                    participant_user = User.find_by_user_id(participant['user_id'])
                    if participant_user:
                        is_winner = participant['user_id'] == winner['user_id']
                        game_result = 'win' if is_winner else 'loss'
                        participant_user.update_stats(
                            score_gained=participant.get('score', 0),
                            game_result=game_result
                        )
                
                # 게임 종료 결과를 방 내 모든 사용자에게 브로드캐스트
                socketio.emit('game:end', {
                    'room_id': room_id,
                    'message': '게임이 종료되었습니다',
                    'final_scores': scores,
                    'winner': winner['name']
                }, room=f'room_{room_id}')
            else:
                # 대기 중 알림 (상대방이 아직 완료하지 않음)
                socketio.emit('game:waiting', {
                    'room_id': room_id,
                    'message': '상대방이 게임을 완료하기를 기다리는 중...',
                    'your_score': final_score
                }, room=request.sid)  # 현재 사용자에게만 전송
            
        except Exception as e:
            current_app.logger.error(f"Game end error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '게임 종료 처리 중 오류가 발생했습니다'})

def register_all_events(socketio):
    """모든 Socket.IO 이벤트 등록"""
    register_connection_events(socketio)
    register_room_events(socketio)
    register_game_events(socketio)
