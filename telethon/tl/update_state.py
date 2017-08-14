from threading import RLock

from . import TLObject


# Updates related, see https://core.telegram.org/api/updates
class UpdateState:
    def __init__(self, pts=0, qts=0, seq=0, date=None):
        self.pts = pts
        self.qts = qts
        self.seq = seq
        self.date = date

        self._lock = RLock()

    def update_state(self, tlobject):
        if not isinstance(tlobject, TLObject):
            return

        # crc32(b'Update'), crc32(b'Updates')
        # crc32(b'updates.State'), crc32(b'updates.Difference')
        update_types = {0x9f89304e, 0x8af52aac, 0x23df1a01, 0x20482874}
        if type(tlobject).subclass_of_id in update_types:
            with self._lock:
                self._update_state(tlobject)

    def _update_state(self, update):
        if hasattr(update, 'updates'):
            for u in update.updates:
                self._update_state(u)

        elif hasattr(update, 'other_updates'):
            # Only the case of 'difference' and 'differenceSlice'
            # have both 'other_updates' and 'state/intermediate_state'
            for u in update.other_updates:
                self._update_state(u)

            if hasattr(update, 'state'):
                self._update_state(update.state)
            elif hasattr(update, 'intermediate_state'):
                self._update_state(update.intermediate_state)

        # Here is where the actual updating happens
        for a in ('pts', 'qts', 'seq', 'date'):
            if hasattr(update, a):
                setattr(self, a, getattr(update, a))
