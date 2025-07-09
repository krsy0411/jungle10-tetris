from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from app.models.user import User
from app.models.game_room import GameRoom
from app.models.game_record import GameRecord
from app.routes.auth import validate_user_id, validate_name, validate_password
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """메인 페이지 - 로그인 여부에 따라 다른 페이지로 리디렉션"""
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 (SSR + JWT)"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST: 폼 처리
    try:
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        
        # 필수 필드 확인
        if not user_id or not password:
            flash('아이디와 비밀번호를 입력해주세요', 'error')
            return redirect(url_for('main.login'))
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            flash('아이디 또는 비밀번호가 올바르지 않습니다', 'error')
            return redirect(url_for('main.login'))
        
        # 비밀번호 확인
        if not user.check_password(password):
            flash('아이디 또는 비밀번호가 올바르지 않습니다', 'error')
            return redirect(url_for('main.login'))
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # 응답 생성 및 쿠키에 토큰 설정
        response = make_response(redirect(url_for('main.main')))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        # 세션에는 기본 정보만 저장 (SSR용)
        session['user_id'] = user_id
        session['user_name'] = user.name
        session.permanent = True
        
        # 성공 시
        return response
            
    except Exception as e:
        flash('로그인 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('main.login'))


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지 (SSR)"""
    if request.method == 'GET':
        return render_template('register.html')
    # POST: 폼 처리
    try:
        user_id = request.form.get('user_id', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        # 유효성 검증
        is_valid_id, id_error = validate_user_id(user_id)
        if not is_valid_id:
            flash(id_error, 'error')
            return render_template('register.html')

        is_valid_name, name_error = validate_name(name)
        if not is_valid_name:
            flash(name_error, 'error')
            return render_template('register.html')

        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('register.html')

        # 비밀번호 확인
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다', 'error')
            return render_template('register.html')

        # 중복 사용자 확인
        if User.exists(user_id):
            flash('이미 존재하는 아이디입니다', 'error')
            return render_template('register.html')


        # 새 사용자 생성
        user = User(user_id=user_id, name=name, password=password)
        user.save()

        # JWT 토큰 생성 (회원가입 시 자동 로그인)
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        # 응답 생성 및 쿠키에 토큰 설정
        response = make_response(redirect(url_for('main.main')))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        # 세션에 저장 (SSR 네비게이션용)
        session['user_id'] = user_id
        session['user_name'] = user.name
        session.permanent = True

        # 성공 시
        return response

    except Exception as e:
        flash('회원가입 처리 중 오류가 발생했습니다.', 'error')
        return render_template('register.html')


@main_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """로그아웃"""
    session.clear()  # 모든 세션 데이터 삭제
    
    # 응답 생성 및 JWT 쿠키 삭제
    response = make_response(redirect(url_for('main.login')))
    unset_jwt_cookies(response)
    
    flash('로그아웃되었습니다.', 'success')
    return response


@main_bp.route('/main')
def main():    
    return render_template('main.html')

@main_bp.route('/solo')
@jwt_required()
def solo():
    """솔로 모드 (JWT 인증) : 테트리스 게임화면으로 이동"""
    user_id = get_jwt_identity()
    user = User.find_by_user_id(user_id)
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.login'))
    # 사용자 최고 점수 조회 (solo_high_score)
    high_score = user.solo_high_score if hasattr(user, 'solo_high_score') else 0
    return render_template('solo.html', user_name=user.name, user_high_score=high_score)

@main_bp.route('/multi')
@jwt_required()
def multi():
    """방 생성 (JWT 인증) : 테트리스 게임화면으로 이동"""
    user_id = get_jwt_identity()
    user = User.find_by_user_id(user_id)
    
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.login'))
    
    # 사용자 최고 점수 조회 (solo_high_score)
    high_score = user.solo_high_score if hasattr(user, 'solo_high_score') else 0
    return render_template('multi.html', user_name=user.name, user_high_score=high_score)

@main_bp.route('/ranking')
@jwt_required()
def ranking():
    """랭킹 페이지 렌더링 (JWT 인증)"""
    user_id = get_jwt_identity()
    user = User.find_by_user_id(user_id)
    
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.login'))
    
    # 실제 데이터베이스에서 랭킹 데이터 조회
    from app.utils.database import get_db
    db = get_db()

    # 승리 랭킹 (최대 15명)
    win_pipeline = [
        {'$match': {'wins': {'$gt': 0}}},
        {'$sort': {'wins': -1, 'created_at': 1}},
        {'$limit': 15},
        {'$project': {'name': 1, 'wins': 1}}
    ]
    win_ranking = list(db.users.aggregate(win_pipeline))

    # 점수 랭킹 (최대 15명)
    score_pipeline = [
        {'$match': {'solo_high_score': {'$gt': 0}}},
        {'$sort': {'solo_high_score': -1, 'created_at': 1}},
        {'$limit': 15},
        {'$project': {'name': 1, 'score': '$solo_high_score'}}
    ]
    # $project에서 필드명 변경이 필요하므로, post-process
    score_ranking = []
    for doc in db.users.aggregate(score_pipeline):
        score_ranking.append({'name': doc.get('name'), 'score': doc.get('score', doc.get('solo_high_score', 0))})

    # 현재 사용자 정보
    current_user = {'name': user.name}
    current_user_wins = user.wins  # 실제 사용자의 승리 횟수
    current_user_score = user.solo_high_score  # 실제 사용자의 최고 점수
    return render_template('ranking.html', 
                         win_ranking=win_ranking,
                         score_ranking=score_ranking,
                         current_user=current_user,
                         current_user_wins=current_user_wins,
                         current_user_score=current_user_score,
                         user_name=user.name)

# ============================================================================
# API 엔드포인트들 (JWT 기반 인증)
# ============================================================================

# 방 생성 API
@main_bp.route('/api/rooms/create', methods=['POST'])
@jwt_required()
def api_create_room():
    """방 생성 API (JWT 인증)"""
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


@main_bp.route('/api/rooms/join', methods=['POST'])
@jwt_required()
def api_join_room():
    """방 참가 API (JWT 인증)"""
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
        
        # 2명이 되면 Socket.IO로 게임 시작 알림
        if len(room.participants) == 2:
            from app import socketio
            
            # 게임 시작
            success, start_message = room.start_game()
            if success:
                # 참가자 정보
                players = [
                    {'name': p['name'], 'user_id': p['user_id'], 'score': 0} 
                    for p in room.participants
                ]
                
                # 방의 모든 참가자에게 게임 시작 알림
                socketio.emit('game:start', {
                    'room_id': room_id,
                    'game_time': 60,  # 60초 게임
                    'players': players,
                    'message': '게임이 시작됩니다!'
                }, room=f'room_{room_id}')
        
        # Socket.IO 방 참가 알림
        from app import socketio
        socketio.emit('room:player_joined', {
            'room_id': room_id,
            'player_name': user.name,
            'players_count': len(room.participants),
            'message': f'{user.name}님이 방에 참가했습니다'
        }, room=f'room_{room_id}')
        
        return jsonify({
            'message': message,
            'room_id': room_id,
            'players': [p['name'] for p in room.participants],
            'game_started': len(room.participants) == 2
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Join room error: {str(e)}")
        return jsonify({'error': '방 참가 중 오류가 발생했습니다'}), 500


@main_bp.route('/api/rooms/<room_id>', methods=['DELETE'])
@jwt_required()
def api_delete_room(room_id):
    """방 삭제 API (JWT 인증)"""
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


# 게임 API
@main_bp.route('/api/game/solo/start', methods=['POST'])
@jwt_required()
def api_start_solo_game():
    """솔로 게임 시작 API (JWT 인증)"""
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


@main_bp.route('/api/game/solo/end', methods=['POST'])
@jwt_required()
def api_end_solo_game():
    """솔로 게임 종료 API (JWT 인증)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        score = data.get('score', 0)
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 개인 최고 점수 확인
        personal_best = score > user.solo_high_score
        
        # 게임 기록 저장
        GameRecord.create_solo_record(user_id, user.name, score, 60)
        
        # 사용자 통계 업데이트
        user.update_stats(solo_score=score)
        
        return jsonify({
            'message': '게임 결과가 저장되었습니다',
            'score': score,
            'is_best': personal_best
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"End solo game error: {str(e)}")
        return jsonify({'error': '솔로 게임 종료 중 오류가 발생했습니다'}), 500

# 멀티 게임 시작 API
@main_bp.route('/api/game/multi/start', methods=['POST'])
@jwt_required()
def api_start_multi_game():
    """멀티 게임 시작 API (JWT 인증)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        room_id = data.get('room_id')
        if not room_id:
            return jsonify({'error': '방 번호를 입력해주세요'}), 400

        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404

        # 방장만 시작 가능
        if not room.is_host(user_id):
            return jsonify({'error': '방장만 게임을 시작할 수 있습니다'}), 403

        # 게임 시작 처리 (이미 시작된 경우 등은 GameRoom 내부에서 처리)
        success, message = room.start_game()
        if not success:
            return jsonify({'error': message}), 400

        # 참가자 정보
        players = [{'name': p['name'], 'user_id': p['user_id'], 'score': 0} for p in room.participants]

        return jsonify({
            'room_id': room_id,
            'game_time': 60,  # 60초 게임
            'players': players,
            'message': '멀티 게임이 시작되었습니다'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Start multi game error: {str(e)}")
        return jsonify({'error': '멀티 게임 시작 중 오류가 발생했습니다'}), 500

# 멀티 게임 종료 API
@main_bp.route('/api/game/multi/end', methods=['POST'])
@jwt_required()
def api_end_multi_game():
    """멀티 게임 종료 API (JWT 인증)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        room_id = data.get('room_id')
        score = data.get('score', 0)

        if not room_id:
            return jsonify({'error': '방 번호를 입력해주세요'}), 400
        if not isinstance(score, int) or score < 0:
            return jsonify({'error': '유효하지 않은 점수입니다'}), 400

        # 방 조회
        room = GameRoom.find_by_room_id(room_id)
        if not room:
            return jsonify({'error': '존재하지 않는 방입니다'}), 404

        # 참가자 점수 갱신
        room.update_participant_score(user_id, score)

        # 모든 참가자가 점수를 제출했는지 확인
        all_finished = all(p.get('score', 0) > 0 for p in room.participants)

        result = {
            'room_id': room_id,
            'your_score': score,
            'all_finished': all_finished
        }

        if all_finished:
            # 승자 결정 (점수 가장 높은 사람)
            winner = max(room.participants, key=lambda p: p.get('score', 0))
            scores = {p['user_id']: p.get('score', 0) for p in room.participants}

            # 게임 종료 처리
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

            result.update({
                'message': '게임이 종료되었습니다',
                'final_scores': scores,
                'winner': winner['name']
            })

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"End multi game error: {str(e)}")
        return jsonify({'error': '멀티 게임 종료 중 오류가 발생했습니다'}), 500

# 랭킹 API
@main_bp.route('/api/ranking/score', methods=['GET'])
def api_get_score_ranking():
    """점수 랭킹 조회 API"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 100)  # 최대 100개까지만 조회
        
        from app.utils.database import get_db
        db = get_db()
        
        # 최고 점수 기준 랭킹 (솔로 게임)
        pipeline = [
            {'$match': {'solo_high_score': {'$gt': 0}}},
            {'$sort': {'solo_high_score': -1, 'created_at': 1}},
            {'$limit': limit},
            {'$project': {
                'user_id': 1,
                'name': 1,
                'solo_high_score': 1,
                'created_at': 1
            }}
        ]
        
        rankings = []
        for i, doc in enumerate(db.users.aggregate(pipeline), 1):
            rankings.append({
                'rank': i,
                'user_id': doc.get('user_id'),
                'name': doc.get('name'),
                'score': doc.get('solo_high_score', 0),
                'created_at': doc.get('created_at')
            })
        
        return jsonify({
            'rankings': rankings,
            'total_count': len(rankings)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get score ranking error: {str(e)}")
        return jsonify({'error': '점수 랭킹 조회 중 오류가 발생했습니다'}), 500


@main_bp.route('/api/ranking/wins', methods=['GET'])
def api_get_wins_ranking():
    """승리 횟수 랭킹 조회 API"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 100)  # 최대 100개까지만 조회
        
        from app.utils.database import get_db
        db = get_db()
        
        # 승리 횟수 기준 랭킹
        pipeline = [
            {'$match': {'wins': {'$gt': 0}}},
            {'$sort': {'wins': -1, 'created_at': 1}},
            {'$limit': limit},
            {'$project': {
                'user_id': 1,
                'name': 1,
                'wins': 1,
                'created_at': 1
            }}
        ]
        
        rankings = []
        for i, doc in enumerate(db.users.aggregate(pipeline), 1):
            rankings.append({
                'rank': i,
                'user_id': doc.get('user_id'),
                'name': doc.get('name'),
                'wins': doc.get('wins', 0),
                'created_at': doc.get('created_at')
            })
        
        return jsonify({
            'rankings': rankings,
            'total_count': len(rankings)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get wins ranking error: {str(e)}")
        return jsonify({'error': '승리 랭킹 조회 중 오류가 발생했습니다'}), 500
