from flask import Blueprint, send_from_directory, current_app
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Swagger UI 설정
SWAGGER_URL = '/docs'  # SwaggerUI에 접근할 URL
API_URL = '/docs/openapi.yaml'  # OpenAPI 스펙 파일 URL

# SwaggerUI 블루프린트 생성
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Jungle Tetris API",
        'supportedSubmitMethods': ['get', 'post', 'put', 'delete', 'patch'],
        'deepLinking': True,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'operationsSorter': 'alpha'
    }
)

# API 문서 블루프린트
docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/docs/openapi.yaml')
def get_openapi_spec():
    """OpenAPI 스펙 파일 제공"""
    try:
        # docs 폴더에서 openapi.yaml 파일 제공
        docs_dir = os.path.join(current_app.root_path, '..', 'docs')
        return send_from_directory(docs_dir, 'openapi.yaml', mimetype='text/yaml')
    except Exception as e:
        current_app.logger.error(f"OpenAPI spec file error: {str(e)}")
        return {'error': 'OpenAPI 스펙 파일을 찾을 수 없습니다.'}, 404

@docs_bp.route('/swagger')
def swagger_redirect():
    """Swagger 리다이렉트 (호환성)"""
    from flask import redirect
    return redirect('/docs')

@docs_bp.route('/api-docs')
def api_docs_redirect():
    """API Docs 리다이렉트 (호환성)"""
    from flask import redirect
    return redirect('/docs')
