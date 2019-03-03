
import inspect
import logging
import json
import types
from typing import Dict

from flask import Flask
from flask import render_template
from flask import request
# noinspection PyProtectedMember
from flask import _app_ctx_stack
# from flask import session
# from flask_session import Session

# Only currently Here for References
# from flask import send_from_directory
# from flask import render_template_string

from werkzeug.wrappers import ETagResponseMixin
from flask.helpers import _PackageBoundObject, send_from_directory
import os
import src.parsing.file_macros as filemacro

from src.common.types_macros import NestClassClassType


class _GlobalPackageAsset(_PackageBoundObject):
    """
    A overload of the Package Bound Object to support the forwarding of global assets
    """
    def __init__(self, asset_folder, import_name, template_folder=None, root_path=None):
        """
        Class constructor
        """
        if asset_folder is None:
            temp = os.path.dirname(__file__)
            temp = os.path.join(temp, "..", "..", "..", "..", "assets", "web")
            filemacro.makefolder(temp, False)
            self.asset_folder = temp
        else:
            self.asset_folder = asset_folder
        _PackageBoundObject.__init__(self, import_name, template_folder, root_path)

    @property
    def has_asset_folder(self):
        # type: () -> bool
        """This is ``True`` if the package bound object's container has a
        folder for assets files.
        """
        return self.asset_folder is not None

    def send_asset_file(self, filename):
        # type: (str) -> ETagResponseMixin
        """Function used internally to send static files from the static
        folder to the browser.

        .. versionadded:: 0.5
        """
        if not self.has_asset_folder:
            raise RuntimeError('No asset folder for this object')
        # Ensure get_send_file_max_age is called in all cases.
        # Here, we ensure get_send_file_max_age is called for Blueprints.
        cache_timeout = self.get_send_file_max_age(filename)
        return send_from_directory(self.asset_folder, filename, cache_timeout=cache_timeout)


def _post_decorator(input_function):
    # type: (types.FunctionType) -> types.FunctionType
    """ A post decorator used for the @POST

    :param input_function: the input function
    :return: a function
    """
    return input_function


def _get_decorator(input_function):
    # type: (types.FunctionType) -> types.FunctionType
    """ A get decorator used for the @GET

    :param input_function: the input function
    :return: a function
    """
    return input_function


def _register_decorator(input_decorator):
    # type: (types.FunctionType) -> types.FunctionType
    """ A convoluted function to appended a flag to a decorator for object creation registration

    :param input_decorator: a decorator
    :return: a function
    """
    def new_decorator(func):
        # type: (types.FunctionType) -> types.FunctionType
        """ the decorator that clones the old decorator with a added registration function added

        :param func: a function
        :return: a function
        """
        called_decorator = input_decorator(func)
        if input_decorator == _post_decorator:
            called_decorator.post_decorator = new_decorator
        else:
            called_decorator.get_decorator = new_decorator
        return called_decorator

    new_decorator.__name__ = input_decorator.__name__
    new_decorator.__doc__ = input_decorator.__doc__

    return new_decorator


# the post decorator
# noinspection PyTypeChecker
POST = _register_decorator(_post_decorator)

# the get decorator
# noinspection PyTypeChecker
GET = _register_decorator(_get_decorator)


class SphinxHost(object):
    """ Sphinx Host Module

    :Synopsis: Host a Sphinx Web Server

    """

    @staticmethod
    def _post_decorator_finder(cls, decorator):
        # type: (NestClassClassType, types.FunctionType) -> [types.FunctionType]
        """ used to find a post decorator

        :param cls: the input class
        :param decorator: the post decorator type
        :return: the post decorator list
        """
        post_decorator_list = []
        if cls is not None:
            for maybeDecorated in cls.__dict__.values():
                if hasattr(maybeDecorated, 'post_decorator'):
                    if maybeDecorated.post_decorator == decorator:
                        post_decorator_list.append(maybeDecorated)
            for base in cls.__bases__:
                post_decorator_list.extend(SphinxHost._post_decorator_finder(base, decorator))
        return post_decorator_list

    @staticmethod
    def _get_decorator_finder(cls, decorator):
        # type: (NestClassClassType, types.FunctionType) -> [types.FunctionType]
        """ used to find a get decorator

        :param cls: the input class
        :param decorator: the get decorator type
        :return: the get decorator list
        """

        get_decorator_list = []
        if cls is not None:
            for maybeDecorated in cls.__dict__.values():
                if hasattr(maybeDecorated, 'get_decorator'):
                    if maybeDecorated.get_decorator == decorator:
                        get_decorator_list.append(maybeDecorated)
            for base in cls.__bases__:
                get_decorator_list.extend(SphinxHost._get_decorator_finder(base, decorator))
        return get_decorator_list

    def __init__(self):
        # type: () -> None
        """ Constructor

        """
        self.parent = None
        self.app = None  # type: Flask
        self.host = None  # type: str
        self.port = None  # type: str
        self.standalone = False  # type: bool
        self.debug = None  # type: bool
        self.reload = None  # type: bool
        self.threaded = None  # type: bool
        self.handler_post = {}
        self.handler_get = {}
        self.session = None

        # Register our get and post decorators
        for post_event in self._post_decorator_finder(self.__class__, POST):
            self.post_event(post_event.__name__, post_event)

        for get_event in self._get_decorator_finder(self.__class__, GET):
            self.get_event(get_event.__name__, get_event)

        self._setup()

    @property
    def is_standalone(self):
        # type: () -> bool
        """ Returns true if the application is launched in standalone mode, false if not

        :return:
        """
        return self.standalone

    def post_event(self, event, input_function):
        # type: (str, types.FunctionType) -> None
        """ a post event decorator

        :param event: the event name
        :param input_function:  the event function
        """
        self.handler_post[event] = input_function

    def get_event(self, event, input_function):
        # type: (str, types.FunctionType) -> None
        """ a get event decorator

        :param event: the event name
        :param input_function:  the event function
        """
        self.handler_get[event] = input_function

    def _setup(
        self,
    ):  # type: () -> None
        """ setup the flask server

        :return: None
        """
        self.app = Flask(
            __name__,
        )

        self.app.gpa = _GlobalPackageAsset(
            None,
            self.app.import_name,
            self.app.template_folder,
            self.app.root_path,
        )
        self.app.add_url_rule(
            '/asset/<path:filename>',
            endpoint='asset',
            view_func=self.app.gpa.send_asset_file
        )

        # self.app.config['SESSION_TYPE'] = 'filesystem'
        # self.app.secret_key = os.urandom(24)
        # self.session.init_app(self.app)

        logging.getLogger("flask_ask").setLevel(logging.INFO)

        # i like to use pug rather than html, so allow pug!
        self.app.jinja_env.add_extension(
            'pypugjs.ext.jinja.PyPugJSExtension'
        )

        # the root index should call the index function
        self.app.add_url_rule('/', "index", self.render_index)

        # allow our plugin to support get/post ajax
        self.app.add_url_rule(
            '/ajax/',
            'basic_ajax',
            self.handle_request,
            methods=['GET', 'POST']
        )
        self.app.add_url_rule(
            '/ajax/<user_request>',
            'basic_ajax_request',
            self.handle_request,
            methods=['GET', 'POST']
        )
        self.app.add_url_rule(
            '/ajax/<user_request>/<value>',
            'complex_ajax_request',
            self.handle_request,
            methods=['GET', 'POST']
        )

        # flask has a bug in jinja currently, if this is not set to true templates will not auto reload and
        # flask must be restarted to see any html/jade changes
        self.app.jinja_env.auto_reload = True

        # this code will add a new template location to the template loader...
        # might be useful if all apps had a common template, but lets segment this
        # my_loader = jinja2.ChoiceLoader([
        #     self.app.jinja_loader,
        #     jinja2.FileSystemLoader([os.path.join(self.app.root_path, "pages")]),
        # ])
        # self.app.jinja_loader = my_loader

        class_path = os.path.dirname(inspect.getfile(self.__class__))
        self.app.root_path = class_path

    def run(
            self,
            host,  # type: str
            port,  # type: str or int
            debug=True,  # type: bool
            reloader=False,  # type: bool
            threaded=True,  # type: bool
    ):
        """

        :param host: the server ip
        :param port: the server port
        :param debug: is in debug mode
        :param reloader: will reload templates
        :param threaded: is threaded
        :return:
        """

        if self.app is None:
            return

        self.app.static_folder = os.path.abspath(self.app.static_folder)

        self.host = host
        self.port = port
        self.debug = debug
        self.reload = reloader
        self.threaded = threaded
        self.standalone = True

        self.app.run(
            host=self.host,
            debug=self.debug,
            use_reloader=self.reload,
            port=self.port,
            threaded=self.threaded
        )

    @staticmethod
    def json_error(message=""):
        # type: (str) -> str
        """ A function to return a basic json error

        :return:
        """
        return json.dumps(
            {
                "Error": True,
                "Message": message
            }
        )

    def handle_request(self, user_request=None, value=None):
        # type: (str or None, str or None) -> str
        """ Data processor of get and post ajax request

        :param user_request: user get request
        :param value: use get value
        :return: json result
        """
        if "GET" in request.method:
            if user_request in self.handler_get:
                return self.handler_get[user_request](self, user_request, value)
            else:
                return self.json_error()

        elif "POST" in request.method:
            posted_data = request.form
            event = posted_data.get("request")
            if event is None:
                return self.json_error()

            if event in self.handler_post:
                return self.handler_post[event](self, posted_data, user_request, value)
            else:
                return self.json_error()
        else:
            return self.json_error()

    # noinspection PyMethodMayBeStatic
    def render_index(self):
        # type: () -> str
        """ Returns a generic welcome message as the base class via a index call, overload this!

        :return: hello world message
        """
        return "A Basic Sphinx Webhost... <br> Inherit this class and start building your web application today!"

    @staticmethod
    def get_template(input_file):
        # type: (str) -> str
        """ Render a jinja/Jade template

        :param input_file: the template to render
        :return: the html template
        """
        return render_template(input_file)

    @staticmethod
    def get_sphinx_template(
            layout_template,
            template_title,
            page_name,
            page_template,
            page_parameters,
            layout_parameters=None
    ):
        # type: (str, str, str, Dict, Dict, Dict) -> str
        """ Render a sphinx template stack

        :param layout_parameters: the layout template parameters
        :param page_name: the name of the page
        :param layout_template: the layout template name
        :param template_title: the html title of the page shown
        :param page_template: the page template name
        :param page_parameters: the page template parameters
        :return:
        """

        if layout_parameters is None:
            layout_parameters = {}

        app_params = {
            "template_title": template_title,
            "page_name": page_name,
        }
        page_parameters.update(app_params)

        local_layout_parameters = {
            "template_title": template_title,
            "page_name": page_name,
            "page_html": render_template(page_template, **page_parameters)
        }

        if layout_parameters is not None:
            local_layout_parameters.update(layout_parameters)

        ctx = _app_ctx_stack.top
        # this is a ugly hack for passing context from the local app to the wsgi host
        ctx.sphinx_context = local_layout_parameters.copy()

        return render_template(
            layout_template,
            **local_layout_parameters
        )

    def before_startup(self):
        # type: () -> None
        """ Simplistic event used to configure plugins prior to the run command being called.
            Useful in a wsgi plugin with services that are needed.
        :return:
        """
        return

    def after_shutdown(self):
        # type: () -> None
        """ Simplistic event used to configure plugins after to the run command exits.
            Useful in a wsgi plugin with services that are needed.
        :return:
        """
        return

    # @staticmethod
    # def render(template, parms=None):
    #     return render_template(
    #         template,
    #         **parms
    #     )
