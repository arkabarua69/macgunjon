from django import template
from allauth.socialaccount.templatetags.socialaccount import provider_login_url as original_provider_login_url

register = template.Library()


@register.simple_tag(takes_context=True)
def safe_provider_login_url(context, provider):
    """
    Return provider login URL if possible, else empty string.
    Usage: {% safe_provider_login_url 'google' as google_url %}
    """
    try:
        return original_provider_login_url(context, provider)
    except Exception:
        return ''


@register.simple_tag
def get_user_avatar_url(user):
    """
    Return the best available avatar URL for the user.
    Priority: uploaded avatar > Google picture > Facebook picture > None.
    Usage: {% get_user_avatar_url user as avatar_url %}
    """
    if not user or not user.is_authenticated:
        return None

    # 1. User-uploaded custom avatar
    if user.avatar and hasattr(user.avatar, 'url'):
        return user.avatar.url

    # 2. Social account pictures (Google, then Facebook)
    for provider, extract_fn in [
        ('google', lambda ed: ed.get('picture')),
        ('facebook', lambda ed: (ed.get('picture') or {}).get('data', {}).get('url')),
    ]:
        try:
            social_account = user.socialaccount_set.filter(provider=provider).first()
            if social_account and social_account.extra_data:
                url = extract_fn(social_account.extra_data)
                if url:
                    return url
        except Exception:
            continue

    return None
