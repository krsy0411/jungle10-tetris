from datetime import datetime
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    # 대체 구현
    import hashlib
    
    def generate_password_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password_hash(hashed, password):
        return hashed == hashlib.sha256(password.encode()).hexdigest()

from app.utils.database import get_db


class User:
    """사용자 모델"""
    
    def __init__(self, user_id, name, password=None, hashed_password=None, created_at=None, 
                 wins=0, solo_high_score=0, 
                 refresh_token_version=0, refresh_token_issued_at=None, last_login=None, is_active=True):
        self.user_id = user_id
        self.name = name
        self.hashed_password = hashed_password or (generate_password_hash(password) if password else None)
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.is_active = is_active
        self.wins = wins
        self.solo_high_score = solo_high_score
        self.refresh_token_version = refresh_token_version
        self.refresh_token_issued_at = refresh_token_issued_at or datetime.utcnow()

    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.hashed_password, password)

    def to_dict(self, include_stats=True):
        """사전 형태로 변환"""
        data = {
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at
        }
        
        if include_stats:
            data.update({
                'wins': self.wins,
                'solo_high_score': self.solo_high_score
            })
        
        return data

    def to_mongodb_doc(self):
        """MongoDB 저장용 문서로 변환"""
        return {
            '_id': self.user_id,
            'user_id': self.user_id,
            'name': self.name,
            'password_hash': self.hashed_password,  # 명세서에 맞게 필드명 변경
            'created_at': self.created_at,
            'last_login': self.last_login,
            'refresh_token_issued_at': self.refresh_token_issued_at,
            'is_active': self.is_active,  # 명세서에 있는 필드 추가
            'wins': self.wins,
            'solo_high_score': self.solo_high_score,
            'refresh_token_version': self.refresh_token_version
        }

    @staticmethod
    def from_mongodb_doc(doc):
        """MongoDB 문서에서 객체 생성"""
        if not doc:
            return None
        
        return User(
            user_id=doc.get('user_id'),
            name=doc.get('name'),
            hashed_password=doc.get('password_hash') or doc.get('hashed_password'),  # 두 필드명 모두 지원
            created_at=doc.get('created_at'),
            last_login=doc.get('last_login'),
            is_active=doc.get('is_active', True),
            wins=doc.get('wins', 0),
            solo_high_score=doc.get('solo_high_score', 0),
            refresh_token_version=doc.get('refresh_token_version', 0),
            refresh_token_issued_at=doc.get('refresh_token_issued_at')
        )

    @staticmethod
    def find_by_user_id(user_id):
        """사용자 ID로 사용자 찾기"""
        db = get_db()
        doc = db.users.find_one({'user_id': user_id})
        return User.from_mongodb_doc(doc)

    @staticmethod
    def exists(user_id):
        """사용자 존재 여부 확인"""
        db = get_db()
        return db.users.find_one({'user_id': user_id}) is not None

    def save(self):
        """사용자 정보 저장"""
        db = get_db()
        doc = self.to_mongodb_doc()
        result = db.users.update_one(
            {'user_id': self.user_id},
            {'$set': doc},
            upsert=True
        )
        return result

    def update_stats(self, score_gained=0, game_result=None, solo_score=None):
        """게임 통계 업데이트"""
        if game_result == 'win':
            self.wins += 1
        
        # 솔로 점수 업데이트
        if solo_score and solo_score > self.solo_high_score:
            self.solo_high_score = solo_score
        
        # 멀티플레이어 점수도 최고 점수 갱신에 반영
        if score_gained > 0 and score_gained > self.solo_high_score:
            self.solo_high_score = score_gained
        
        self.save()

    def increment_refresh_token_version(self):
        """리프레시 토큰 버전 증가 (로그아웃 처리)"""
        self.refresh_token_version += 1
        self.save()

    def is_refresh_token_valid(self, token_issued_at):
        """리프레시 토큰이 유효한지 확인"""
        if not self.refresh_token_issued_at or not token_issued_at:
            return False
        return token_issued_at >= self.refresh_token_issued_at
    
    def deactivate_account(self):
        """계정 비활성화"""
        self.is_active = False
        self.save()
    
    def activate_account(self):
        """계정 활성화"""
        self.is_active = True
        self.save()

    @staticmethod
    def get_ranking(limit=10):
        """랭킹 조회"""
        db = get_db()
        pipeline = [
            {
                '$sort': {
                    'wins': -1,
                    'solo_high_score': -1
                }
            },
            {'$limit': limit}
        ]
        
        ranking = []
        for i, doc in enumerate(db.users.aggregate(pipeline), 1):
            user = User.from_mongodb_doc(doc)
            user_data = user.to_dict()
            user_data['rank'] = i
            ranking.append(user_data)
        
        return ranking