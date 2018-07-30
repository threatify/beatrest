import requests
from celery.beat import Scheduler, logger

from celery import __version__


API_BASE_URL = 'http://localhost:8181'


class RestScheduler(Scheduler):
    """Scheduler backed by REST API."""

    persistence = None

    def __init__(self, *args, **kwargs):
        logger.debug("RestScheduler initializing")
        Scheduler.__init__(self, *args, **kwargs)

    def setup_schedule(self):  # celery must have method
        logger.debug("RestScheduler.setup_schedule called!")

        # key = self.app.conf.get(
        #     'persistent_scheduler_key', 'celery-beat-scheduler'
        # )
        # self.persistence = RedisDict(persistence=self.redis_instance, key=key)
        # self._create_schedule()
        # 
        # tz = self.app.conf.timezone
        # stored_tz = self.persistence.get(str('tz'))
        # if stored_tz is not None and stored_tz != tz:
        #     logger.warning(
        #         'Reset: Timezone changed from %r to %r', stored_tz, tz
        #     )
        #     self.persistence.clear()  # Timezone changed, reset db!
        # utc = self.app.conf.enable_utc
        # stored_utc = self.persistence.get(str('utc_enabled'))
        # if stored_utc is not None and stored_utc != utc:
        #     choices = {True: 'enabled', False: 'disabled'}
        #     logger.warning(
        #         'Reset: UTC changed from %s to %s', choices[stored_utc],
        #         choices[utc]
        #     )
        #     self.persistence.clear()  # UTC setting changed, reset db!
        # entries = self.persistence.setdefault(str('entries'), {})
        # self.merge_inplace(self.app.conf.beat_schedule)
        # self.install_default_entries(self.schedule)
        # self.persistence.update(
        #     {
        #         str('__version__'): __version__,
        #         str('tz'): tz,
        #         str('utc_enabled'): utc,
        #     }
        # )
        # logger.debug(
        #     'Current schedule:\n' +
        #     '\n'.join(repr(entry) for entry in values(entries))
        # )

    def get_schedule(self):  # celery must have method

        # base_url = self.app.conf['PYRAMID_REGISTRY'].settings['beatrest_api_base_url']
        # url = base_url + '/schedule'
        url = API_BASE_URL + '/schedule'
        resp = requests.get(url)

        return resp.json()

    def set_schedule(self, schedule):  # celery must have method
        # base_url = self.app.conf['PYRAMID_REGISTRY'].settings['beatrest_api_base_url']
        # url = base_url + '/schedule'
        url = API_BASE_URL + '/schedule'
        resp = requests.put(url, schedule)
        assert resp.ok

    schedule = property(get_schedule, set_schedule)

    @property
    def info(self):
        # print(self.app.conf)
        # u = self.app.conf['PYRAMID_REGISTRY'].settings['beatrest_api_base_url']
        u = API_BASE_URL
        return u
