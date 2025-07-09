from functools import wraps
from flask import request, jsonify, current_app, make_response, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, create_access_token, set_access_cookies, jwt_required
import time
from collections import defaultdict


# Rate limiting을 위한 전역 변수
request_counts = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 60  # 분당 요청 제한
RATE_LIMIT_WINDOW = 60  # 60초 윈도우


def rate_limiter(limit=RATE_LIMIT_PER_MINUTE):
    """요청 수 제한 미들웨어"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 클라이언트 IP 주소 가져오기
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            
            # 현재 시간에서 윈도우 시간 이전의 요청들은 제거
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < RATE_LIMIT_WINDOW
            ]
            
            # 현재 요청 수가 제한을 초과하는지 확인
            if len(request_counts[client_ip]) >= limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'분당 최대 {limit}회 요청 가능합니다'
                }), 429
            
            # 현재 요청 시간 기록
            request_counts[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def jwt_required_with_refresh_check():
    """JWT 토큰 검증 + 리프레시 토큰 버전 확인 미들웨어"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # JWT 토큰 검증
                verify_jwt_in_request()
                
                # 토큰에서 사용자 정보 추출
                user_id = get_jwt_identity()
                claims = get_jwt()
                token_version = claims.get('refresh_token_version', 0)
                
                # 사용자 조회 및 토큰 버전 확인
                from app.models.user import User
                user = User.find_by_user_id(user_id)
                
                if not user:
                    return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
                
                # 토큰 버전이 일치하지 않으면 (로그아웃된 토큰)
                if token_version != user.refresh_token_version:
                    return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
                
                return func(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"JWT verification error: {str(e)}")
                return jsonify({'error': '인증 실패'}), 401
        
        return wrapper
    return decorator


def validate_json_content_type():
    """JSON Content-Type 검증 미들웨어"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    return jsonify({
                        'error': 'Content-Type must be application/json'
                    }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_request():
    """요청 로깅 미들웨어"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 요청 정보 로깅
            current_app.logger.info(
                f"{request.method} {request.path} - "
                f"IP: {request.remote_addr} - "
                f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
            )
            
            # 함수 실행
            response = func(*args, **kwargs)
            
            # 응답 시간 계산 및 로깅
            duration = time.time() - start_time
            current_app.logger.info(
                f"Response: {response[1] if isinstance(response, tuple) else 200} - "
                f"Duration: {duration:.3f}s"
            )
            
            return response
        return wrapper
    return decorator


def handle_cors():
    """CORS 처리 미들웨어"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            
            # Flask-CORS가 이미 처리하지만, 추가적인 헤더 설정
            if isinstance(response, tuple):
                data, status_code = response
                headers = {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Max-Age': '3600'
                }
                return data, status_code, headers
            
            return response
        return wrapper
    return decorator


class SecurityMiddleware:
    """보안 관련 미들웨어"""
    
    @staticmethod
    def sanitize_input(data):
        """입력 데이터 정제"""
        if isinstance(data, dict):
            return {key: SecurityMiddleware.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [SecurityMiddleware.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # XSS 방지를 위한 기본적인 HTML 태그 제거
            import re
            return re.sub(r'<[^>]+>', '', data).strip()
        else:
            return data
    
    @staticmethod
    def validate_request_size(max_size_mb=10):
        """요청 크기 제한"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if request.content_length:
                    max_size_bytes = max_size_mb * 1024 * 1024
                    if request.content_length > max_size_bytes:
                        return jsonify({
                            'error': 'Request too large',
                            'message': f'최대 {max_size_mb}MB까지 허용됩니다'
                        }), 413
                
                return func(*args, **kwargs)
            return wrapper
        return decorator