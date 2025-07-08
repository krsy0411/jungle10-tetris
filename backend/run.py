#!/usr/bin/env python3
"""
Jungle Tetris Backend Server
실시간 대전 테트리스 게임 백엔드 서버
"""

import os
from dotenv import load_dotenv
from app import create_app, socketio

# .env 파일 로드
load_dotenv()

# Flask 앱 생성
app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting Jungle Tetris Backend on {host}:{port}")
    print(f"📝 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"🔧 Debug mode: {debug}")
    
    # Socket.IO와 함께 서버 실행
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug
    )
