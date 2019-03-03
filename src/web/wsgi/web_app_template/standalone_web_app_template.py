from src.web.wsgi.web_app_template.web_app_template import WebAppTemplate

if __name__ == "__main__":
    host = "0.0.0.0"
    web_host = WebAppTemplate()
    web_host.run(host=host, port=6807)
