import json
from typing import Dict

from werkzeug.datastructures import ImmutableMultiDict

from src.web.network.sphinx_host.sphinx_host import SphinxHost, POST


class WebAppTemplate(SphinxHost):
    """ The

    :Synopsis: Interfaces with SphinxHost to provide

    """

    def __init__(
            self,
            config=None
    ):
        # type: (None or Dict) -> None
        """ Constructor

        """

        SphinxHost.__init__(self)
        self.services = {}

    def before_startup(self):
        # type: () -> None
        """ Simplistic event used to configure plugins prior to the run command being called.
            Useful in a wsgi plugin with services that are needed.
        :return:
        """
        if self.parent is None:
            raise ValueError("Invalid Configuration")

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
        for key, service in self.services.items():
            service.start()

        super(WebAppTemplate, self).run(host, port, debug, reloader, threaded)

        for key, service in self.services.items():
            service.running = False

        for key, service in self.services.items():
            service.join()

    def render_index(self):
        # type: () -> str
        """ Render the web index

        :return: the web page as a string
        """
        if self.is_standalone:
            return self.get_sphinx_template(
                "standalone_template.pug",
                "Title",
                "",
                "app_template.pug",
                {}
            )
        else:
            raise Exception("WSGI Not supported on SphinxMultiHost")

    # def request_wsgi_index_callback(self, html_data):
    #     # type: (str) -> str
    #     """ Test Host Template Callback
    #
    #     :param html_data:
    #     :return:
    #     """
    #     if self.is_standalone:
    #         return self.get_wsgi_sphinx_template(
    #             "wsgi_callback_template.pug",
    #             "BLAH BLAH - ",
    #             html_data
    #         )
    #     else:
    #         return html_data


    @POST
    def ajax_callback(self, posted_data, user_request, value):
        # type: (ImmutableMultiDict, str or None, str or None) -> object
        """

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """

        _ = user_request
        _ = value
        ui = posted_data.get("user")
        print("You entered: %s" % ui)
        output = {
            "": ""
        }

        return json.dumps(output)