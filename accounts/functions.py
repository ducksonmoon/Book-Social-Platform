from core.models import UserProfile


def is_following(user, profile):
    """
    Check if a user is following a profile
    """
    if user.is_authenticated:
        return user.userprofile.following.filter(id=profile.id).exists()
    return False
