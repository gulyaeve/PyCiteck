# Python-клиент для Citeck Community Edition

## Клиент находится в разработке!

### Особенности

Клиент полностью асинхронный. Требуется Python 3.14 или выше. Основан на `httpx`.

### Установка

```console
$ pip install pyciteck
```

### Использование
```Python
from pprint import pprint

from PyCiteck.citeck_client import CiteckClient


async def main():
    print("Hello from pyciteck!")
    # Client init / Создание клиента
    ecm_client = CiteckClient(
        keycloak_client_id=settings.ECM_CLIENT_ID,
        keycloak_secret=settings.ECM_CLIENT_SECRET,
        citeck_base_url=settings.ECM_BASE_URL,
    )

    # Quety example / Пример запроса
    record = await ecm_client.query(
        query={
            "records": ["emodel/person@1234"],
            "attributes": ["?json"],
            "version": 1,
        }
    )
    pprint(record)

    # Mutate example / Пример запроса на изменение или добавление данных
    users_data = [
        {
            "id": f"emodel/person@1234",
            "attributes": {
                "phone?num": 123456
            },
        }
    ]
    await ecm_client.mutate(users_data)
    

if __name__ == "__main__":
    from asyncio import run
    run(main())
```
