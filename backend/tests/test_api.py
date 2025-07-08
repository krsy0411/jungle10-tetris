"""
Jungle Tetris Backend API Tests
기본적인 API 엔드포인트 동작 테스트
"""

import unittest
import json
import os
from app import create_app
from app.utils.database import get_database


class TetrisAPITestCase(unittest.TestCase):
    """테트리스 API 테스트 케이스"""
    
    def setUp(self):
        """테스트 초기화"""
        # 테스트용 환경 변수 설정
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/tetris_test'
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 테스트 DB 초기화
        self.db = get_database()
        self.clear_test_data()
    
    def tearDown(self):
        """테스트 정리"""
        self.clear_test_data()
        self.app_context.pop()
    
    def clear_test_data(self):
        """테스트 데이터 정리"""
        try:
            self.db.users.delete_many({'user_id': {'$regex': '^test_'}})
            self.db.game_rooms.delete_many({'room_id': {'$regex': '^test_'}})
            self.db.game_records.delete_many({'room_id': {'$regex': '^test_'}})
        except Exception as e:
            print(f"테스트 데이터 정리 중 오류: {e}")
    
    # 인증 API 테스트
    def test_register_success(self):
        """회원가입 성공 테스트"""
        data = {
            'user_id': 'test_user123',
            'name': '테스트유저',
            'password': 'Test1234!@#'
        }
        response = self.client.post('/api/auth/register', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '회원가입이 완료되었습니다')
        self.assertIn('access_token', json_data['data'])
    
    def test_register_duplicate_user(self):
        """중복 아이디 회원가입 테스트"""
        # 첫 번째 회원가입
        data = {
            'user_id': 'test_duplicate',
            'name': '테스트유저',
            'password': 'Test1234!@#'
        }
        self.client.post('/api/auth/register', 
                        data=json.dumps(data),
                        content_type='application/json')
        
        # 중복 회원가입 시도
        response = self.client.post('/api/auth/register', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 409)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '이미 존재하는 아이디입니다')
    
    def test_login_success(self):
        """로그인 성공 테스트"""
        # 회원가입
        register_data = {
            'user_id': 'test_login',
            'name': '테스트유저',
            'password': 'Test1234!@#'
        }
        self.client.post('/api/auth/register', 
                        data=json.dumps(register_data),
                        content_type='application/json')
        
        # 로그인
        login_data = {
            'user_id': 'test_login',
            'password': 'Test1234!@#'
        }
        response = self.client.post('/api/auth/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '로그인 성공')
        self.assertIn('access_token', json_data['data'])
    
    def test_login_invalid_credentials(self):
        """잘못된 로그인 정보 테스트"""
        data = {
            'user_id': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '아이디 또는 비밀번호가 올바르지 않습니다')
    
    # 방 관리 API 테스트
    def test_create_room_unauthorized(self):
        """인증 없이 방 생성 시도 테스트"""
        data = {
            'room_name': '테스트 방',
            'password': '',
            'max_players': 2
        }
        response = self.client.post('/api/rooms', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_rooms_list(self):
        """방 목록 조회 테스트"""
        response = self.client.get('/api/rooms')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('data', json_data)
        self.assertIn('rooms', json_data['data'])
    
    # 랭킹 API 테스트
    def test_get_ranking(self):
        """랭킹 조회 테스트"""
        response = self.client.get('/api/ranking')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('data', json_data)
        self.assertIn('rankings', json_data['data'])
    
    # 헬스체크 테스트
    def test_health_check(self):
        """헬스체크 테스트"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['status'], 'healthy')
    
    # 유틸리티 메서드
    def create_test_user_and_get_token(self, user_id='test_auth_user'):
        """테스트용 사용자 생성 및 토큰 반환"""
        data = {
            'user_id': user_id,
            'name': '테스트유저',
            'password': 'Test1234!@#'
        }
        response = self.client.post('/api/auth/register', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        if response.status_code == 201:
            json_data = json.loads(response.data)
            return json_data['data']['access_token']
        return None
    
    def get_auth_headers(self, token):
        """인증 헤더 반환"""
        return {'Authorization': f'Bearer {token}'}


if __name__ == '__main__':
    unittest.main()
