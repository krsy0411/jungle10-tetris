from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models.user import User
from app.models.game_room import GameRoom
from app.models.game_record import GameRecord

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/solo/start', methods=['POST'])
@jwt_required()
def start_solo_game():
    """솔로 게임 시작"""
    try:
        user_id = get_jwt_identity()
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        return jsonify({
            'game_time': 60,  # 60초 게임
            'message': '솔로 게임이 시작되었습니다'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Start solo game error: {str(e)}")
        return jsonify({'error': '솔로 게임 시작 중 오류가 발생했습니다'}), 500


@game_bp.route('/solo/end', methods=['POST'])
@jwt_required()
def end_solo_game():
    """솔로 게임 종료"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'score' not in data:
            return jsonify({'error': '점수를 입력해주세요'}), 400
        
        score = data.get('score', 0)
        if not isinstance(score, int) or score < 0:
            return jsonify({'error': '유효하지 않은 점수입니다'}), 400
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 개인 최고 점수 확인
        personal_best = score > user.solo_high_score
        
        # 게임 기록 저장
        GameRecord.create_solo_record(user_id, user.name, score, 60)
        
        # 사용자 통계 업데이트
        if personal_best:
            user.solo_high_score = score
        user.total_score += score
        user.games_played += 1
        user.save()
        
        return jsonify({
            'message': '게임 결과가 저장되었습니다',
            'final_score': score,
            'personal_best': personal_best,
            'previous_best': user.solo_high_score if not personal_best else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"End solo game error: {str(e)}")
        return jsonify({'error': '솔로 게임 종료 중 오류가 발생했습니다'}), 500


@game_bp.route('/versus/start', methods=['POST'])
@jwt_required()
def start_versus_game():
    """대전 게임 시작"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'room_id' not in data:
            return jsonify({'error': '방 번호를 입력해주세요'}), 400
        
        room_id = data['room_id']
        
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        # 방장 권한 확인
        if not room.is_host(user_id):
            return jsonify({'error': '방장만 게임을 시작할 수 있습니다'}), 403
        
        # 게임 시작
        success, message = room.start_game()
        if not success:
            return jsonify({'error': message}), 400
        
        # 참가자 정보
        players = [
            {'name': p['name'], 'score': 0} 
            for p in room.participants
        ]
        
        return jsonify({
            'room_id': room_id,
            'game_time': 60,  # 60초 게임
            'players': players,
            'message': message
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Start versus game error: {str(e)}")
        return jsonify({'error': '대전 게임 시작 중 오류가 발생했습니다'}), 500


@game_bp.route('/versus/end', methods=['POST'])
@jwt_required()
def end_versus_game():
    """대전 게임 종료"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'room_id' not in data or 'score' not in data:
            return jsonify({'error': '방 번호와 점수를 입력해주세요'}), 400
        
        room_id = data['room_id']
        score = data.get('score', 0)
        
        if not isinstance(score, int) or score < 0:
            return jsonify({'error': '유효하지 않은 점수입니다'}), 400
        
        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404
        
        # 점수 업데이트
        room.update_participant_score(user_id, score)
        
        # 모든 플레이어가 점수를 제출했는지 확인
        all_finished = all(p.get('score', 0) > 0 for p in room.participants)
        
        if all_finished:
            # 승자 결정
            winner = max(room.participants, key=lambda p: p.get('score', 0))
            scores = {p['user_id']: p.get('score', 0) for p in room.participants}
            
            # 게임 종료
            room.end_game(scores)
            
            # 게임 기록 저장
            players_data = [
                {'user_id': p['user_id'], 'name': p['name'], 'score': p.get('score', 0)}
                for p in room.participants
            ]
            
            GameRecord.create_multiplayer_record(
                room_id, players_data, scores, winner['user_id'], 60
            )
            
            # 사용자 통계 업데이트
            for participant in room.participants:
                user = User.find_by_user_id(participant['user_id'])
                if user:
                    is_winner = participant['user_id'] == winner['user_id']
                    game_result = 'win' if is_winner else 'loss'
                    user.update_stats(
                        score_gained=participant.get('score', 0),
                        game_result=game_result
                    )
            
            return jsonify({
                'message': '게임이 종료되었습니다',
                'is_winner': user_id == winner['user_id'],
                'final_scores': scores,
                'winner': winner['name']
            }), 200
        else:
            return jsonify({
                'message': '점수가 기록되었습니다. 상대방을 기다리는 중...',
                'waiting_for_opponent': True
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"End versus game error: {str(e)}")
        return jsonify({'error': '대전 게임 종료 중 오류가 발생했습니다'}), 500


@game_bp.route('/history', methods=['GET'])
@jwt_required()
def get_game_history():
    """게임 기록 조회"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # 최대 50개까지만 조회
        
        history = GameRecord.get_user_history(user_id, limit)
        
        return jsonify({
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get game history error: {str(e)}")
        return jsonify({'error': '게임 기록 조회 중 오류가 발생했습니다'}), 500
