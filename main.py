from app.config import load_config
from app.state import load_app_state
from app.timer import ReminderTimer


def main() -> None:
    config = load_config()
    state = load_app_state()
    timer = ReminderTimer(config=config, state=state)
    timer.run()


if __name__ == "__main__":
    main()
