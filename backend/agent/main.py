import time

from agent.core.sender import (
    send_system_info,
    send_heartbeat,
    send_event,
)

from agent.core.collector import (
    collect_processes,
    detect_new_processes,
)

from agent.core.identity import get_agent_id


REGISTER_URL = "http://127.0.0.1:8000/api/v1/agents/register"
HEARTBEAT_URL = "http://127.0.0.1:8000/api/v1/agents/{}/heartbeat"
EVENT_URL = "http://127.0.0.1:8000/api/v1/events"


if __name__ == "__main__":
    agent_id = get_agent_id()

    registration_data = send_system_info(
        REGISTER_URL,
        agent_id=agent_id,
    )

    print("Registration:", registration_data)

    heartbeat_url = HEARTBEAT_URL.format(agent_id)

    previous_processes = collect_processes()

    print(
        f"Agent ID: {agent_id}"
    )

    print(
        f"Initial process snapshot: "
        f"{len(previous_processes)} processes"
    )

    while True:
        try:
            current_processes = collect_processes()

            new_processes = detect_new_processes(
                previous_processes,
                current_processes,
            )

            for process in new_processes:
                event = {
                    "agent_id": agent_id,
                    "event_type": "new_process",
                    "pid": process["pid"],
                    "process_name": process["name"],
                }

                result = send_event(
                    EVENT_URL,
                    event,
                )

                print(
                    "Process Event:",
                    result,
                )

            previous_processes = current_processes

            heartbeat_result = send_heartbeat(
                heartbeat_url,
                agent_id,
            )

            print(
                "Heartbeat:",
                heartbeat_result,
            )

            time.sleep(10)

        except KeyboardInterrupt:
            print("\nAgent stopped.")
            break

        except Exception as error:
            print(
                "Agent error:",
                error,
            )

            time.sleep(5)