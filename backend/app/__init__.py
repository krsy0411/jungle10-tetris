"""
Jungle Tetris Backend Application Package
Flask 앱 팩토리 패턴을 사용한 애플리케이션 초기화
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os
import logging
from datetime import datetime

# SocketIO 인스턴스 (전역)
socketio = SocketIO()

def create_app():
    """Flask 앱 팩토리"""
    # 템플릿 폴더 경로를 명시적으로 지정
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # 앱 설정
    app.config.from_object('app.config.Config')
    
    # 로깅 설정
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # CORS 설정
    CORS(app, 
         origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','),
         supports_credentials=True)
    
    # JWT 초기화
    jwt = JWTManager(app)
    
    # JWT 에러 핸들러
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': '토큰이 만료되었습니다'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': '토큰이 필요합니다'}), 401
    
    # Socket.IO 초기화 (eventlet 사용, 모든 오리진 허용)
    socketio.init_app(app,
                     cors_allowed_origins="*",
                     async_mode='eventlet')
    
    # 데이터베이스 연결
    from app.utils.database import init_db
    init_db()
    
    # 블루프린트 등록
    from app.routes.main import main_bp
    from app.routes.docs import docs_bp, swaggerui_blueprint
    
    # 모든 라우트를 main_bp에 통합 - API 블루프린트들 제거
    app.register_blueprint(main_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(swaggerui_blueprint)
    
    # Socket.IO 이벤트 등록
    from app.socket_events.handlers import register_all_events
    register_all_events(socketio)
    
    # 기본 라우트
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Jungle Tetris API',
            'version': '1.0.0',
            'description': '실시간 대전 테트리스 게임 API',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'auth': '/api/auth',
                'rooms': '/api/rooms',
                'game': '/api/game',
                'ranking': '/api/ranking',
                'websocket': '/socket.io'
            }
        })
    
    @app.route('/health')
    def health_check():
        """헬스 체크 엔드포인트"""
        try:
            # 데이터베이스 연결 확인
            from app.utils.database import get_db
            db = get_db()
            db.command('ping')
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected',
                'version': '1.0.0'
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '요청한 리소스를 찾을 수 없습니다'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': '허용되지 않은 HTTP 메서드입니다'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다'}), 500
    
    return app
