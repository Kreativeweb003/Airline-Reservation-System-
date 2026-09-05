from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    """
    Restricts a view to staff or admin-role users.
    Unauthenticated users are redirected to the login page;
    authenticated non-admin users get Django's default 403-style redirect behavior
    from user_passes_test (redirects to login_url since no separate permission-denied
    page is configured).
    """
    def check(user):
        return user.is_authenticated and (user.is_staff or getattr(user, "is_admin_role", False))

    return user_passes_test(check, login_url="accounts:login")(view_func)