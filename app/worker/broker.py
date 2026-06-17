from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.config import settings

result_backend = RedisAsyncResultBackend(str(settings.redis_url))
broker = ListQueueBroker(url=str(settings.redis_url)).with_result_backend(result_backend)
