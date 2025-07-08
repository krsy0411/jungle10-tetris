from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """메인 페이지 - 로그인 여부에 따라 다른 페이지로 리디렉션"""
    return redirect(url_for('main.login'))


@main_bp.route('/login')
def login():
    """로그인 페이지 렌더링"""
    return render_template('login.html')


@main_bp.route('/register')
def register():
    """회원가입 페이지 렌더링"""
    return render_template('register.html')


@main_bp.route('/main')
@jwt_required(optional=True)
def main():
    """메인 게임 페이지 렌더링"""
    current_user = get_jwt_identity()
    if not current_user:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('main.login'))
    
    return render_template('main.html')


@main_bp.route('/rooms')
@jwt_required(optional=True)
def rooms():
    """방 목록 페이지 렌더링"""
    current_user = get_jwt_identity()
    if not current_user:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('main.login'))
    
    # TODO: 방 목록 데이터를 가져와서 템플릿에 전달
    return render_template('rooms.html')
