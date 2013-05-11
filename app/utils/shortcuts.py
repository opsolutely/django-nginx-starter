import simplejson as json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import force_unicode
from django.utils.translation import gettext, ngettext, ugettext, ungettext, pgettext, npgettext
from django.utils.functional import Promise

from app.utils.exceptions import TroutSlappingException


def render_to_template(template_file, context=None, request=None):
    context = context if context else {}
    context['static_base'] = settings.STATIC_BASE_LINK
    if request:
        context['request'] = request
        context['user'] = request.user
    context_instance = RequestContext(request) if request else None
    return render_to_response(template_file, context, context_instance=context_instance)


def render_to_json(response_obj, context={}, mimetype="application/json", translate=False):
    # We can put checks on the response_obj here if necessary.
    if translate:
        return HttpResponse(json.dumps(response_obj, cls=LazyEncoder), mimetype=mimetype)
    return HttpResponse(json.dumps(response_obj, cls=LazyEncoderNoTranslate), mimetype=mimetype)


class LazyEncoder(json.encoder.JSONEncoder):
    """
    Support encoding lazy i18n strings. Encodes the translated version.
    Inspired by: http://fromzerotocodehero.blogspot.com/2011/01/django-ajax-tutorial-part-1.html
    and https://docs.djangoproject.com/en/dev/topics/serialization/#id2
    """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)


class LazyEncoderNoTranslate(json.encoder.JSONEncoder):
    """
    Support encoding lazy i18n strings. Does not encode the translated version.
    Inspired by: http://fromzerotocodehero.blogspot.com/2011/01/django-ajax-tutorial-part-1.html
    and https://docs.djangoproject.com/en/dev/topics/serialization/#id2
    """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, Promise):
            force_unicode(obj)  # make sure the object can be properly evaluated and translated
            # Docs on __reduce__(): http://docs.python.org/library/pickle.html#object.__reduce__
            callable_obj, reduce_args = obj.__reduce__()

            # Luckily, we can determine the function thanks to the way Django's lazy() is using __reduce__()
            func, args, kwargs, klasses = reduce_args

            # parse the args differently depending on what lazy() function is wrapping
            if func is gettext or func is ugettext:
                return args[0]
            elif func is ngettext or func is ungettext:
                singular, plural, num = args
                # This is what the Python ngettext implementation does. Any non-one number is considered plural (negatives and zero included)
                if num == 1:
                    return singular
                return plural
            elif func is pgettext:
                context, message = args
                return message
            elif func is npgettext:
                context, singular, plural, num = args
                # This is what the Python ngettext implementation does. Any non-one number is considered plural (negatives and zero included)
                if num == 1:
                    return singular
                return plural
            raise TroutSlappingException("Cannot encode lazy obj: %s func: %s reduce_args: %s" % (obj, func, reduce_args))

        return super(LazyEncoderNoTranslate, self).default(obj)
