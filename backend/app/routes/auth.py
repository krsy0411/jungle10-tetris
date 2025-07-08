from flask import Blueprint, request, jsonify, current_app
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


@auth_bp.route('/register', methods=['POST'])
def register():
    """회원가입"""
    try:
        data = request.get_json()
        
        # 필수 필드 확인
        required_fields = ['user_id', 'name', 'password', 'password_confirm']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field}는 필수 입력 항목입니다'}), 400
        
        user_id = data['user_id'].strip()
        name = data['name'].strip()
        password = data['password']
        password_confirm = data['password_confirm']
        
        # 입력값 유효성 검증
        valid, error_msg = validate_user_id(user_id)
        if not valid:
            return jsonify({'error': error_msg}), 400
        
        valid, error_msg = validate_name(name)
        if not valid:
            return jsonify({'error': error_msg}), 400
        
        valid, error_msg = validate_password(password)
        if not valid:
            return jsonify({'error': error_msg}), 400
        
        # 비밀번호 확인
        if password != password_confirm:
            return jsonify({'error': '비밀번호가 일치하지 않습니다'}), 400
        
        # 사용자 존재 여부 확인
        if User.exists(user_id):
            return jsonify({'error': '이미 존재하는 아이디입니다'}), 409
        
        # 새 사용자 생성
        user = User(user_id=user_id, name=name, password=password)
        user.save()
        
        # JWT 토큰 생성
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15),
            additional_claims={'refresh_token_version': user.refresh_token_version}
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(hours=3),
            additional_claims={'refresh_token_version': user.refresh_token_version}
        )
        
        return jsonify({
            'message': '회원가입이 완료되었습니다',
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': '회원가입 처리 중 오류가 발생했습니다'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """로그인"""
    try:
        data = request.get_json()
        
        # 필수 필드 확인
        if not data or 'user_id' not in data or 'password' not in data:
            return jsonify({'error': '아이디와 비밀번호를 입력해주세요'}), 400
        
        user_id = data['user_id'].strip()
        password = data['password']
        
        if not user_id or not password:
            return jsonify({'error': '아이디와 비밀번호를 입력해주세요'}), 400
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다'}), 401
        
        # 비밀번호 확인
        if not user.check_password(password):
            return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다'}), 401
        
        # JWT 토큰 생성
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15),
            additional_claims={'refresh_token_version': user.refresh_token_version}
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(hours=3),
            additional_claims={'refresh_token_version': user.refresh_token_version}
        )
        
        return jsonify({
            'message': '로그인되었습니다',
            'user_id': user_id,
            'name': user.name,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': '로그인 처리 중 오류가 발생했습니다'}), 500


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


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """현재 사용자 정보 조회"""
    try:
        user_id = get_jwt_identity()
        
        # 사용자 조회
        user = User.find_by_user_id(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': '사용자 정보 조회 중 오류가 발생했습니다'}), 500
