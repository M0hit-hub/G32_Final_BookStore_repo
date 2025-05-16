def admin_status(request):
    """
    Adds admin status to the context of all templates.
    This makes the admin status available in all templates.
    """
    is_admin = False
    is_authenticated = False
    username = None
    
    if request.user.is_authenticated:
        is_authenticated = True
        username = request.user.username
        is_admin = request.user.is_staff or request.user.is_superuser
    
    return {
        'is_admin': is_admin,
        'is_user_authenticated': is_authenticated,
        'username': username,
    } 