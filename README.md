# Knownly

A SAAS product that allows people to host static websites with custom domains direct from
Dropbox. See the [Knownly website](https://www.knownly.net) for more about the product.

The primary goal is to enable non-technical people to create and edit HTML/CSS/JavaScript in their local Dropbox folder, and have those files immediately visible on the web.

## Project overview

The system combines a Django/Python web application with a Ledge/Openresty web-proxy server, with the Dropbox API acting like an "origin webserver". This approach means that files don't need to be copied out of users' Dropbox accounts and is advantageous for several reasons. It means fewer components need to access Dropbox, caching occurs only at the web-proxy, and involves no additional storage costs.

## Shutting down the service and open sourcing the code

The initial prototype was built in early 2014. It then sat on the shelf for roughly a year. With more time and interest in a side project, the prototype was eventually launched in 2015. The service then grew to ~200 users.

Unfortunately due to a lack of time and some misuse by undesirable users, new signups were disabled in December 2016. The service was eventually shut down entirely November 2017.

## Dependencies

### Frontend
- [Angular](https://angular.io)
- [Bootstrap](http://getbootstrap.com/)
- [Fontawesome](http://fontawesome.io/)
- [Sass](http://sass-lang.com/)

### Backend
- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](http://www.django-rest-framework.org/)
- [Gunicorn](http://gunicorn.org/)
- [Postgres](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### Systems
- [Openresty](https://openresty.org)
- [ledge](https://luarocks.org/modules/pintsized/ledge)
- [Redis](https://redis.io/)
- [lua-mimetypes](https://luarocks.org/modules/luarocks/mimetypes)

## 3rd Party Services
- [Dropbox](https://www.dropbox.com/developers)
- [Stripe](https://stripe.com)
- [Mixpanel](https://mixpanel.com)
- [Google Analytics](http://analytics.google.com/)

## Devops
- [Fabric](http://www.fabfile.org/)
- [Supervisord](github.com/supervisor/supervisor)
- [New Relic](https://newrelic.com/)
- [Sentry](https://www.sentry.io/)

## Testing

```(shell)
coverage run ./manage.py test --liveserver=localhost:8090-8099 -l DEBUG && coverage report -m
```

## Copyright and License Information

Copyright (c) 2014-2017 Dwight Gunning. All rights reserved.

See the file "LICENSE" for information on the history of this software, terms & conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.
