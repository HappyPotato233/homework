from flask import Blueprint, request
from pydantic import ValidationError
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.core.response import json, BizException
from app.core.dependencies import login_required, role_required, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, ProfileRequest, PasswordRequest

bp = Blueprint("auth", __name__)

def _parse_body(model_cls):
    """公共辅助：取 JSON body → Pydantic 校验 → 返回模型实例

    逐字思路：
    1. request.get_json(silent=True) 取 body，取不到返回 None
    2. body 为 None 用空字典兜底
    3. 校验不过抛 BizException(1001)
    """
    body = request.get_json(silent=True) or {}
    try:
        return model_cls(**body)
    except ValidationError:
        raise BizException(1001, "参数校验错误，请检查请求体字段", 400)

def _token_response(user: User) -> dict:
    """拼统一的 token 响应体（登录/注册复用）"""
    return json({
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {"id": user.id, "username": user.username, "role": user.role},
    })

@bp.route("/register", methods=["POST"])
def register():
    """注册：查重-哈希-入库-签JWT(返回token)"""
    req = _parse_body(RegisterRequest)
    db = get_db()
    user = User.find_by_username(db, req.username)
    if user:
        raise BizException(1004, "用户名已存在", 400)
    user = User.create(db, req.username, hash_password(req.password), role = "user")
    return _token_response(user)
    
@bp.route("/login", methods=["POST"])
def login():
    """登录：校验-签JWT(返回token)"""
    req = _parse_body(LoginRequest)
    db = get_db()
    user = User.find_by_username(db, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise BizException(1002, "用户名或密码错误", 401)
    return _token_response(user)

@bp.route("/me", methods=["GET"])
@login_required
def me():
    """获取当前用户信息"""
    user = get_current_user()
    return json({
            "id": user.id,
            "username": user.username,
            "role": user.role,
        })

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """退出登录：JWT 无状态，前端丢弃 Token 即可，后端返回成功提示"""
    return json(message="已登出",code=0)

@bp.route("/users", methods=["GET"])
@role_required("admin")
def users():
    """获取所有用户列表"""
    db = get_db()
    users = User.all_users(db)
    return json({
        "users": [
            {"id": u.id, "username": u.username, "role": u.role,
             "created_at": u.created_at.isoformat() if u.created_at else None}
             for u in users
            ]
    })
'''
    添加更多路由时，要注意以下几点：
    1，每次路由都要返回JWTtoken
    2.每次测试时，都要用新的token去测试数据（例如我更改了用户名，后续测试用的token就会失效，要用新返回的token）
'''
@bp.route("/profile", methods=["PUT"])
@login_required
def check_username():
    """修改用户名称"""
    req = _parse_body(ProfileRequest)
    db = get_db()
    if User.find_by_username(db, req.new_username):
        raise BizException(1004, "用户名已存在", 400)
    user = get_current_user()
    if user.username == req.new_username:
        raise BizException(1004, "用户名未改变", 400)
    user = user.update_username(db, req.new_username)
    return _token_response(user)

@bp.route("/password", methods=["PUT"])
@login_required
def check_password():
    """修改用户密码"""
    req = _parse_body(PasswordRequest)
    db = get_db()
    user = get_current_user()
    if not verify_password(req.old_password, user.password_hash):
        raise BizException(1004, "原始密码错误", 400)
    if verify_password(req.new_password, user.password_hash):
        raise BizException(1004, "新密码与原密码相同", 400)
    user = user.update_password(db, hash_password(req.new_password))
    return _token_response(user)
