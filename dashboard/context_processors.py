def admin_layout_flag(request):
    user = request.user
    is_admin_layout = user.is_authenticated and (user.is_staff or getattr(user, "is_admin_role", False))
    return {"is_admin_layout": is_admin_layout}