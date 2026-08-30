import time

from agent.core.sender import send_system_info, send_heartbeat


REGISTER_URL = "http://127.0.0.1:8000/api/v1/agents/register"
HEARTBEAT_URL = "http://127.0.0.1:8000/api/v1/agents/{}/heartbeat"


if __name__ == "__main__":
    registration = send_system_info(REGISTER_URL)

    print(registration)

    agent_id = registration["agent_id"]

    heartbeat_url = HEARTBEAT_URL.format(agent_id)

    while True:
        result = send_heartbeat(heartbeat_url, agent_id)

        print(result)

        time.sleep(30)