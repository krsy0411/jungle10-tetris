"""
애플리케이션 설정
"""
import os
from datetime import timedelta

class Config:
    """기본 설정"""
    
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # 15분
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=3)    # 3시간
    JWT_ALGORITHM = 'HS256'
    
    # JWT 쿠키 설정
    JWT_TOKEN_LOCATION = ['cookies', 'headers']  # 쿠키와 헤더 둘 다 지원
    JWT_COOKIE_SECURE = False  # 개발환경에서는 False, 프로덕션에서는 True
    JWT_COOKIE_CSRF_PROTECT = False  # CSRF 보호 비활성화 (개발용)
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    
    # MongoDB 설정
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/jungle_tetris')
    
    # CORS 설정
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Socket.IO 설정
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # 서버 설정
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # 게임 설정
    GAME_TIME_LIMIT = 60  # 60초
    MAX_ROOM_PLAYERS = 2  # 최대 2명
    ROOM_TIMEOUT = 600    # 10분 비활성 시 자동 삭제
    
    # 랭킹 설정
    MAX_RANKING_LIMIT = 100
    
    # 보안 설정
    BCRYPT_LOG_ROUNDS = 12  # bcrypt 해싱 라운드
