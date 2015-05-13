{% extends 'token/base.tpl' %}
{% load static %}

{% block content %}
    <div id="not-logged-in">
        <img src="{% static 'images/booking-cares_alt.svg' %}" />
        <h1>Welcome to Booking Cares</h1>
        <p>It seems your authentication token has expired. Please login to use the Booking Cares Platform</p>

        <a class="btn btn-sec donate-btn" id="office-login-link" href="https://office.booking.com/staff/booking_cares.html?url={{url}}">Login</a>

        <p class="subtext">Access to Booking Cares is only possible from inside a Booking.com office. Not a Booking.com employee? Follow our updates on <a href="https://www.facebook.com/bookingcares">Facebook</a></p>
    </div>
{% endblock %}
