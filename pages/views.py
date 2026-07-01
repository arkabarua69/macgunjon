from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import ContactMessage
from .forms import ContactMessageForm


def about(request):
    from dashboard.models import CompanyStat, TimelineEntry, SiteSettings, EcosystemCard
    site_settings = SiteSettings.get_settings()
    stats = CompanyStat.objects.filter(is_active=True).order_by('ordering')
    timeline = TimelineEntry.objects.filter(is_active=True).order_by('ordering')
    ecosystem_cards = EcosystemCard.objects.filter(is_active=True, page='about').order_by('ordering')
    ecosystem_list = list(ecosystem_cards)
    half = len(ecosystem_list) // 2
    ecosystem_left = ecosystem_list[:half] if half else []
    ecosystem_right = ecosystem_list[half:] if half else []
    return render(request, 'pages/about.html', {
        'stats': stats,
        'timeline': timeline,
        'site_settings': site_settings,
        'ecosystem_left': ecosystem_left,
        'ecosystem_right': ecosystem_right,
    })


@csrf_protect
def contact(request):
    from dashboard.models import SiteSettings
    site_settings = SiteSettings.get_settings()
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! We will get back to you soon.')
            return redirect('pages:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactMessageForm()
    return render(request, 'pages/contact.html', {'form': form, 'site_settings': site_settings})


def faq(request):
    from dashboard.models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('ordering')
    return render(request, 'pages/faq.html', {'faqs': faqs})


def privacy(request):
    return render(request, 'pages/privacy.html')


def terms(request):
    return render(request, 'pages/terms.html')
