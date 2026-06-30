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
    # Client init
    ecm_client = CiteckClient(
        keycloak_client_id=settings.ECM_CLIENT_ID,
        keycloak_secret=settings.ECM_CLIENT_SECRET,
        citeck_base_url=settings.ECM_BASE_URL,
    )
    # Quety example
    record = await ecm_client.query(
        query={
            "records": ["emodel/person@1234"],
            "attributes": ["?json"],
            "version": 1,
        }
    )
    pprint(record)


if __name__ == "__main__":
    from asyncio import run
    run(main())
```
