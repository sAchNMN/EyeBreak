from app.config import load_config
from app.state import AppState
from app.timer import ReminderTimer


def main() -> None:
    config = load_config()
    state = AppState()
    timer = ReminderTimer(config=config, state=state)
    timer.run()


if __name__ == "__main__":
    main()
