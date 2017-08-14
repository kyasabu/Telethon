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

    # TODO updates.Difference and updates.State
    def update_state(self, tlobject):
        if not isinstance(tlobject, TLObject):
            return

        # crc32(b'Update'), crc32(b'Updates')
        # crc32(b'updates.State'), crc32(b'updates.Difference')
        update_types = {0x9f89304e, 0x8af52aac, 0x23df1a01, 0x20482874}
        if type(tlobject).subclass_of_id in update_types:
            # TODO Avoid reentering the lock?
            if hasattr(tlobject, 'updates'):
                for update in tlobject.updates:
                        self.update_state(update)

            attributes = [x for x in ('pts', 'qts', 'seq', 'date')
                          if hasattr(tlobject, x)]
            if attributes:
                with self._lock:
                    for a in attributes:
                        setattr(self, a, getattr(tlobject, a))

            elif hasattr(tlobject, 'other_updates'):
                # Only the case of 'difference' and 'differenceSlice',
                # these don't seem to have 'pts', 'qts', etc.
                with self._lock:
                    if hasattr(tlobject, 'state'):
                        self.update_state(tlobject.state)
                    elif hasattr(tlobject, 'intermediate_state'):
                        self.update_state(tlobject.intermediate_state)

                    for update in tlobject.other_updates:
                        self.update_state(update)
