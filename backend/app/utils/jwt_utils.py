"""
JWT 유틸리티 함수들
"""
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import datetime, timedelta
import logging

def generate_tokens(user_id, name):
    """액세스 토큰과 리프레시 토큰 생성"""
    try:
        # 추가 클레임
        additional_claims = {
            "name": name,
            "type": "access"
        }
        
        # 액세스 토큰 생성 (15분)
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims
        )
        
        # 리프레시 토큰 생성 (3시간)
        refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims={"type": "refresh"}
        )
        
        return access_token, refresh_token
        
    except Exception as e:
        logging.error(f"토큰 생성 실패: {e}")
        raise

def get_current_user_id():
    """현재 인증된 사용자 ID 반환"""
    try:
        return get_jwt_identity()
    except Exception as e:
        logging.error(f"사용자 ID 조회 실패: {e}")
        return None

def refresh_access_token(user_id, name):
    """새로운 액세스 토큰 생성"""
    try:
        additional_claims = {
            "name": name,
            "type": "access"
        }
        
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims
        )
        
        return access_token
        
    except Exception as e:
        logging.error(f"액세스 토큰 갱신 실패: {e}")
        raise
