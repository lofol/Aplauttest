import unittest
from unittest.mock import AsyncMock, MagicMock

from pars.parser import OzonParser, Review
from pars.session import Base, Session


class TestBase(unittest.TestCase):

    def setUp(self):
        self.base = Base()

    def test_msg_info(self):
        log_mock = MagicMock()
        self.base.log = log_mock
        self.base.msg("info", "Test message")
        log_mock.info.assert_called_once_with("Test message")

    def test_msg_error(self):
        log_mock = MagicMock()
        self.base.log = log_mock
        self.base.msg("error", "Test error message")
        log_mock.error.assert_called_once_with("Test error message")


class TestSession(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = Session()

    async def test_set_session_success(self):
        self.session.session = AsyncMock()
        self.session.session.post = AsyncMock(return_value=MagicMock(status_code=200, json=AsyncMock(
            return_value={'authToken': {'accessToken': 'token'}})))

        await self.session.set_session()

        self.assertTrue(self.session.msg.called)
        self.assertTrue(self.session.session.headers['Authorization'] == 'Bearer token')

    async def test_request_retry_on_error(self):
        self.session.session = AsyncMock()
        self.session.session.request = AsyncMock(side_effect=[MagicMock(status_code=500), MagicMock(status_code=200)])

        await self.session.request('GET', 'https://api.ozon.ru/test')

        self.assertEqual(self.session.msg.call_count, 1)
        self.assertEqual(self.session.set_session.call_count, 1)


class TestOzonParser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.parser = OzonParser()

    async def test_parse_message_no_article(self):
        result = await self.parser.parse_message("Без артикула или он короткий 1")
        self.assertEqual(result, 'Не найден артикул в сообщении!')

    async def test_parse_message_with_article(self):
        self.parser.parse_article = AsyncMock(return_value="Article parsed successfully")
        result = await self.parser.parse_message("Артикул: 12345")
        self.assertEqual(result, 'Article parsed successfully')

    async def test_parse_article_success(self):
        self.parser.save_reviews_to_json = AsyncMock()
        await self.parser.session.set_session()
        result = await self.parser.parse_article(158723509)

        self.assertEqual(result, 'У товара c артикулом 158723509 получено 3 отзывов(а)')
        self.assertTrue(self.parser.save_reviews_to_json.called)

    async def test_save_reviews_to_json(self):
        reviews = [Review(datetime="2022-01-15 10:30", nickname="User1", body="Great product!", rating="5")]
        article = "158723509"

        await self.parser.save_reviews_to_json(reviews, article)

        self.assertTrue(self.parser.rews_file.endswith("158723509.json"))


if __name__ == '__main__':
    unittest.main()
