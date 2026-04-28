Currency Converter

Конвертер валют с графическим интерфейсом, поддержкой API и историей операций.

Автор
**[Камилла Манян**  
[manyan@icloud.com]  
[GitHub/LinkedIn — опционально]

Возможности
- Конвертация между 160+ валютами мира
- Актуальные курсы через ExchangeRate-API
- Сохранение истории в JSON
- Импорт/экспорт истории
- Валидация ввода (положительные числа)
- Удобный интерфейс на tkinter

Получение API-ключа

1. Перейдите на [exchangerate-api.com](https://www.exchangerate-api.com/)
2. Зарегистрируйтесь (бесплатный тариф: 1500 запросов/мес)
3. В личном кабинете скопируйте ваш API-ключ
4. Замените `your_api_key_here` в `main.py` ИЛИ используйте переменную окружения:

```bash
# Linux/macOS
export EXCHANGE_API_KEY="ваш_ключ_здесь"

# Windows (CMD)
set EXCHANGE_API_KEY=ваш_ключ_здесь

# Windows (PowerShell)
$env:EXCHANGE_API_KEY="ваш_ключ_здесь"
