from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from app.models.game_record import GameRecord

ranking_bp = Blueprint('ranking', __name__, url_prefix='/api/ranking')


@ranking_bp.route('/score', methods=['GET'])
def get_score_ranking():
    """점수 랭킹 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 100)  # 최대 100개까지만 조회
        
        from app.utils.database import get_db
        db = get_db()
        
        # 최고 점수 기준 랭킹 (솔로 게임)
        pipeline = [
            {'$match': {'solo_high_score': {'$gt': 0}}},
            {'$sort': {'solo_high_score': -1, 'created_at': 1}},
            {'$limit': limit},
            {'$project': {
                'user_id': 1,
                'name': 1,
                'solo_high_score': 1,
                'games_played': 1,
                'created_at': 1
            }}
        ]
        
        rankings = []
        for i, doc in enumerate(db.users.aggregate(pipeline), 1):
            rankings.append({
                'rank': i,
                'user_id': doc.get('user_id'),
                'name': doc.get('name'),
                'score': doc.get('solo_high_score', 0),
                'games_played': doc.get('games_played', 0),
                'created_at': doc.get('created_at')
            })
        
        return jsonify({
            'rankings': rankings,
            'total_count': len(rankings)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get score ranking error: {str(e)}")
        return jsonify({'error': '점수 랭킹 조회 중 오류가 발생했습니다'}), 500


@ranking_bp.route('/wins', methods=['GET'])
def get_wins_ranking():
    """승리 횟수 랭킹 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 100)  # 최대 100개까지만 조회
        
        from app.utils.database import get_db
        db = get_db()
        
        # 승리 횟수 기준 랭킹
        pipeline = [
            {'$match': {'wins': {'$gt': 0}}},
            {'$sort': {'wins': -1, 'losses': 1, 'created_at': 1}},
            {'$limit': limit},
            {'$project': {
                'user_id': 1,
                'name': 1,
                'wins': 1,
                'losses': 1,
                'games_played': 1,
                'created_at': 1
            }}
        ]
        
        rankings = []
        for i, doc in enumerate(db.users.aggregate(pipeline), 1):
            total_versus_games = doc.get('wins', 0) + doc.get('losses', 0)
            win_rate = (doc.get('wins', 0) / total_versus_games * 100) if total_versus_games > 0 else 0
            
            rankings.append({
                'rank': i,
                'user_id': doc.get('user_id'),
                'name': doc.get('name'),
                'wins': doc.get('wins', 0),
                'losses': doc.get('losses', 0),
                'win_rate': round(win_rate, 1),
                'total_versus_games': total_versus_games,
                'created_at': doc.get('created_at')
            })
        
        return jsonify({
            'rankings': rankings,
            'total_count': len(rankings)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get wins ranking error: {str(e)}")
        return jsonify({'error': '승리 랭킹 조회 중 오류가 발생했습니다'}), 500


@ranking_bp.route('/recent-games', methods=['GET'])
def get_recent_games():
    """최근 게임 기록 조회"""
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 50)  # 최대 50개까지만 조회
        
        recent_games = GameRecord.get_recent_games(limit)
        
        return jsonify({
            'recent_games': recent_games,
            'count': len(recent_games)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get recent games error: {str(e)}")
        return jsonify({'error': '최근 게임 기록 조회 중 오류가 발생했습니다'}), 500
