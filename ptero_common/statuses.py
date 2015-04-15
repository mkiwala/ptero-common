new = 'new'
scheduled = 'scheduled'
running = 'running'
succeeded = 'succeeded'
failed = 'failed'
errored = 'errored'
canceled = 'canceled'

TERMINAL_STATUSES = (succeeded, failed, errored, canceled)

VALID_STATUSES = (new, scheduled, running) + TERMINAL_STATUSES

VALID_STATUS_TRANSITIONS = {
    new: (scheduled, running, failed, errored, succeeded,
        canceled),
    scheduled: (running, failed, errored, succeeded, canceled),
    running: (failed, errored, succeeded, canceled),
    failed: tuple(),
    errored: tuple(),
    succeeded: tuple(),
    canceled: tuple(),
}


def is_valid(status):
    return status in VALID_STATUSES


def is_terminal(status):
    return status in TERMINAL_STATUSES


def is_valid_transition(old_status, new_status):
    return new_status in VALID_STATUS_TRANSITIONS[old_status]
