#!/usr/bin/env python3
"""
개발용 서버 실행 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from app import create_app, socketio

def main():
    """메인 함수"""
    print("🎮 Jungle Tetris Backend Server 시작...")
    
    # Flask 앱 생성
    app = create_app()
    
    # 개발 환경 설정
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    print(f"🌐 서버 URL: http://{host}:{port}")
    print(f"🔧 디버그 모드: {debug}")
    print(f"📁 프로젝트 루트: {project_root}")
    
    if debug:
        print("\n📋 주요 엔드포인트:")
        print(f"  - 헬스 체크: http://{host}:{port}/health")
        print(f"  - API 문서: http://{host}:{port}/")
        print(f"  - 인증: http://{host}:{port}/api/auth")
        print(f"  - 방 관리: http://{host}:{port}/api/rooms")
        print(f"  - 게임: http://{host}:{port}/api/game")
        print(f"  - 랭킹: http://{host}:{port}/api/ranking")
        print(f"  - Socket.IO: ws://{host}:{port}/socket.io")
    
    try:
        # SocketIO 서버 시작
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=debug
        )
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다...")
    except Exception as e:
        print(f"❌ 서버 시작 오류: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
