from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from flask import current_app, request, session
from app.models.user import User
from app.models.game_room import GameRoom


def authenticate_socket(auth_data):
    """Socket.IO 연결 시 JWT 토큰 인증"""
    try:
        token = auth_data.get('token') if auth_data else None
        
        if not token:
            return None, "토큰이 제공되지 않았습니다"
        
        # JWT 토큰 디코딩
        decoded_token = decode_token(token)
        user_id = decoded_token.get('sub')  # JWT identity
        
        if not user_id:
            return None, "유효하지 않은 토큰입니다"
        
        # 사용자 존재 여부 확인
        user = User.find_by_user_id(user_id)
        if not user:
            return None, "사용자를 찾을 수 없습니다"
        
        # 세션에 사용자 정보 저장
        session['user_id'] = user_id
        session['user_name'] = user.name
        
        return user, None
        
    except Exception as e:
        current_app.logger.error(f"Socket authentication error: {str(e)}")
        return None, "인증 실패"


def get_current_user():
    """현재 세션의 사용자 정보 조회"""
    user_id = session.get('user_id')
    if not user_id:
        return None, "인증되지 않은 사용자입니다"
    
    user = User.find_by_user_id(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다"
    
    return user, None


def register_connection_events(socketio):
    """연결 관련 이벤트 등록"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """클라이언트 연결 시"""
        try:
            # 인증 정보 확인
            user, error = authenticate_socket(auth)
            
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
        current_app.logger.info(f"Socket disconnected")


def register_room_events(socketio):
    """방 관련 이벤트 등록"""
    
    @socketio.on('room:join')
    def handle_room_join(data):
        """방 참가"""
        try:
            # 인증 확인
            user, error = get_current_user()
            
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
            
        except Exception as e:
            current_app.logger.error(f"Room join error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '방 참가 중 오류가 발생했습니다'})
    
    @socketio.on('room:leave')
    def handle_room_leave(data):
        """방 나가기"""
        try:
            # 인증 확인
            user, error = get_current_user()
            
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
    
    @socketio.on('game:start')
    def handle_game_start(data):
        """게임 시작 (방장이 실행)"""
        try:
            # 인증 확인
            user, error = get_current_user()
            
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
        """실시간 점수 업데이트"""
        try:
            # 인증 확인
            user, error = get_current_user()
            
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
    
    @socketio.on('game:game_over')
    def handle_game_over(data):
        """게임 오버 처리"""
        try:
            # 인증 확인
            user, error = get_current_user()
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            final_score = data.get('final_score', 0)
            
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
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
                # 승자 결정
                winner = max(room.participants, key=lambda p: p.get('score', 0))
                loser = min(room.participants, key=lambda p: p.get('score', 0))
                final_scores = {p['name']: p.get('score', 0) for p in room.participants}
                
                # 게임 종료
                room.end_game()
                
                # 게임 오버 알림을 방 내 모든 사용자에게 브로드캐스트
                socketio.emit('game:game_over', {
                    'room_id': room_id,
                    'game_over': True,
                    'winner': winner['name'],
                    'loser': loser['name'],
                    'final_scores': final_scores
                }, room=room_id)
            
        except Exception as e:
            current_app.logger.error(f"Game over error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '게임 종료 처리 중 오류가 발생했습니다'})


def register_all_events(socketio):
    """모든 Socket.IO 이벤트 등록"""
    register_connection_events(socketio)
    register_room_events(socketio)
    register_game_events(socketio)
