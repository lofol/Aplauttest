import uuid
import logging

from curl_cffi.requests import AsyncSession

from pars.cfg import Cfg


class Base:
    url = 'https://api.ozon.ru'
    reviews_url = '/composer-api.bx/page/json/v2?url=/products/{}/review/list'

    def __init__(self):
        self.config = Cfg().load()
        self.log = logging.getLogger(__name__)

    def msg(self, status, message):
        return {
            "info": self.log.info,
            "error": self.log.error
        }[status](message)


class Session(Base):
    """Класс сессии, нужен для работы с запросами."""
    def __init__(self):
        super().__init__()
        self.session = AsyncSession(
            headers=self.config.get('requests', {}).get('headers', {}).update({
                'MOBILE-GAID': str(uuid.uuid4())}))

    # @staticmethod
    # def check(r):
    #     """Метод проверки кода ответа.
    #     Был в планах для использования как обертка в случае бана со стороны озона,
    #     для его определения и переустановки сессии."""
    #     return r.status_code == 200

    async def set_session(self):
        """Выполнение всех служебных запросов, которые происходят в приложении Озон
        (без них источник выдает 404 на любой запрос)"""
        try:
            self.session = AsyncSession(
                headers=self.config.get('requests', {}).get('headers', {}))
            self.session.headers.update({'MOBILE-GAID': str(uuid.uuid4())})
            self.log.info('Пробую установить сессию')
            r = await self.session.post('https://api.ozon.ru/composer-api.bx/_action/initAuth',
                                        json={"clientId": "androidapp"})
            self.session.headers['Authorization'] = 'Bearer ' + r.json()['authToken']["accessToken"]
            self.msg("info", 'Получен токен при установки сессии')
            await self.session.get('https://api.ozon.ru/composer-api.bx/_action/getMobileConfigs')
            self.log.info('Получена мобильная конфигурация при установки сессии')
            await self.session.get('https://api.ozon.ru/composer-api.bx/_action/get3rdPartyConfig')
            self.log.info('Получен 3rdPartyConfig при установки сессии')
            await self.session.get('https://api.ozon.ru/composer-api.bx/page/json/v2?url=warmup')
            self.log.info('Успешный разогрев при установки сессии')
            await self.session.get('https://api.ozon.ru/composer-api.bx/_action/getPreferredCDNs')
            self.log.info('Успешный получение PreferredCDNs при установки сессии')
            await self.session.post('https://api.ozon.ru/composer-api.bx/_action/getTabBarConfig',
                                    json={"miniapp": "main"})
            self.log.info('Успешный получение TabBarConfig при установки сессии')
            await self.session.get('https://api.ozon.ru/composer-api.bx/_action/summary')
            self.log.info('Успешный получение summary при установки сессии')
            r = await self.session.get('https://api.ozon.ru/composer-api.bx/page/json/v2?url=/home?anchor=true')
            self.log.info('При переходе на стартовую страницу параметры ' + str(r.json()['browser']))
            self.log.info('Внешний IP ' + r.json()['browser']['ip'])
            await self.session.post('https://api.ozon.ru/composer-api.bx/_action/setBirthdate',
                                    json={"link": "/", "birthdate": "1994-01-01"})
            self.log.info('Установлен возраст 18+ ')
        except Exception as e:
            raise e

    # async def get_session(self):
    #     """Метод получения сессии, нужен был для переназначения сесссии.
    #      Не используеться."""
    #     try:
    #         await self.auth()
    #     except Exception as error:
    #         self.msg("error", error)
    #         await asyncio.sleep(30)

    # async def auth(self):
    #     try:
    #         await self.set_session()
    #         self.msg("info", "Сессия готова")
    #     except:
    #         self.msg("error", "Не удалось установить сессию")

    async def request(self, method, url, *args, **kwargs):
        """"Обертка дял выполнения запроса, в случае бана(ответ не 200) выполняем переустановку сессии.
         Если есть пркоси, меняем адресс(не реализовано)"""
        for i in range(1, 3):
            try:
                r = await self.session.request(method, url, *args, **kwargs)
                if r.status_code != 200:
                    raise
                return r
            except:
                self.msg("error", "Не удалось получить ответ, переустанавливаю сессию")
                await self.set_session()
