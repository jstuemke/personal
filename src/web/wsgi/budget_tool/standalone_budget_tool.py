from src.web.wsgi.budget_tool.budget_tool import BudgetTool

if __name__ == "__main__":
    host = "0.0.0.0"
    web_host = BudgetTool()
    web_host.run(host=host, port=6807)
