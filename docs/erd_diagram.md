# ER-Диаграмма — Cinema Booking App

Бұл файл дерекқор схемасының сипаттамасы.
Нақты ER-диаграмманы `erd_diagram.pdf` файлынан қараңыз.

## Байланыстар

```
users    (1) ──── (N) tickets
movies   (1) ──── (N) sessions
halls    (1) ──── (N) seats
halls    (1) ──── (N) sessions
sessions (1) ──── (N) tickets
seats    (1) ──── (N) tickets
```

## Кестелер

- **users** — Тіркелген пайдаланушылар
- **movies** — Фильмдер каталогы
- **halls** — Кинозалдар
- **seats** — Залдардағы орындар
- **sessions** — Сеанстар кестесі (фильм + зал + уақыт)
- **tickets** — Брондалған / сатылған билеттер
