import logging

from hive import Runtime


class CmdA:
    pass


class CmdB:
    pass


class BadCmd:
    pass


def test_drain_processes_initial_queue():
    rt = Runtime()
    called = []

    def handle_a(cmd, world):
        called.append(("A", cmd))

    rt.router.register(CmdA, handle_a)

    rt.dispatcher.dispatch(CmdA())
    rt.dispatcher.dispatch(CmdA())

    n = rt.drain()
    assert n == 2
    assert len(called) == 2
    assert not rt.dispatcher.queue


def test_drain_does_not_process_commands_added_by_handlers():
    rt = Runtime()
    called = []

    def handle_a(cmd, world):
        rt.dispatcher.dispatch(CmdB())
        called.append("A")

    def handle_b(cmd, world):
        called.append("B")

    rt.router.register(CmdA, handle_a)
    rt.router.register(CmdB, handle_b)

    rt.dispatcher.dispatch(CmdA())
    n = rt.drain()
    assert n == 1
    assert called == ["A"]
    assert len(rt.dispatcher.queue) == 1


def test_handler_exception_is_caught_and_logged(caplog):
    rt = Runtime()

    def bad_handler(cmd, world):
        raise RuntimeError("handler failed")

    def good_handler(cmd, world):
        pass

    rt.router.register(BadCmd, bad_handler)
    rt.router.register(CmdA, good_handler)

    rt.dispatcher.dispatch(BadCmd())
    rt.dispatcher.dispatch(CmdA())

    caplog.set_level(logging.ERROR)
    n = rt.drain()
    # only CmdA routed successfully (BadCmd raised)
    assert n == 1
    assert any("Command handler failed" in rec.getMessage() for rec in caplog.records)
