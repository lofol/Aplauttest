import json
import os
import re
import traceback
from dataclasses import dataclass
from urllib import parse

from pars.session import Session


class OzonParser:
    def __init__(self, ):
        self.rews_file = ''
        self.session = Session()

    async def parse_message(self, string) -> (str, str):
        """Выполняет обработку строки сообещния. На вход принимаем сообщение из телеграм чата,
         на выходе получаем сообщение о результате выполнения метода сборки товара
          либо же о неудаче получения артикула"""
        match = re.search(r'\b\d{5,16}\b', string)
        if not match:
            return 'Не найден артикул в сообщении!'
        return await self.parse_article(int(match.group()))

    async def parse_article(self, article) -> str:
        """Выполняет сбор артикула, на вход принимаем код товара,
         на выходе получаем сообщение о результате выполнения парсинга."""
        try:
            r = await self.session.request('GET',
                                           parse.urljoin(self.session.url, self.session.reviews_url.format(article)))
            if not r or not r.status_code == 200:
                return f'Товар c артикулом {article} не найден, {f"код ответа :{r}" if r else "ошибка запроса"}'
            response = r.json()
            if not response.get('widgetStates'):
                return f'Товар c артикулом {article} не найден нет widgetStates в теле запроса.'
            reviews_key = [_ for _ in response['widgetStates'] if 'listReviews' in _]
            if not reviews_key:
                return f'У товара c артикулом {article} нет отзывов.'
            reviews = json.loads(response['widgetStates'][reviews_key[0]])
            if not reviews:
                return 'У товара нет отзывов.'
            fin_reviews = [Review(datetime=review['header']['subtitle'],
                                  nickname=review['header']['title'],
                                  body=review['bodySections'][0]['descriptionAtom']['text'],
                                  rating=review['header']['rating'])
                           for review in reviews.get('reviews', [])]
            self.rews_file = str(article) + '.json'
            await self.save_reviews_to_json(fin_reviews, str(article))
            return f'У товара c артикулом {article} получено {len(fin_reviews)} отзывов(а)'
        except Exception:
            return f'Ошибка при получении товара с ариткулом {article}\n' + traceback.format_exc()

    async def save_reviews_to_json(self, reviews, article: str):
        """Сохраняет данные об отзывах в файл"""
        self.rews_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), str(article) + '.json')
        with open(self.rews_file, 'w', encoding='utf-8') as file:
            json.dump([{"datetime": review.datetime,
                        "nickname": review.nickname,
                        "body": review.body,
                        "rating": review.rating
                        } for review in reviews], file, indent=4, ensure_ascii=False)

    def __del__(self):
        if self.rews_file:
            os.remove(self.rews_file)
            self.session.msg('info', f"Файл {self.rews_file} успешно удален.")
        else:
            self.session.msg('info', f"Файл {self.rews_file} не существует.")


@dataclass
class Review:
    """Дата класс отзыва, который содержит:
     Дату отзыва(формат оставил как в озоне)
     Никнейм пользователя оставившего отзыв
     Тело, которое содержит текст отзыва
     Оценка, содержит значение от 1 до 5. Пока оставил тип str т.к. не до конца уверен в этом поле и нужны тесты.
    """
    datetime: str
    nickname: str
    body: str
    rating: str
