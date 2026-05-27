import signal


class ShutdownFlag:
    def __init__(self) -> None:
        self.should_stop = False

    def request_stop(self, *_args: object) -> None:
        self.should_stop = True


def install_shutdown_handlers(flag: ShutdownFlag) -> None:
    signal.signal(signal.SIGINT, flag.request_stop)
    signal.signal(signal.SIGTERM, flag.request_stop)
