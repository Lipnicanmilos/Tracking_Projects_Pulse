# Tracking Projects Pulse

Interný **Django** nástroj na **automatizáciu reportingu a monitoringu** — plánované úlohy
(APScheduler), generovanie reportov (Excel/PDF), integrácie na e-mail, JIRA a SharePoint,
a prehľadové dashboardy nad prevádzkovými dátami.

> ⚠️ **Sanitizovaná verzia.** Všetky reálne dáta, prihlasovacie údaje, interné hostname-y
> a produkčné SQL boli odstránené alebo nahradené zástupnými hodnotami. Konfigurácia sa
> načítava z `.env` (mimo gitu).

## Funkcie

- **Plánovač úloh** (APScheduler + django-apscheduler) — pravidelné reporty a kontroly
- **Generovanie reportov** — denné/týždenné výstupy (openpyxl)
- **Integrácie** — e-mail (SMTP), JIRA (REST API), SharePoint (Office365 REST)
- **Aplikácie** — `work`, `eets`, `edz` (rôzne reportovacie a monitorovacie moduly)
- **Admin** — Jazzmin (alternatívne admin rozhranie), šifrované polia (encrypted-model-fields)

## Technológie

Django 4.1 · APScheduler · Jazzmin · crispy-forms · openpyxl · JIRA API ·
Office365 REST (SharePoint) · SQLite (dev) / Oracle (prod cez cx_Oracle)

## Inštalácia

```bash
python -m venv venv
source venv/Scripts/activate          # Windows (Git Bash)
# source venv/bin/activate            # Linux / macOS

pip install -r requirements.txt

cp .env.example .env
# vyplň DJANGO_SECRET_KEY a FIELD_ENCRYPTION_KEY (príkazy sú v .env.example)

python manage.py migrate
python manage.py runserver
```

## Štruktúra

```
project/        # konfigurácia (settings, urls, wsgi/asgi, DB router)
work/           # hlavný modul – reporty, monitoring, EMS, používatelia
eets/           # modul EETS – reporty + JIRA integrácia
edz/            # modul EDZ – reporty
scheduler.py    # definície plánovaných úloh
manage.py
```

## Poznámky

- Aktívna databáza je SQLite (`db.sqlite3` sa necommituje). Produkčné pripojenie na Oracle
  je v kóde pripravené (zakomentované), vyžaduje `cx_Oracle` + Oracle client.
- Priečinky s dátami/reportmi/logmi (`Reports/`, `logs/`, `Scripts/`, `ems_logs/` …)
  sú v `.gitignore` a nie sú súčasťou repozitára.
