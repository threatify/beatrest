import requests
from celery.beat import Scheduler, logger
from celery.five import values
from celery import __version__


class RestScheduler(Scheduler):
    """Scheduler backed by REST API."""

    persistence = None

    def __init__(self, *args, **kwargs):
        Scheduler.__init__(self, *args, **kwargs)

    def setup_schedule(self):  # celery must have method
        key = self.app.conf.get(
            'persistent_scheduler_key', 'celery-beat-scheduler'
        )
        self.persistence = RedisDict(persistence=self.redis_instance, key=key)
        self._create_schedule()

        tz = self.app.conf.timezone
        stored_tz = self.persistence.get(str('tz'))
        if stored_tz is not None and stored_tz != tz:
            logger.warning(
                'Reset: Timezone changed from %r to %r', stored_tz, tz
            )
            self.persistence.clear()  # Timezone changed, reset db!
        utc = self.app.conf.enable_utc
        stored_utc = self.persistence.get(str('utc_enabled'))
        if stored_utc is not None and stored_utc != utc:
            choices = {True: 'enabled', False: 'disabled'}
            logger.warning(
                'Reset: UTC changed from %s to %s', choices[stored_utc],
                choices[utc]
            )
            self.persistence.clear()  # UTC setting changed, reset db!
        entries = self.persistence.setdefault(str('entries'), {})
        self.merge_inplace(self.app.conf.beat_schedule)
        self.install_default_entries(self.schedule)
        self.persistence.update(
            {
                str('__version__'): __version__,
                str('tz'): tz,
                str('utc_enabled'): utc,
            }
        )
        logger.debug(
            'Current schedule:\n' +
            '\n'.join(repr(entry) for entry in values(entries))
        )

    def _create_schedule(self):
        for _ in (1, 2):
            try:
                self.persistence[str('entries')]
            except KeyError:
                self.persistence[str('entries')] = {}
            else:
                if str('__version__') not in self.persistence:
                    logger.warning(
                        'DB Reset: Account for new __version__ field'
                    )
                    self.persistence.clear()  # remove sched at 2.2.2 upgrade.
                elif str('tz') not in self.persistence:
                    logger.warning('DB Reset: Account for new tz field')
                    self.persistence.clear()  # remove sched at 3.0.8 upgrade
                elif str('utc_enabled') not in self.persistence:
                    logger.warning(
                        'DB Reset: Account for new utc_enabled field'
                    )
                    self.persistence.clear()  # remove sched at 3.0.9 upgrade
            break

    def get_schedule(self):  # celery must have method

        url = self.app.conf['beatrest_api_base_url'] + '/schedule'        
        resp = requests.get(url)
        
        return resp.json()

    def set_schedule(self, schedule):  # celery must have method
        url = self.app.conf['beatrest_api_base_url'] + '/schedule'        
        resp = requests.put(url, schedule)
        assert resp.ok

    schedule = property(get_schedule, set_schedule)

    @property
    def info(self):
        return self.app.conf['beatrest_api_base_url']
