from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.game_room import GameRoom
from app.models.user import User

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@rooms_bp.route('', methods=['POST'])
@jwt_required()
def create_room():
    """방 생성"""
    try:
        user_id = get_jwt_identity()
        
        # 사용자 정보 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 이미 생성한 방이 있는지 확인
        from app.utils.database import get_db
        db = get_db()
        existing_room = db.game_rooms.find_one({
            'host_user_id': user_id,
            'status': {'$in': ['waiting', 'playing']}
        })
        
        if existing_room:
            return jsonify({'error': '이미 생성한 방이 있습니다'}), 400
        
        # 새 방 생성
        room = GameRoom(
            host_user_id=user_id,
            host_name=user.name
        )
        
        # 방장을 첫 번째 참가자로 추가
        room.add_participant(user_id, user.name)
        room.save()
        
        return jsonify(room.to_dict()), 201
        
    except Exception as e:
        current_app.logger.error(f"Create room error: {str(e)}")
        return jsonify({'error': '방 생성 중 오류가 발생했습니다'}), 500


@rooms_bp.route('/join', methods=['POST'])
@jwt_required()
def join_room():
    """방 참가"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'room_id' not in data:
            return jsonify({'error': '방 번호를 입력해주세요'}), 400
        
        room_id = data['room_id']
        
        # 사용자 정보 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        # 방 참가 가능 여부 확인
        if not room.can_join():
            if room.status == 'playing':
                return jsonify({'error': '게임이 진행 중인 방입니다'}), 400
            elif len(room.participants) >= 2:
                return jsonify({'error': '방이 가득 찼습니다'}), 400
            else:
                return jsonify({'error': '참가할 수 없는 방입니다'}), 400
        
        # 방에 참가
        success, message = room.add_participant(user_id, user.name)
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'message': message,
            'room_id': room_id,
            'players': [p['name'] for p in room.participants]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Join room error: {str(e)}")
        return jsonify({'error': '방 참가 중 오류가 발생했습니다'}), 500


@rooms_bp.route('/<room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    """방 삭제"""
    try:
        user_id = get_jwt_identity()
        
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        # 방장 권한 확인
        if not room.is_host(user_id):
            return jsonify({'error': '방장만 방을 삭제할 수 있습니다'}), 403
        
        # 방 삭제
        room.delete()
        
        return jsonify({'message': '방이 삭제되었습니다'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete room error: {str(e)}")
        return jsonify({'error': '방 삭제 중 오류가 발생했습니다'}), 500


@rooms_bp.route('/<room_id>/leave', methods=['POST'])
@jwt_required()
def leave_room(room_id):
    """방 나가기"""
    try:
        user_id = get_jwt_identity()
        
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        # 방에서 나가기
        success, message = room.remove_participant(user_id)
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        current_app.logger.error(f"Leave room error: {str(e)}")
        return jsonify({'error': '방 나가기 중 오류가 발생했습니다'}), 500


@rooms_bp.route('/<room_id>', methods=['GET'])
@jwt_required()
def get_room_info(room_id):
    """방 정보 조회"""
    try:
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        return jsonify(room.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Get room info error: {str(e)}")
        return jsonify({'error': '방 정보 조회 중 오류가 발생했습니다'}), 500


@rooms_bp.route('', methods=['GET'])
def get_waiting_rooms():
    """대기 중인 방 목록 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # 최대 50개까지만 조회
        
        rooms = GameRoom.get_waiting_rooms(limit)
        
        return jsonify({
            'rooms': rooms,
            'count': len(rooms)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get waiting rooms error: {str(e)}")
        return jsonify({'error': '방 목록 조회 중 오류가 발생했습니다'}), 500
