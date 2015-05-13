{% load i18n %}
{% load bb_ember %}
{% load compress %}
{% load static %}
{% load tenant_static %}

<!DOCTYPE HTML>
<html lang="{{ LANGUAGE_CODE }}">

<head>
    <meta charset="utf-8" />
    <meta content="IE=edge,chrome=1" http-equiv="X-UA-Compatible">
    <meta name="viewport" content="width=device-width" />

    <title>{% trans "Booking.com Cares" %}</title>

    {% block defaults_js %}
        <script type="text/javascript">
            var default_title = '{% blocktrans %}1%Club - Share a little. Change the world{%  endblocktrans %}';
            var default_description = '{% blocktrans %}1%Club is the global crowdfunding and crowdsourcing platform where you can share a little and change the world, in your very own way. Pick any project you like, support it with 1% of your knowledge, money or time and follow the progress online.{% endblocktrans %}';
            var default_keywords = '{% blocktrans %}crowdfunding, crowdsourcing, platform, developing countries, time, skills, money, doneren, international cooperation, charity{% endblocktrans %}';
        </script>
    {% endblock defaults_js %}

    {% block meta %}
        <meta name="description" content="{% blocktrans %}1%Club is the global crowdfunding and crowdsourcing platform where you can share a little and change the world, in your very own way. Pick any project you like, support it with 1% of your knowledge, money or time and follow the progress online.{% endblocktrans %}" />
        <meta name="author" content="{% blocktrans %}1%Club{% endblocktrans %}" />
        <meta name="keywords" content="{% blocktrans %}crowdfunding, crowdsourcing, platform, developing countries, time, skills, money, doneren, international cooperation, charity{% endblocktrans %}" />
        <link rel="shortcut icon" href="{% static 'favicon.ico' %}">
    {% endblock %}

    {# Stylesheets #}
	{% block screen_css %}
        <link rel="stylesheet" href="{% tenant_static 'css/main.css' %}" media="screen" />
        <link rel="stylesheet" href="{% static 'vendor/css/redactor.css' %}" media="screen" />
	{% endblock %}
</head>
<body id="body">
    {% block content %}
        Token
    {% endblock %}
</body>
</html>
