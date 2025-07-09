from datetime import datetime
from app.utils.database import get_db
import uuid


class GameRoom:
    """게임 방 모델"""
    
    def __init__(self, room_id=None, host_user_id=None, host_name=None, status='waiting', 
                 participants=None, created_at=None, game_start_time=None, game_end_time=None):
        self.room_id = room_id or str(uuid.uuid4())[:8]
        self.host_user_id = host_user_id
        self.host_name = host_name
        self.status = status  # 'waiting', 'playing', 'finished'
        self.participants = participants or []
        self.created_at = created_at or datetime.utcnow()
        self.game_start_time = game_start_time
        self.game_end_time = game_end_time

    def to_dict(self):
        """사전 형태로 변환"""
        return {
            'room_id': self.room_id,
            'host_user_id': self.host_user_id,
            'host_name': self.host_name,
            'status': self.status,
            'participants': self.participants,
            'participant_count': len(self.participants),
            'max_participants': 2,
            'created_at': self.created_at,
            'game_start_time': self.game_start_time,
            'game_end_time': self.game_end_time
        }

    def to_mongodb_doc(self):
        """MongoDB 저장용 문서로 변환"""
        return {
            '_id': self.room_id,
            'room_id': self.room_id,
            'host_user_id': self.host_user_id,
            'host_name': self.host_name,
            'status': self.status,
            'participants': self.participants,
            'created_at': self.created_at,
            'game_start_time': self.game_start_time,
            'game_end_time': self.game_end_time
        }

    @staticmethod
    def from_mongodb_doc(doc):
        """MongoDB 문서에서 객체 생성"""
        if not doc:
            return None
        
        return GameRoom(
            room_id=doc.get('room_id'),
            host_user_id=doc.get('host_user_id'),
            host_name=doc.get('host_name'),
            status=doc.get('status', 'waiting'),
            participants=doc.get('participants', []),
            created_at=doc.get('created_at'),
            game_start_time=doc.get('game_start_time'),
            game_end_time=doc.get('game_end_time')
        )

    @staticmethod
    def find_by_room_id(room_id):
        """방 ID로 방 찾기"""
        db = get_db()
        doc = db.game_rooms.find_one({'room_id': room_id})
        return GameRoom.from_mongodb_doc(doc)

    def save(self):
        """방 정보 저장"""
        db = get_db()
        doc = self.to_mongodb_doc()
        result = db.game_rooms.update_one(
            {'room_id': self.room_id},
            {'$set': doc},
            upsert=True
        )
        return result

    def delete(self):
        """방 삭제"""
        db = get_db()
        return db.game_rooms.delete_one({'room_id': self.room_id})

    def add_participant(self, user_id, user_name):
        """참가자 추가"""
        if len(self.participants) >= 2:
            return False, "방이 가득 찼습니다"
        
        if any(p['user_id'] == user_id for p in self.participants):
            return False, "이미 참가한 사용자입니다"
        
        participant = {
            'user_id': user_id,
            'name': user_name,
            'joined_at': datetime.utcnow(),
            'score': 0,
            'status': 'ready'
        }
        
        self.participants.append(participant)
        self.save()
        return True, "방에 참가했습니다"

    def start_game(self):
        """게임 시작"""
        if len(self.participants) != 2:
            return False, "2명이 모두 참가해야 게임을 시작할 수 있습니다"
        
        if self.status != 'waiting':
            return False, "게임을 시작할 수 없는 상태입니다"
        
        self.status = 'playing'
        self.game_start_time = datetime.utcnow()
        self.save()
        return True, "게임이 시작되었습니다"

    def end_game(self, scores=None):
        """게임 종료"""
        self.status = 'finished'
        self.game_end_time = datetime.utcnow()
        
        if scores:
            for participant in self.participants:
                if participant['user_id'] in scores:
                    participant['score'] = scores[participant['user_id']]
        
        self.save()
        return True, "게임이 종료되었습니다"

    def update_participant_score(self, user_id, score):
        """참가자 점수 업데이트"""
        for participant in self.participants:
            if participant['user_id'] == user_id:
                participant['score'] = score
                self.save()
                return True
        return False

    def is_host(self, user_id):
        """방장 여부 확인"""
        return self.host_user_id == user_id

    def can_join(self):
        """참가 가능 여부 확인"""
        return self.status == 'waiting' and len(self.participants) < 2
