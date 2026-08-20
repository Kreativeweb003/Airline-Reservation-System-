from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    def check(user):
        return user.is_authenticated and (user.is_staff or user.is_admin_role)
    return user_passes_test(check, login_url="accounts:login")(view_func)