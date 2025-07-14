from datetime import datetime
from app.utils.database import get_db


class GameRecord:
    """게임 기록 모델"""
    
    def __init__(self, game_id=None, room_id=None, game_type='solo', players=None, 
                 winner_id=None, duration=None, created_at=None):
        self.game_id = game_id
        self.room_id = room_id
        self.game_type = game_type  # 'solo' or 'multiplayer'
        self.players = players or []  # [{'user_id': str, 'name': str, 'score': int}]
        self.winner_id = winner_id
        self.duration = duration  # 게임 지속 시간 (초)
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        """사전 형태로 변환"""
        return {
            'game_id': self.game_id,
            'room_id': self.room_id,
            'game_type': self.game_type,
            'players': self.players,
            'winner_id': self.winner_id,
            'duration': self.duration,
            'created_at': self.created_at
        }

    def to_mongodb_doc(self):
        """MongoDB 저장용 문서로 변환"""
        return {
            '_id': self.game_id,
            'game_id': self.game_id,
            'room_id': self.room_id,
            'game_type': self.game_type,
            'players': self.players,
            'winner_id': self.winner_id,
            'duration': self.duration,
            'created_at': self.created_at
        }

    @staticmethod
    def from_mongodb_doc(doc):
        """MongoDB 문서에서 객체 생성"""
        if not doc:
            return None
        
        return GameRecord(
            game_id=doc.get('game_id'),
            room_id=doc.get('room_id'),
            game_type=doc.get('game_type', 'solo'),
            players=doc.get('players', []),
            winner_id=doc.get('winner_id'),
            duration=doc.get('duration'),
            created_at=doc.get('created_at')
        )

    def save(self):
        """게임 기록 저장"""
        db = get_db()
        
        # game_id가 없으면 자동 생성
        if not self.game_id:
            try:
                from bson import ObjectId
                self.game_id = str(ObjectId())
            except ImportError:
                import uuid
                self.game_id = str(uuid.uuid4())
        
        doc = self.to_mongodb_doc()
        result = db.game_records.update_one(
            {'game_id': self.game_id},
            {'$set': doc},
            upsert=True
        )
        return result

    @staticmethod
    def create_solo_record(user_id, user_name, score, duration):
        """솔로 게임 기록 생성"""
        record = GameRecord(
            game_type='solo',
            players=[{'user_id': user_id, 'name': user_name, 'score': score}],
            winner_id=user_id,
            duration=duration
        )
        record.save()
        return record

    @staticmethod
    def create_multiplayer_record(room_id, players_data, scores, winner_id, duration):
        """멀티플레이어 게임 기록 생성"""
        record = GameRecord(
            room_id=room_id,
            game_type='multiplayer',
            players=players_data,
            winner_id=winner_id,
            duration=duration
        )
        record.save()
        return record
