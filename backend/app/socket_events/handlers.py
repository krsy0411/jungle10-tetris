from flask_socketio import emit, join_room, leave_room, disconnect
from flask import current_app, request
from flask_jwt_extended import decode_token
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


def get_current_user_from_socket():
    """Socket.IO 요청에서 쿠키의 JWT 토큰으로 사용자 정보 조회"""
    try:
        # 쿠키에서 JWT 토큰 추출
        token = None
        if hasattr(request, 'cookies'):
            token = request.cookies.get('access_token')
        
        if not token:
            return None, "인증 토큰이 필요합니다"
        
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        user = User.find_by_user_id(user_id)
        if not user:
            return None, "사용자를 찾을 수 없습니다"
        
        return user, None
        
    except Exception as e:
        current_app.logger.error(f"Get user from socket error: {str(e)}")
        return None, "인증 실패"


def register_connection_events(socketio):
    """연결 관련 이벤트 등록"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """클라이언트 연결 시 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰 추출
            token = None
            
            # request.cookies에서 access_token 추출
            if hasattr(request, 'cookies'):
                token = request.cookies.get('access_token')
            
            # 쿠키에서 토큰을 찾지 못한 경우 auth 파라미터 확인 (fallback)
            if not token and auth and isinstance(auth, dict) and 'token' in auth:
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
        """방 참가 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
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

            # 참가자 수가 2명이 되면 서버가 자동으로 게임 시작 알림을 브로드캐스트
            if len(room.participants) == 2:
                # 게임 시작 처리 (room.start_game() 등 필요시 호출)
                if hasattr(room, 'start_game'):
                    room.start_game()
                players = [{'name': p['name'], 'user_id': p['user_id'], 'score': 0} for p in room.participants]
                socketio.emit('game:start', {
                    'room_id': room_id,
                    'players': players,
                    'game_time': 60  # 60초 게임
                }, room=room_id)
        except Exception as e:
            current_app.logger.error(f"Room join error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '방 참가 중 오류가 발생했습니다'})
    
    @socketio.on('room:leave')
    def handle_room_leave(data):
        """방 나가기 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
            
            if error:
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            room_id = data.get('room_id')
            if not room_id:
                emit('error', {'type': 'VALIDATION_ERROR', 'message': '방 번호가 필요합니다'})
                return
            
            # 방 조회
            room = GameRoom.find_by_room_id(room_id)
            
            # DB에서 참가자 제거 (참가자가 없으면 방 삭제)
            success = room.remove_participant(user.user_id)
            
            # Socket.IO 방에서 나가기
            leave_room(room_id)
            
            # 성공 응답
            emit('room:leave', {
                'message': '방을 나갔습니다',
                'user_id': user.user_id,
            })

            # 클라이언트 연결도 끊기 (가능한 경우)
            try:
                disconnect()
            except Exception as e:
                current_app.logger.warning(f"Disconnect after leave_room failed: {str(e)}")
            
        except Exception as e:
            current_app.logger.error(f"Room leave error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '방 나가기 중 오류가 발생했습니다'})


def register_game_events(socketio):
    """게임 관련 이벤트 등록"""
    
    @socketio.on('game:score_update')
    def handle_score_update(data):
        """실시간 점수 업데이트 (쿠키 기반 JWT 인증)"""
        try:
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
            
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
        """게임 종료 처리 (쿠키 기반 JWT 인증) - 플레이어가 게임 완료 시 호출"""
        try:
            current_app.logger.info(f"Game end request received: {data}")
            
            # 쿠키에서 JWT 토큰으로 사용자 인증
            user, error = get_current_user_from_socket()
            if error:
                current_app.logger.error(f"Authentication failed in game:end: {error}")
                emit('error', {'type': 'AUTH_ERROR', 'message': error})
                return
            
            current_app.logger.info(f"User {user.user_id} requesting game end")
            
            room_id = data.get('room_id')
            final_score = data.get('score', 0)

            # 방 조회
            room = GameRoom.find_by_room_id(room_id)
            if not room:
                current_app.logger.error(f"Room not found: {room_id}")
                emit('error', {'type': 'ROOM_NOT_FOUND', 'message': '존재하지 않는 방입니다'})
                return
            
            current_app.logger.info(f"Room {room_id} found with {len(room.participants)} participants")
            
            # 최종 점수 업데이트
            room.update_participant_score(user.user_id, final_score)
            current_app.logger.info(f"Updated score for user {user.user_id}: {final_score}")
            
            # 모든 플레이어가 게임을 마쳤는지 확인
            all_finished = all(p.get('score', 0) > 0 for p in room.participants)
            current_app.logger.info(f"All players finished: {all_finished}")
            
            result = {
                'room_id': room_id
            }
            
            if all_finished:
                current_app.logger.info(f"All players finished game in room {room_id}")
                
                scores = {p['user_id']: p.get('score', 0) for p in room.participants}
                current_app.logger.info(f"Final scores: {scores}")
                
                # 승부 결정 (점수 비교)
                max_score = max(scores.values())
                winners = [user_id for user_id, score in scores.items() if score == max_score]
                
                is_draw = len(winners) > 1
                winner_user_id = None if is_draw else winners[0]
                
                current_app.logger.info(f"Game result - max_score: {max_score}, winners: {winners}, is_draw: {is_draw}")
                
                # 게임 종료
                room.end_game(scores)
                current_app.logger.info(f"Room {room_id} game ended")
                
                # 게임 기록 저장
                from app.models.game_record import GameRecord
                players_data = [
                    {'user_id': p['user_id'], 'name': p['name'], 'score': p.get('score', 0)}
                    for p in room.participants
                ]
                GameRecord.create_multiplayer_record(
                    room_id, players_data, scores, winner_user_id, 60
                )
                current_app.logger.info(f"Game record saved for room {room_id}")
                
                # 사용자 통계 업데이트
                for participant in room.participants:
                    participant_user = User.find_by_user_id(participant['user_id'])
                    if participant_user:
                        if is_draw:
                            game_result = 'draw'
                        else:
                            game_result = 'win' if participant['user_id'] == winner_user_id else 'loss'
                        participant_user.update_stats(
                            score_gained=participant.get('score', 0),
                            game_result=game_result
                        )
                        current_app.logger.info(f"Updated stats for user {participant['user_id']}: {game_result}")
                
                # 결과 메시지 설정
                if is_draw:
                    result.update({
                        'status': 'finished',
                        'final_scores': scores,
                        'is_draw': True
                    })
                    current_app.logger.info(f"Game ended in draw for room {room_id}")
                else:
                    result.update({
                        'status': 'finished',
                        'final_scores': scores,
                        'winner': winner_user_id,
                        'is_draw': False
                    })
                    current_app.logger.info(f"Game ended with winner {winner_user_id} for room {room_id}")
                
                # 게임 종료 결과를 방 내 모든 사용자에게 브로드캐스트
                socketio.emit('game:end', result, room=room_id)
                current_app.logger.info(f"Game end result broadcasted to room {room_id}")
            else:
                current_app.logger.info(f"Waiting for other players to finish in room {room_id}")
                # waiting 상태를 game:end 응답에 포함 (별도 이벤트 emit하지 않음)
                result.update({
                    'message': '상대방이 게임을 완료하기를 기다리는 중...',
                    'status': 'waiting',
                })
                emit('game:end', result)
                current_app.logger.info(f"Waiting response sent to user {user.user_id}")
        except Exception as e:
            current_app.logger.error(f"Game end error: {str(e)}")
            emit('error', {'type': 'SERVER_ERROR', 'message': '게임 종료 처리 중 오류가 발생했습니다'})

def register_all_events(socketio):
    """모든 Socket.IO 이벤트 등록"""
    register_connection_events(socketio)
    register_room_events(socketio)
    register_game_events(socketio)
