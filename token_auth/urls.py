from django.conf.urls import patterns, url

from .views import TokenRedirectView, TokenLoginView, TokenErrorView, MembersOnlyView

urlpatterns = patterns(
    '',
    url(r'^redirect/(?P<token>.+?)$', TokenRedirectView.as_view(), name='token-redirect'),
    url(r'^login/(?P<token>.+?)$', TokenLoginView.as_view(), name='token-login'),
    url(r'^link/(?P<token>.+?)/(?P<link>.+?)$', TokenLoginView.as_view(), name='token-login-link'),
    url(r'^error/$', TokenErrorView.as_view(), name='token-error'),
    url(r'^missing/$', MembersOnlyView.as_view(), name='members-only'),
)
