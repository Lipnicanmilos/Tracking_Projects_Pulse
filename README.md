# Tracking Projects Pulse

Interný **Django** nástroj na **automatizáciu reportingu a monitoringu** prevádzky.
Plánované úlohy generujú denné/týždenné reporty (Excel/PDF), sťahujú a parsujú serverové
logy cez SSH, integrujú sa na Oracle databázy, JIRA a SharePoint a distribuujú výstupy e-mailom.

> ⚠️ **Sanitizovaná verzia.** Všetky reálne dáta, prihlasovacie údaje, interné hostname-y
> a produkčné SQL boli odstránené alebo nahradené zástupnými hodnotami. Konfigurácia sa
> načítava z `.env` (mimo gitu). Dáta/logy/reporty sú v `.gitignore`.

## Automatizované procesy

Plánovač (APScheduler) spúšťa podľa CRON konfigurácie (`jobs.json`) tieto úlohy:

| Úloha | Popis |
|-------|-------|
| **Denné reporty** | Faktúry a vyrubené mýto (podľa kategórie/krajiny) – Excel + ZIP + e-mail |
| **Marketingové štatistiky** | Mesačné štatistiky z DWH → Excel |
| **EDZ podania** | Report elektronických podaní, upload na SharePoint |
| **EETS Lego / OBE positions** | EETS reporty a kontrola pozícií OBU |
| **PAYWELL** | Automatizovaný PAYWELL report |
| **Inactivity reporty (4M/6M)** | Týždenné reporty neaktivity účtov |
| **Rating monitoring** | Kontrola oceňovania mýtnych udalostí + notifikácie do JIRA |

## Parsovanie logov

Modul EMS sťahuje **realtime logy z aplikačných serverov cez SSH** (Paramiko), parsuje ich
(chybové hlásenia, web/POS/BO logy) a zobrazuje v dashboarde. Podporuje sťahovanie denných
logov, filtrovanie podľa typu a hromadné otvorenie logov naprieč servermi.

## Použité knižnice

| Oblasť | Knižnice |
|--------|----------|
| **Web / admin** | Django 4.1, django-jazzmin, django-crispy-forms |
| **Plánovanie** | APScheduler, django-apscheduler |
| **Databázy** | cx_Oracle (Oracle), pyodbc, Django ORM (SQLite dev) |
| **Reporty – Excel** | openpyxl, XlsxWriter, pandas |
| **Reporty – PDF** | ReportLab, xhtml2pdf |
| **Logy / SSH** | Paramiko |
| **Integrácie** | requests + JIRA REST API, Office365-REST (SharePoint), smtplib/email |
| **Bezpečnosť** | encrypted-model-fields, django-cryptography, python-dotenv |

## Stromová štruktúra

```
Tracking_Projects_Pulse/
├── project/                 # Django konfigurácia
│   ├── settings.py          # nastavenia, DB router, logging, scheduler config
│   ├── urls.py
│   ├── routers.py           # router pre viac databáz
│   ├── asgi.py · wsgi.py
│   └── __init__.py
├── work/                    # hlavný modul – reporty, monitoring, EMS, používatelia
│   ├── models.py            # CISDB / BILLDB / DWHDB (šifrované prístupy k DB)
│   ├── views.py             # dashboardy, logy, transakcie, autentifikácia
│   ├── views_ems.py         # EMS: parsovanie logov, denné reporty, PAYWELL, inactivity
│   ├── forms.py · urls.py · admin.py · jobs.py
│   ├── static/  ·  templates/  ·  migrations/
│   └── HPSM/
├── eets/                    # modul EETS – reporty + JIRA integrácia
│   ├── views.py · views_scheduler.py
│   ├── jira_service.py      # JIRA REST API klient
│   ├── models.py            # EETSDB, PROXYDB, SAIDAMD …
│   └── static/  ·  migrations/
├── edz/                     # modul EDZ – reporty (EDZ podania, CRV)
│   ├── views.py · jobs_non.py
│   └── static/  ·  migrations/
├── templates/               # spoločné šablóny
├── scheduler.py             # registrácia plánovaných úloh (APScheduler)
├── mark_stat.py             # marketingové štatistiky
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

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

## Poznámky

- Aktívna databáza je SQLite (`db.sqlite3` sa necommituje). Produkčné pripojenie na Oracle
  je v kóde pripravené, vyžaduje `cx_Oracle` + Oracle client.
- Prihlasovacie údaje k cieľovým DB sa ukladajú **šifrovane** (encrypted-model-fields).
- Priečinky s dátami/reportmi/logmi (`Reports/`, `logs/`, `Scripts/`, `ems_logs/` …)
  sú v `.gitignore` a nie sú súčasťou repozitára.
