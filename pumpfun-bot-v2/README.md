# Pump.fun Telegram Bot

## Что делает бот

- Ищет пампы монет
- Анализирует объемы
- Проверяет ликвидность
- Фильтрует монеты СТАРШЕ 30 дней
- Отправляет уведомления в Telegram
- В уведомлении есть ссылка на pump.fun

---

## Куда вставлять ключи

Создай файл `.env`

И вставь:

```env
BOT_TOKEN=
CHAT_ID=
BIRDEYE_API_KEY=
HELIUS_API_KEY=
```

---

## Запуск

```bash
docker compose up -d --build
```
