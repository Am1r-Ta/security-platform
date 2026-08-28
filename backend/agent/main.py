from agent.core.sender import send_system_info


API_URL = "http://127.0.0.1:8000/api/v1/agents/register"


if __name__ == "__main__":
    result = send_system_info(API_URL)
    print(result)