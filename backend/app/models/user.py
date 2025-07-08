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
                 total_score=0, games_played=0, wins=0, losses=0, solo_high_score=0, refresh_token_version=0):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.hashed_password = hashed_password or (generate_password_hash(password) if password else None)
        self.created_at = created_at or datetime.utcnow()
        self.total_score = total_score
        self.games_played = games_played
        self.wins = wins
        self.losses = losses
        self.solo_high_score = solo_high_score
        self.refresh_token_version = refresh_token_version

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
                'total_score': self.total_score,
                'games_played': self.games_played,
                'wins': self.wins,
                'losses': self.losses,
                'solo_high_score': self.solo_high_score
            })
        
        return data

    def to_mongodb_doc(self):
        """MongoDB 저장용 문서로 변환"""
        return {
            '_id': self.user_id,
            'user_id': self.user_id,
            'name': self.name,
            'hashed_password': self.hashed_password,
            'created_at': self.created_at,
            'total_score': self.total_score,
            'games_played': self.games_played,
            'wins': self.wins,
            'losses': self.losses,
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
            hashed_password=doc.get('hashed_password'),
            created_at=doc.get('created_at'),
            total_score=doc.get('total_score', 0),
            games_played=doc.get('games_played', 0),
            wins=doc.get('wins', 0),
            losses=doc.get('losses', 0),
            solo_high_score=doc.get('solo_high_score', 0),
            refresh_token_version=doc.get('refresh_token_version', 0)
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
        self.games_played += 1
        self.total_score += score_gained
        
        if game_result == 'win':
            self.wins += 1
        elif game_result == 'loss':
            self.losses += 1
        
        if solo_score and solo_score > self.solo_high_score:
            self.solo_high_score = solo_score
        
        self.save()

    def increment_refresh_token_version(self):
        """리프레시 토큰 버전 증가 (로그아웃 처리)"""
        self.refresh_token_version += 1
        self.save()

    @staticmethod
    def get_ranking(limit=10):
        """랭킹 조회"""
        db = get_db()
        pipeline = [
            {
                '$sort': {
                    'total_score': -1,
                    'wins': -1,
                    'games_played': 1
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
