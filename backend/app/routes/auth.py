from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import re
from app.models.user import User


def validate_user_id(user_id):
    """사용자 ID 유효성 검증"""
    if not user_id or len(user_id) < 3 or len(user_id) > 20:
        return False, "아이디는 3-20자 사이여야 합니다"
    
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
    if not password or len(password) < 4 or len(password) > 20:
        return False, "비밀번호는 4-20자 사이여야 합니다"
    
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