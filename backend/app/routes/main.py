from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
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
        
        # 세션에는 기본 정보만 저장 (SSR용)
        session['user_id'] = user_id
        session['user_name'] = user.name
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session.permanent = True
        
        # 성공 시
        flash('로그인 성공!', 'success')
        return redirect(url_for('main.main'))
            
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
            return redirect(url_for('main.register'))
        
        is_valid_name, name_error = validate_name(name)
        if not is_valid_name:
            flash(name_error, 'error')
            return redirect(url_for('main.register'))
        
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return redirect(url_for('main.register'))
        
        # 비밀번호 확인
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다', 'error')
            return redirect(url_for('main.register'))
        
        # 중복 사용자 확인
        if User.exists(user_id):
            flash('이미 존재하는 아이디입니다', 'error')
            return redirect(url_for('main.register'))
        
        # 새 사용자 생성
        user = User(user_id=user_id, name=name, password=password)
        user.save()
        
        # JWT 토큰 생성 (회원가입 시 자동 로그인)
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # 세션에 저장 (SSR 네비게이션용)
        session['user_id'] = user_id
        session['user_name'] = user.name
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session.permanent = True
        
        # 성공 시
        flash('회원가입이 완료되었습니다! 자동으로 로그인되었습니다.', 'success')
        return redirect(url_for('main.main'))
            
    except Exception as e:
        flash('회원가입 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('main.register'))


@main_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """로그아웃"""
    session.clear()  # 모든 세션 데이터 삭제
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('main.login'))


@main_bp.route('/main')
def main():    
    return render_template('main.html')


@main_bp.route('/rooms')
@jwt_required()
def rooms():
    """방 생성 (JWT 인증) : 테트리스 게임화면으로 이동"""
    user_id = get_jwt_identity()
    user = User.find_by_user_id(user_id)
    
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.login'))
    
    return render_template('rooms.html', user_name=user.name)


@main_bp.route('/ranking')
@jwt_required()
def ranking():
    """랭킹 페이지 렌더링 (JWT 인증)"""
    user_id = get_jwt_identity()
    user = User.find_by_user_id(user_id)
    
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.login'))
    
    # TODO: 실제 데이터베이스에서 랭킹 데이터를 가져오기
    # 임시 더미 데이터
    win_ranking = [
        {'name': '김정글', 'wins': 15},
        {'name': '이테트리스', 'wins': 12},
        {'name': '박블록', 'wins': 10},
        {'name': '최라인', 'wins': 8},
        {'name': '정게임', 'wins': 6},
        {'name': '황테트', 'wins': 5},
    ]
    
    score_ranking = [
        {'name': '김정글', 'score': 250000},
        {'name': '이테트리스', 'score': 180000},
        {'name': '박블록', 'score': 150000},
        {'name': '최라인', 'score': 120000},
        {'name': '정게임', 'score': 95000},
        {'name': '황테트', 'score': 85000},
        {'name': '조퍼즐', 'score': 72000},
        {'name': '신게이머', 'score': 68000},
        {'name': '이승부', 'score': 55000},
        {'name': '강도전', 'score': 42000},
        {'name': '송마스터', 'score': 38000},
        {'name': '윤프로', 'score': 35000},
        {'name': '전챔피언', 'score': 28000},
        {'name': '남키퍼', 'score': 22000},
        {'name': '류플레이어', 'score': 18000}
    ]
    
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
# JWT 인증 API
# ============================================================================

@main_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh_token():
    """JWT 액세스 토큰 새로고침"""
    try:
        current_user_id = get_jwt_identity()
        
        # 사용자 존재 확인
        user = User.find_by_user_id(current_user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 새 액세스 토큰 생성
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token,
            'user_id': current_user_id,
            'name': user.name
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': '토큰 갱신 중 오류가 발생했습니다'}), 500


@main_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """JWT 기반 로그아웃 API"""
    try:
        user_id = get_jwt_identity()
        
        # 사용자 정보 업데이트 (리프레시 토큰 무효화)
        user = User.find_by_user_id(user_id)
        if user:
            user.increment_refresh_token_version()
        
        return jsonify({'message': '로그아웃되었습니다'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': '로그아웃 중 오류가 발생했습니다'}), 500


@main_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """JWT 로그인 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '잘못된 요청입니다'}), 400
        
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '')
        
        # 필수 필드 확인
        if not user_id or not password:
            return jsonify({'error': '아이디와 비밀번호를 입력해주세요'}), 400
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '아이디 또는 비밀번호가 올바르지 않습니다'}), 401
        
        # 비밀번호 확인
        if not user.check_password(password):
            return jsonify({'error': '아이디 또는 비밀번호가 올바르지 않습니다'}), 401
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # 사용자 정보 업데이트
        user.refresh_token_issued_at = datetime.utcnow()
        user.last_login = datetime.utcnow()
        user.save()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'name': user.name,
            'message': '로그인 성공'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"API login error: {str(e)}")
        return jsonify({'error': '로그인 처리 중 오류가 발생했습니다'}), 500


@main_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    """JWT 회원가입 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '잘못된 요청입니다'}), 400
        
        user_id = data.get('user_id', '').strip()
        name = data.get('name', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        
        # 유효성 검증
        is_valid_id, id_error = validate_user_id(user_id)
        if not is_valid_id:
            return jsonify({'error': id_error}), 400
        
        is_valid_name, name_error = validate_name(name)
        if not is_valid_name:
            return jsonify({'error': name_error}), 400
        
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return jsonify({'error': password_error}), 400
        
        # 비밀번호 확인
        if password != password_confirm:
            return jsonify({'error': '비밀번호가 일치하지 않습니다'}), 400
        
        # 중복 사용자 확인
        if User.exists(user_id):
            return jsonify({'error': '이미 존재하는 아이디입니다'}), 400
        
        # 새 사용자 생성
        user = User(user_id=user_id, name=name, password=password)
        user.save()
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # 사용자 정보 업데이트
        user.refresh_token_issued_at = datetime.utcnow()
        user.save()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user_id,
            'name': name,
            'message': '회원가입이 완료되었습니다'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"API register error: {str(e)}")
        return jsonify({'error': '회원가입 처리 중 오류가 발생했습니다'}), 500


# ============================================================================
# API 엔드포인트들 (JWT 기반 인증)
# ============================================================================

# 방 생성 API
@main_bp.route('/api/rooms', methods=['POST'])
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
        user.update_stats(solo_score=score)
        
        return jsonify({
            'message': '게임 결과가 저장되었습니다',
            'final_score': score,
            'personal_best': personal_best,
            'previous_best': user.solo_high_score if not personal_best else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"End solo game error: {str(e)}")
        return jsonify({'error': '솔로 게임 종료 중 오류가 발생했습니다'}), 500


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
