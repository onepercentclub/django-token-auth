from django.conf.urls import patterns, url
from token_auth.views import MetadataView, TokenLogoutView

from .views import TokenRedirectView, TokenLoginView, TokenErrorView, MembersOnlyView

urlpatterns = patterns(
    '',
    url(r'^redirect/$', TokenRedirectView.as_view(),
        name='token-redirect'),
    url(r'^login/(?P<token>.*?)$', TokenLoginView.as_view(),
        name='token-login'),
    url(r'^logout/$', TokenLogoutView.as_view(), name='token-logout'),
    url(r'^link/(?P<token>.+?)/(?P<link>.+?)$', TokenLoginView.as_view(),
        name='token-login-link'),
    url(r'^error/$', TokenErrorView.as_view(), name='token-error'),
    url(r'^missing/$', MembersOnlyView.as_view(), name='members-only'),
    url(r'^metadata/$', MetadataView.as_view(content_type='text/xml'),
        name='token-metadata'),
)
