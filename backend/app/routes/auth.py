from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import re
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_user_id(user_id):
    """사용자 ID 유효성 검증"""
    if not user_id or len(user_id) < 5 or len(user_id) > 20:
        return False, "아이디는 5-20자 사이여야 합니다"
    
    if not re.match(r'^[a-zA-Z0-9]+$', user_id):
        return False, "아이디는 영문과 숫자만 사용할 수 있습니다"
    
    return True, ""


def validate_name(name):
    """사용자 이름 유효성 검증"""
    if not name or len(name) < 2 or len(name) > 10:
        return False, "이름은 2-10자 사이여야 합니다"
    
    if not re.match(r'^[가-힣a-zA-Z\s]+$', name):
        return False, "이름은 한글, 영문만 사용할 수 있습니다"
    
    return True, ""


def validate_password(password):
    """비밀번호 유효성 검증"""
    if not password or len(password) < 8 or len(password) > 20:
        return False, "비밀번호는 8-20자 사이여야 합니다"
    
    # 영문, 숫자, 특수문자 포함 여부 검증
    has_alpha = re.search(r'[a-zA-Z]', password)
    has_digit = re.search(r'\d', password)
    has_special = re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?]', password)
    
    if not (has_alpha and has_digit and has_special):
        return False, "비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 합니다"
    
    return True, ""


def create_user_tokens(user_id, refresh_token_version):
    """JWT 토큰 생성 (공통 함수)"""
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(minutes=15),
        additional_claims={'refresh_token_version': refresh_token_version}
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(hours=3),
        additional_claims={'refresh_token_version': refresh_token_version}
    )
    return access_token, refresh_token


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 (API + SSR)"""
    # GET 요청: 회원가입 페이지 렌더링 (SSR)
    if request.method == 'GET':
        return render_template('register.html')
    
    # POST 요청: 회원가입 처리
    try:
        # 데이터 파싱 (JSON API 또는 Form SSR)
        if request.is_json:
            data = request.get_json()
            user_id = data.get('user_id', '').strip()
            name = data.get('name', '').strip()
            password = data.get('password', '')
            password_confirm = data.get('password_confirm', '')
        else:
            user_id = request.form.get('user_id', '').strip()
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
        
        # 유효성 검증
        is_valid_id, id_error = validate_user_id(user_id)
        if not is_valid_id:
            if request.is_json:
                return jsonify({'error': id_error}), 400
            flash(id_error, 'error')
            return redirect(url_for('auth.register'))
        
        is_valid_name, name_error = validate_name(name)
        if not is_valid_name:
            if request.is_json:
                return jsonify({'error': name_error}), 400
            flash(name_error, 'error')
            return redirect(url_for('auth.register'))
        
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            if request.is_json:
                return jsonify({'error': password_error}), 400
            flash(password_error, 'error')
            return redirect(url_for('auth.register'))
        
        # 비밀번호 확인
        if password != password_confirm:
            error_msg = '비밀번호가 일치하지 않습니다'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('auth.register'))
        
        # 중복 사용자 확인
        if User.exists(user_id):
            error_msg = '이미 존재하는 아이디입니다'
            if request.is_json:
                return jsonify({'error': error_msg}), 409
            flash(error_msg, 'error')
            return redirect(url_for('auth.register'))
        
        # 새 사용자 생성
        user = User(user_id=user_id, name=name, password=password)
        user.save()
        
        # JWT 토큰 생성
        access_token, refresh_token = create_user_tokens(user_id, user.refresh_token_version)
        
        # 응답 반환
        if request.is_json:
            return jsonify({
                'message': '회원가입이 완료되었습니다',
                'data': {
                    'user': {'user_id': user_id, 'name': name},
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 201
        else:
            flash('회원가입이 완료되었습니다!', 'success')
            return redirect(url_for('auth.login'))
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        error_msg = '회원가입 처리 중 오류가 발생했습니다'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('auth.register'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 (API + SSR)"""
    # GET 요청: 로그인 페이지 렌더링 (SSR)
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST 요청: 로그인 처리
    try:
        # 데이터 파싱 (JSON API 또는 Form SSR)
        if request.is_json:
            data = request.get_json()
            user_id = data.get('user_id', '').strip()
            password = data.get('password', '')
        else:
            user_id = request.form.get('user_id', '').strip()
            password = request.form.get('password', '')
        
        # 필수 필드 확인
        if not user_id or not password:
            error_msg = '아이디와 비밀번호를 입력해주세요'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('auth.login'))
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            error_msg = '아이디 또는 비밀번호가 올바르지 않습니다'
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            flash(error_msg, 'error')
            return redirect(url_for('auth.login'))
        
        # 비밀번호 확인
        if not user.check_password(password):
            error_msg = '아이디 또는 비밀번호가 올바르지 않습니다'
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            flash(error_msg, 'error')
            return redirect(url_for('auth.login'))
        
        # JWT 토큰 생성
        access_token, refresh_token = create_user_tokens(user_id, user.refresh_token_version)
        
        # 응답 반환
        if request.is_json:
            return jsonify({
                'message': '로그인되었습니다',
                'data': {
                    'user': {'user_id': user_id, 'name': user.name},
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 200
        else:
            flash('로그인 성공!', 'success')
            return redirect(url_for('main.main'))
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        error_msg = '로그인 처리 중 오류가 발생했습니다'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """로그아웃"""
    try:
        user_id = get_jwt_identity()
        
        # 사용자 조회 및 리프레시 토큰 버전 증가
        user = User.find_by_user_id(user_id)
        if user:
            user.increment_refresh_token_version()
        
        return jsonify({'message': '로그아웃되었습니다'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': '로그아웃 처리 중 오류가 발생했습니다'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """액세스 토큰 갱신"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        token_version = claims.get('refresh_token_version', 0)
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        # 리프레시 토큰 버전 확인
        if token_version != user.refresh_token_version:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
        
        # 새 액세스 토큰 생성
        new_access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15),
            additional_claims={'refresh_token_version': user.refresh_token_version}
        )
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': '토큰 갱신 처리 중 오류가 발생했습니다'}), 500