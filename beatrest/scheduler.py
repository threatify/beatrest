"""
Rest Scheduler for Celery Beat
"""

import logging
from datetime import datetime
import dateutil.parser
import requests
from celery.beat import Scheduler, ScheduleEntry
# from celery.utils.log import get_logger
from celery.schedules import crontab as crontab_schedule, \
                             schedule as interval_schedule

import beatrest.debug

log = logging.getLogger(__name__)


class RestScheduler(Scheduler):
    """Scheduler backed by REST API."""

    persistence = None

    def __init__(self, *args, **kwargs):
        print("RestScheduler initializing")
        Scheduler.__init__(self, *args, **kwargs)

        self.api_base_url = self.app.conf['PYRAMID_REGISTRY'].settings.get(
            'beatrest_api_base_url')

    def setup_schedule(self):  # celery must have method
        print("RestScheduler.setup_schedule called!")

        # key = self.app.conf.get(
        #     'persistent_scheduler_key', 'celery-beat-scheduler'
        # )
        # self.persistence = RedisDict(persistence=self.redis_instance, key=key)
        # self._create_schedule()
        #
        # tz = self.app.conf.timezone
        # stored_tz = self.persistence.get(str('tz'))
        # if stored_tz is not None and stored_tz != tz:
        #     log.warning(
        #         'Reset: Timezone changed from %r to %r', stored_tz, tz
        #     )
        #     self.persistence.clear()  # Timezone changed, reset db!
        # utc = self.app.conf.enable_utc
        # stored_utc = self.persistence.get(str('utc_enabled'))
        # if stored_utc is not None and stored_utc != utc:
        #     choices = {True: 'enabled', False: 'disabled'}
        #     log.warning(
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
        # log.info(
        #     'Current schedule:\n' +
        #     '\n'.join(repr(entry) for entry in values(entries))
        # )

    def apply_async(self, entry, producer=None, advance=True, **kwargs):
        # Update time-stamps and run counts before we actually execute,
        # so we have that done if an exception is raised (doesn't schedule
        # forever.)
        print('In Apply Async')
        print(self.app.tasks)

        entry = self.reserve(entry) if advance else entry
        task = self.app.tasks.get(entry.task)

        try:
            if task:
                return task.apply_async(entry.args, entry.kwargs,
                                        producer=producer,
                                        **entry.options)
            else:
                print('===> Sending task: %r' % entry.task)
                ret = self.send_task(entry.task, entry.args, entry.kwargs,
                                      producer=producer,
                                      **entry.options)
                return ret
        except Exception as exc:  # pylint: disable=broad-except
            reraise(SchedulingError, SchedulingError(
                "Couldn't apply scheduled task {0.name}: {exc}".format(
                    entry, exc=exc)), sys.exc_info()[2])
        finally:
            self._tasks_since_sync += 1
            if self.should_sync():
                self._do_sync()

    def get_schedule(self):  # celery must have method

        # base_url = self.app.conf['PYRAMID_REGISTRY'].settings['beatrest_api_base_url']
        # url = base_url + '/schedule'
        print("API Base URL: %s" % self.api_base_url)
        url = self.api_base_url + '/schedule'

        resp = requests.get(url)
        celery_schedules = {}
        for sname, sdict in resp.json().items():
            schedule = None
            if 'interval' == sdict['type']:  # pylint: disable=C0122
                is_relative = False

                if 'relative' in sdict and sdict['relative'] is True:
                    is_relative = True

                schedule = interval_schedule(
                    run_every=sdict['value'],
                    relative=is_relative,
                    app=self.app
                )

            elif 'crontab' == sdict['type']:  # pylint: disable=C0122
                schedule = crontab_schedule(
                    app=self.app, **sdict['value'])

            last_run_at = datetime.utcnow()
            if 'last_run_at' in sdict:
                last_run_at = dateutil.parser.parse(sdict['last_run_at'])

            celery_schedules[sname] = ScheduleEntry(
                name=sname,
                task=sdict['task'],
                args=sdict.get('args', ()),
                kwargs=sdict.get('kwargs', None),
                schedule=schedule,
                options=sdict.get('options', None),
                last_run_at=last_run_at,
            )

        log.info(celery_schedules)
        print(celery_schedules)
        return celery_schedules

    def set_schedule(self, schedule):  # celery must have method
        # base_url = self.app.conf['PYRAMID_REGISTRY'].settings['beatrest_api_base_url']
        # url = base_url + '/schedule'
        # url = API_BASE_URL + '/schedule'
        print('Calling set schedule')
        url = self.api_base_url + '/schedule'
        resp = requests.put(url, schedule)
        assert resp.ok

    schedule = property(get_schedule, set_schedule)

    @property
    def info(self):
        return self.api_base_url + '/schedule'
