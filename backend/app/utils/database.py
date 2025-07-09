"""
MongoDB 데이터베이스 연결 및 관리
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

# 전역 데이터베이스 변수
db = None
client = None

def init_db():
    """데이터베이스 연결 초기화"""
    global db, client
    
    try:
        # MongoDB URI 가져오기
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/jungle_tetris')
        
        # MongoDB 클라이언트 생성
        client = MongoClient(mongodb_uri)
        
        # 연결 테스트
        client.admin.command('ping')
        
        # 데이터베이스 선택
        db_name = mongodb_uri.split('/')[-1] if '/' in mongodb_uri else 'jungle_tetris'
        db = client[db_name]
        
        # 인덱스 생성
        create_indexes()
        
        logging.info(f"✅ MongoDB 연결 성공: {mongodb_uri}")
        
    except ConnectionFailure as e:
        logging.error(f"❌ MongoDB 연결 실패: {e}")
        raise
    except Exception as e:
        logging.error(f"❌ 데이터베이스 초기화 실패: {e}")
        raise

def create_indexes():
    """필요한 인덱스 생성"""
    try:
        # users 컬렉션 인덱스
        db.users.create_index("user_id", unique=True)
        db.users.create_index("created_at")
        
        # rooms 컬렉션 인덱스
        db.rooms.create_index("room_id", unique=True)
        db.rooms.create_index("host_id")
        db.rooms.create_index("status")
        db.rooms.create_index("created_at")
        
        # game_records 컬렉션 인덱스
        db.game_records.create_index("user_id")
        db.game_records.create_index("game_type")
        db.game_records.create_index("played_at")
        db.game_records.create_index([("game_type", 1), ("score", -1)])  # 랭킹용
        
        # user_stats 컬렉션 인덱스
        db.user_stats.create_index("user_id", unique=True)
        db.user_stats.create_index("solo_best_score")
        db.user_stats.create_index("versus_total_wins")
        
        logging.info("✅ 데이터베이스 인덱스 생성 완료")
        
    except Exception as e:
        logging.error(f"❌ 인덱스 생성 실패: {e}")

def get_db():
    """데이터베이스 인스턴스 반환"""
    global db
    if db is None:
        init_db()
    return db
