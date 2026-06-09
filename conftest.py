from dotenv import load_dotenv

load_dotenv()


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: real network calls, requires services running")
