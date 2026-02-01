# Исправления таймаутов для инструментов сканирования

## 🔴 Проблема

Инструменты сканирования получали ошибки:
```
(!) FATAL: Too many errors connecting to host
    (Possible cause: OPERATION TIMEOUT)
```

**Причины:**
1. ❌ Нет таймаутов в командах - инструменты ждали слишком долго
2. ❌ Нет retry логики - при ошибке сразу прекращали работу
3. ❌ Нет User-Agent - серверы блокировали запросы
4. ❌ Слишком быстрые запросы - серверы блокировали rate limiting
5. ❌ Нет задержек между запросами

## ✅ Исправления

### 1. Nmap
**Было:**
```bash
nmap -sV -sC -oN file.txt host
```

**Стало:**
```bash
nmap -sV -sC --max-retries 3 --host-timeout 5m --script-timeout 2m -oN file.txt host
```

**Добавлено:**
- `--max-retries 3` - до 3 попыток при ошибках
- `--host-timeout 5m` - таймаут на хост 5 минут
- `--script-timeout 2m` - таймаут на скрипты 2 минуты

### 2. Nikto
**Было:**
```bash
nikto -h URL -o file.txt -Format txt
```

**Стало:**
```bash
nikto -h URL -o file.txt -Format txt -timeout 30 -useragent 'Mozilla/5.0...'
```

**Добавлено:**
- `-timeout 30` - таймаут 30 секунд
- `-useragent` - User-Agent заголовок для обхода защиты

### 3. Nuclei
**Было:**
```bash
nuclei -u URL -o file.txt
```

**Стало:**
```bash
nuclei -u URL -o file.txt -timeout 30 -retries 3 -rate-limit 10 -H 'User-Agent: ...'
```

**Добавлено:**
- `-timeout 30` - таймаут 30 секунд
- `-retries 3` - до 3 попыток
- `-rate-limit 10` - ограничение скорости (10 запросов/сек)
- `-H 'User-Agent'` - User-Agent заголовок

### 4. Dirb
**Было:**
```bash
dirb URL -o file.txt
```

**Стало:**
```bash
dirb URL -o file.txt -S -w -t 30 -H 'User-Agent: ...'
```

**Добавлено:**
- `-t 30` - таймаут 30 секунд
- `-S` - silent mode (меньше вывода)
- `-w` - не показывать предупреждения
- `-H 'User-Agent'` - User-Agent заголовок

### 5. SQLMap
**Было:**
```bash
sqlmap -u URL --batch --output-dir=dir
```

**Стало:**
```bash
sqlmap -u URL --batch --timeout=30 --retries=3 --delay=2 --randomize=User-Agent --output-dir=dir
```

**Добавлено:**
- `--timeout=30` - таймаут 30 секунд
- `--retries=3` - до 3 попыток
- `--delay=2` - задержка 2 секунды между запросами
- `--randomize=User-Agent` - случайный User-Agent

## 📊 Результат

Теперь инструменты:
- ✅ Имеют таймауты - не зависают надолго
- ✅ Делают повторные попытки - более надежные
- ✅ Используют User-Agent - обходят базовую защиту
- ✅ Ограничивают скорость - не блокируются rate limiting
- ✅ Делают задержки - не перегружают сервер

## 🚀 Применено

Все исправления применены на сервере и запушены в git.

В новых пентестах инструменты будут работать более надежно и обходить базовую защиту серверов.

