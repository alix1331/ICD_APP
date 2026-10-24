<a id="english"></a>

# ICD Codes App: Documentation

**🇬🇧 English** · [🇮🇷 فارسی](#persian)

A Django 5 web application and REST API for browsing, searching, adding and deleting **ICD (International Classification of Diseases) codes**. The data is imported from `icd_codes.csv` into SQLite and is available through:

- a server-rendered web UI (search by category title / code, paginated, copy button, staff-only add and delete)
- a REST API in two flavors (function-based views under `/api/v1/`, class-based views under `/api/v2/`)
- auto-generated Swagger and ReDoc documentation

**Access model:** everyone can read. Only logged-in **staff** users (`is_staff=True`) can add or delete records, in both the web UI and the API.

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Project Structure](#2-project-structure)
3. [Getting Started](#3-getting-started)
4. [Configuration and Environment Variables](#4-configuration-and-environment-variables)
5. [Access Control](#5-access-control)
6. [URL Map](#6-url-map)
7. [Data Model](#7-data-model)
8. [Web UI](#8-web-ui)
9. [REST API Reference](#9-rest-api-reference)
10. [Code Reference, File by File](#10-code-reference-file-by-file)
11. [Data Import Command](#11-data-import-command)
12. [Tests](#12-tests)
13. [Deployment Notes](#13-deployment-notes)
14. [Known Limitations](#14-known-limitations)
15. [Change Log](#15-change-log)

---

## 1. Tech Stack

| Component | Package | Version |
|---|---|---|
| Web framework | Django | 5.0.1 |
| REST API | djangorestframework | 3.14.0 |
| Filtering (web UI) | django-filter | 23.5 |
| API docs (Swagger / ReDoc) | drf-yasg | 1.21.7 |
| CSV import | pandas | 2.2.0 |
| Database | SQLite 3 | bundled with Python |
| Front end | Bootstrap 5, Font Awesome 4.7, htmx, jQuery | served from `static/` and CDNs |

Full pinned dependencies are in `requirements.txt`.

---

## 2. Project Structure

```
ICD_APP/
├── manage.py                        # Django CLI entry point
├── requirements.txt                 # Pinned dependencies
├── db.sqlite3                       # SQLite database
├── icd_codes.csv                    # Source data for the import command
├── static/                          # bootstrap5/, css/style.css, js/ (main.js, htmx, jquery ...)
├── icdproject/                      # Project configuration
│   ├── settings.py                  # Settings (env-driven secrets, DRF, Swagger)
│   ├── urls.py                      # Root URLs (admin + icdapp)
│   ├── asgi.py
│   └── wsgi.py
└── icdapp/                          # The application
    ├── models.py                    # ICDModel
    ├── migrations/
    │   ├── 0001_initial.py          # Creates the table
    │   └── 0002_icdmodel_ordering_indexes.py   # Ordering, indexes, verbose names
    ├── admin.py                     # Admin configuration
    ├── permissions.py               # IsStaffOrReadOnly
    ├── serializers.py               # ICDSerializer, SearchQuerySerializer
    ├── forms.py                     # ICDForm (web "add" form)
    ├── filters.py                   # ICDSearchFilter (web search form)
    ├── views.py                     # Web views: index, about, add, delete
    ├── api.py                       # REST API views (v1 and v2)
    ├── urls.py                      # App URLs + Swagger/ReDoc schema view
    ├── tests.py                     # 44 tests
    ├── management/commands/
    │   └── import_icd_data.py       # CSV importer
    ├── templates/
    │   ├── base.html                # Layout: navbar, messages, scripts
    │   ├── index.html               # Search + results table
    │   ├── about.html
    │   ├── icd_form.html            # Add form
    │   └── icd_confirm_delete.html  # Delete confirmation
    └── templatetags/
        └── customizers.py           # Template filters (e.g. highlight_search)
```

---

## 3. Getting Started

### 3.1 Install

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3.2 Prepare the database

```powershell
python manage.py migrate
python manage.py import_icd_data --path icd_codes.csv
```

If you use the `db.sqlite3` that is already in the repository, the data is loaded and the import can be skipped. The import refuses to run on a non-empty table unless you pass `--replace` or `--append` (see section 11).

### 3.3 Create a staff account

No default admin account exists. Create one:

```powershell
python manage.py createsuperuser
```

To list existing staff accounts or reset a password:

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.filter(is_staff=True).values_list('username', flat=True)))"
python manage.py changepassword <username>
```

### 3.4 Run

```powershell
python manage.py runserver
```

| URL | Purpose |
|---|---|
| http://127.0.0.1:8000/ | Web UI |
| http://127.0.0.1:8000/about/ | About page |
| http://127.0.0.1:8000/swagger/ | Swagger UI |
| http://127.0.0.1:8000/redoc/ | ReDoc |
| http://127.0.0.1:8000/admin/ | Django admin, also the login page |

---

## 4. Configuration and Environment Variables

Configuration is in `icdproject/settings.py`. Deployment-specific values come from environment variables.

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_DEBUG` | `true` | `true` / `false` (also accepts `1`, `yes`, `on`) |
| `DJANGO_SECRET_KEY` | built-in dev key when debug is on | **Required** when `DJANGO_DEBUG=false`. The app refuses to start without it |
| `DJANGO_ALLOWED_HOSTS` | empty | Comma-separated host names, e.g. `example.com,www.example.com` |
| `API_CONTACT_EMAIL` | `contact@example.com` | Contact e-mail shown in Swagger / ReDoc |

PowerShell example:

```powershell
$env:DJANGO_DEBUG = "false"
$env:DJANGO_SECRET_KEY = "a-long-random-string"
$env:DJANGO_ALLOWED_HOSTS = "example.com"
```

### Other notable settings

| Setting | Value | Notes |
|---|---|---|
| `INSTALLED_APPS` | Django built-ins, `icdapp`, `rest_framework`, `drf_yasg`, `django_filters` | |
| `DATABASES` | SQLite at `BASE_DIR/db.sqlite3` | |
| `TIME_ZONE` / `USE_TZ` | `UTC` / `True` | |
| `STATIC_URL` | `static/` | |
| `STATICFILES_DIRS` | `[BASE_DIR/static]` | |
| `STATIC_ROOT` | `BASE_DIR/root` | Target of `collectstatic` |
| `LOGIN_URL` | `admin:login` | Where staff-only pages send anonymous visitors |
| `DEFAULT_AUTO_FIELD` | `BigAutoField` | |

### Django REST framework

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [SessionAuthentication, BasicAuthentication],
    "DEFAULT_PERMISSION_CLASSES": ["icdapp.permissions.IsStaffOrReadOnly"],
    "DEFAULT_THROTTLE_CLASSES": [AnonRateThrottle, UserRateThrottle],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min", "user": "600/min"},
}
```

Throttle counters live in Django's default cache (in-memory per process), so limits are per server process unless you configure a shared cache.

### Swagger

`SWAGGER_SETTINGS` defines HTTP Basic as a security scheme and enables session login, so the "Authorize" button and a logged-in admin session both work in `/swagger/`.

---

## 5. Access Control

| Action | Anonymous | Logged-in, not staff | Staff |
|---|---|---|---|
| View web UI, search, copy | ✔ | ✔ | ✔ |
| API: GET list / detail / search | ✔ | ✔ | ✔ |
| Web: add / delete | redirected to login | redirected to login | ✔ |
| API: POST (create) / DELETE | 401 or 403 | 403 | ✔ |

**API authentication:** HTTP Basic (`curl -u user:password`) or the session cookie. Basic auth sends the password with every request, so use HTTPS outside local development.

**Web pages:** `/icd/add/` and `/icd/<id>/delete/` use Django's `staff_member_required`, which redirects to `/admin/login/?next=...`. After logging in, staff return to the page they asked for.

---

## 6. URL Map

| Path | View | Name | Purpose |
|---|---|---|---|
| `admin/` | Django admin | n/a | Admin site and login |
| `` | `views.index_view` | `index` | Search and browse |
| `about/` | `views.about_view` | `about` | About page |
| `icd/add/` | `views.add_view` | `icd_add` | Add a record (staff) |
| `icd/<int:pk>/delete/` | `views.delete_view` | `icd_delete` | Delete a record (staff) |
| `swagger<format>/` | `schema_view.without_ui` | `schema-json` | `swagger.json` / `swagger.yaml` |
| `swagger/` | `schema_view.with_ui('swagger')` | `schema-swagger-ui` | Swagger UI |
| `redoc/` | `schema_view.with_ui('redoc')` | `schema-redoc` | ReDoc |
| `api/v1/icd/list/` | `api.icd_list_view` | `icd_list` | GET list, POST create |
| `api/v1/icd/code/<int:pk>` | `api.icd_retrieve_view` | `icd_retrieve` | GET one, DELETE |
| `api/v1/icd/search/` | `api.icd_search_view` | `icd_search` | Search |
| `api/v2/icd/list/` | `api.IcdCodeListAPIView` | `list_icd` | GET list, POST create |
| `api/v2/icd/list-search/` | `api.IcdCodeListAPIViewWithSearch` | `lists_icd` | List with optional `?query=` |
| `api/v2/icd/code/<int:pk>` | `api.IcdCodeRetrieveAPIView` | `retrieve_icd` | GET one, DELETE |
| `api/v2/icd/search/` | `api.IcdSearchAPIView` | `search_icd` | Search |

The detail URLs have **no trailing slash**. Ids must be integers, otherwise the response is a 404.

---

## 7. Data Model

`icdapp.models.ICDModel`, one row per ICD code.

| Field | Type | Max length | Null | Indexed | Description |
|---|---|---|---|---|---|
| `id` | `BigAutoField` | n/a | No | PK | Primary key |
| `category_code` | `CharField` | 50 | Yes | ✔ | Category the diagnosis belongs to |
| `diagnosis_code` | `CharField` | 100 | Yes | | Code of the specific diagnosis |
| `full_code` | `CharField` | 500 | Yes | ✔ | Complete ICD code |
| `abbreviated_description` | `CharField` | 5000 | Yes | | Short description |
| `full_description` | `CharField` | 5000 | Yes | | Long description |
| `category_title` | `CharField` | 200 | Yes | ✔ | Category name |

- `Meta.ordering = ["id"]`, so pagination is deterministic.
- `__str__` returns `full_code`, falling back to `category_code`, then `ICD #<id>`.
- The columns are nullable because the CSV has gaps. New records created through the API or web form must still have `category_code`, `full_code` and `full_description`.
- `full_code` is **not** unique at the database level (existing data may contain duplicates). Uniqueness for *new* records is checked in the serializer and form (case-insensitive).
- The indexes speed up exact and prefix lookups, such as the duplicate check. They do **not** speed up `icontains` searches (see section 14).

**Example record (illustrative values)**

```json
{
  "id": 1,
  "category_code": "A00",
  "diagnosis_code": "0",
  "full_code": "A000",
  "abbreviated_description": "Cholera due to Vibrio cholerae 01, biovar cholerae",
  "full_description": "Cholera due to Vibrio cholerae 01, biovar cholerae",
  "category_title": "Cholera"
}
```

---

## 8. Web UI

### 8.1 Home page: `/`

- Two search boxes (**category title**, **category code**), both case-insensitive "contains", combined with AND.
- A results table, 20 rows per page, with a **copy** button per row. Matches are highlighted in the description and title columns (`highlight_search` filter).
- The navbar search box calls the v2 search API through htmx and shows the response in the right-hand `#results` panel.
- **Staff only:** an **Add** button next to Search, and a red **trash** button in every row.

### 8.2 Add: `/icd/add/` (staff)

A form with the six data fields. `category_code`, `full_code` and `full_description` are required (marked with `*`). A duplicate `full_code` (case-insensitive) is rejected with an inline error. On success the user returns to the home page with the message "ICD code X was added."

### 8.3 Delete: `/icd/<id>/delete/` (staff)

- **GET** shows a confirmation page with the record's details. Nothing is deleted.
- **POST** (the "Yes, delete" button) deletes the record and returns to the home page with "ICD code X was deleted."
- An unknown id gives a 404.

### 8.4 Layout (`base.html`)

- Navbar: brand, Home, API (Swagger), **Add ICD code** (staff only), theme switcher, **Staff login** or **Log out (username)**, navbar search box.
- Logout is a small POST form, because Django 5 does not allow logout by GET.
- Flash messages (success / error) appear above the page content and can be dismissed.
- The page `<title>` comes from the `title` context value of each view (`block title`).

---

## 9. REST API Reference

Base URL during development: `http://127.0.0.1:8000`

### 9.1 Pagination

All list and search endpoints return the standard DRF envelope (the numbers below are illustrative):

```json
{
  "count": 74260,
  "next": "http://127.0.0.1:8000/api/v2/icd/list/?page=2",
  "previous": null,
  "results": [ { "id": 1, "...": "..." } ]
}
```

| | v1 | v2 |
|---|---|---|
| Page size | 10, fixed | 10 by default, `?page_size=N` up to 10,000 |
| Page parameter | `?page=N` | `?page=N` |

### 9.2 List: `GET`

`GET /api/v1/icd/list/`, `GET /api/v2/icd/list/`

```bash
curl "http://127.0.0.1:8000/api/v2/icd/list/?page=2&page_size=50"
```

### 9.3 List with optional search (v2 only): `GET`

`GET /api/v2/icd/list-search/?query=cholera`

Same as the v2 list, narrowed by `query` when it is given.

### 9.4 Retrieve: `GET`

`GET /api/v1/icd/code/<id>` or `GET /api/v2/icd/code/<id>`

`<id>` is the database id, not the ICD code. Returns one record, or `404` with `{"detail": "Not found."}`.

```bash
curl "http://127.0.0.1:8000/api/v2/icd/code/42"
```

### 9.5 Search: `GET`

`GET /api/v1/icd/search/?query=<text>` or `GET /api/v2/icd/search/?query=<text>`

| Parameter | Required | Description |
|---|---|---|
| `query` | No | Case-insensitive substring searched in `category_code`, `category_title` and `full_description` (OR). Leading and trailing spaces are ignored. An empty or missing query returns every record |
| `page` | No | Page number |
| `page_size` | No | v2 only |

```bash
curl "http://127.0.0.1:8000/api/v2/icd/search/?query=cholera&page=1"
```

### 9.6 Create: `POST` (staff)

`POST /api/v1/icd/list/` or `POST /api/v2/icd/list/`

| Field | Required | Notes |
|---|---|---|
| `category_code` | **Yes** | Not blank |
| `full_code` | **Yes** | Not blank; must not already exist (case-insensitive) |
| `full_description` | **Yes** | Not blank |
| `diagnosis_code`, `abbreviated_description`, `category_title` | No | |
| `id` | n/a | Read-only, ignored if sent |

```bash
curl -u staff:password -X POST http://127.0.0.1:8000/api/v2/icd/list/ \
     -H "Content-Type: application/json" \
     -d '{"category_code":"Z99","full_code":"Z991","full_description":"Example"}'
```

Responses:

| Status | Meaning | Body |
|---|---|---|
| `201 Created` | Record created | The new record |
| `400 Bad Request` | Validation failed | e.g. `{"full_code": ["An ICD record with this full code already exists."]}` |
| `401` / `403` | Not logged in / not staff | `{"detail": "..."}` |

### 9.7 Delete: `DELETE` (staff)

`DELETE /api/v1/icd/code/<id>` or `DELETE /api/v2/icd/code/<id>`

```bash
curl -u staff:password -X DELETE http://127.0.0.1:8000/api/v2/icd/code/123
```

| Status | Meaning |
|---|---|
| `204 No Content` | Deleted |
| `401` / `403` | Not logged in / not staff |
| `404` | No such id |

Deletion is permanent.

### 9.8 Interactive docs

- Swagger UI: `/swagger/`. Log in at `/admin/` first (or use "Authorize" with Basic auth) to try POST and DELETE.
- ReDoc: `/redoc/`
- Raw schema: `/swagger.json`, `/swagger.yaml`

### 9.9 Rate limits

Anonymous clients: 120 requests/minute. Authenticated clients: 600 requests/minute. Over the limit, the API answers `429 Too Many Requests`.

---

## 10. Code Reference, File by File

### `manage.py`
Standard Django CLI. Sets `DJANGO_SETTINGS_MODULE=icdproject.settings` and runs the command.

### `icdproject/settings.py`
See sections 4 and 5. Helper `_env_bool` parses boolean environment variables. When `DEBUG` is false and `DJANGO_SECRET_KEY` is empty, it raises `ImproperlyConfigured`.

### `icdproject/urls.py`
Mounts `admin/` and includes `icdapp.urls` at the site root.

### `icdproject/asgi.py`, `icdproject/wsgi.py`
Deployment entry points exposing `application`.

### `icdapp/models.py`
`ICDModel`. See section 7.

### `icdapp/migrations/`
- `0001_initial.py`: creates the table.
- `0002_icdmodel_ordering_indexes.py`: adds `ordering`, `verbose_name(_plural)`, and `db_index=True` on `category_code`, `full_code`, `category_title`.

### `icdapp/admin.py`
`ICDModelAdmin`: list columns `id, full_code, category_code, category_title, abbreviated_description`; search on `full_code, category_code, category_title, full_description`; 50 rows per page; `show_full_result_count = False` to avoid a slow `COUNT(*)`.

### `icdapp/permissions.py`
`IsStaffOrReadOnly`: safe methods (GET, HEAD, OPTIONS) are open to everyone. Other methods need `user.is_authenticated and user.is_staff`.

### `icdapp/serializers.py`

| Class | Purpose |
|---|---|
| `ICDSerializer` | `ModelSerializer` over all fields. `id` is read-only. `category_code`, `full_code`, `full_description` are required and non-blank. `validate_full_code` strips whitespace and rejects a case-insensitive duplicate (excluding the record itself when updating) |
| `SearchQuerySerializer` | One optional `query` field. Used only so Swagger shows the search parameter. It does not validate requests |

### `icdapp/forms.py`
`ICDForm` (`ModelForm`): the six data fields with Bootstrap `form-control` widgets (textareas for the descriptions). Marks the same three fields required and applies the same duplicate check in `clean_full_code`.

### `icdapp/filters.py`
`ICDSearchFilter` (`django_filters.FilterSet`): `category_title` and `category_code`, both `icontains`, rendered as text inputs.

### `icdapp/views.py`

| View | Access | Description |
|---|---|---|
| `index_view` | public | Applies `ICDSearchFilter`, paginates at 20, renders `index.html`. Context: `title`, `search_filter`, `page_obj`, `search_term`, `can_edit` (true for staff) |
| `about_view` | public | Renders `about.html` |
| `add_view` | staff | GET: empty form. POST: validate, save, flash message, redirect to `index`. Invalid: redisplay with errors |
| `delete_view` | staff | GET: confirmation page. POST: delete, flash message, redirect to `index`. 404 for unknown id |

`add_view` and `delete_view` accept only GET and POST.

### `icdapp/api.py`

Helpers:

| Name | Description |
|---|---|
| `StandardPagination` | 10 per page, fixed |
| `LargeResultsSetPagination` | 10 per page, `page_size` up to 10,000 |
| `filter_by_query(queryset, query)` | Strips `query`; empty returns the queryset unchanged; otherwise OR-filters `category_code`, `category_title`, `full_description` with `icontains` |

v1, function-based (decorator order: `swagger_auto_schema`, then `api_view`, then `permission_classes`):

| View | Methods | Description |
|---|---|---|
| `icd_list_view` | GET, POST | Paginated list; staff-only create (201) |
| `icd_retrieve_view` | GET, DELETE | One record; staff-only delete (204) |
| `icd_search_view` | GET | Paginated search |

v2, class-based:

| Class | Base | Description |
|---|---|---|
| `IcdCodeListAPIView` | `ListCreateAPIView` | List and create |
| `IcdCodeRetrieveAPIView` | `RetrieveDestroyAPIView` | Retrieve and delete |
| `IcdSearchAPIView` | `APIView` | Search with `LargeResultsSetPagination` |
| `IcdCodeListAPIViewWithSearch` | `ListAPIView` | List narrowed by optional `?query=` |

### `icdapp/urls.py`
Defines `schema_view` (title "ICD Codes API", version `v1`, public, contact e-mail from `settings.API_CONTACT_EMAIL`) and `urlpatterns` (section 6).

### `icdapp/templates/`
See section 8. `base.html` loads `bootstrap5/css/bootstrap.css`, `css/style.css`, and scripts `jquery.min.js`, `tether.min.js`, `main.js`, `popper.min.js`, `bootstrap.min.js`, `color-modes.js`, `htmx.min.js` from `static/`. Font Awesome, Boxicons, Material Icons and Bootstrap Icons come from CDNs. `index.html`'s copy button calls `CopyText2(id)`, which is expected to be defined in `static/js/main.js`.

### `icdapp/templatetags/customizers.py`
Provides template filters used by `index.html`, notably `highlight_search`. *This file was not available when this documentation was written, so its internals are not described here.*

### `icdapp/management/commands/import_icd_data.py`
See section 11.

---

## 11. Data Import Command

```powershell
python manage.py import_icd_data [--path FILE] [--replace | --append] [--batch-size N]
```

| Option | Default | Description |
|---|---|---|
| `--path` | `icd_codes.csv` | CSV file; relative paths resolve from the current directory |
| `--replace` | off | Delete all existing rows first, then import |
| `--append` | off | Import even though the table already has rows |
| `--batch-size` | `5000` | Rows per INSERT batch |

`--replace` and `--append` cannot be combined.

**Expected CSV columns:** an unnamed index column (ignored) followed by `category_code, diagnosis_code, full_code, abbreviated_description, full_description, category_title`.

**Behavior**

1. If the table already has rows and neither `--replace` nor `--append` is given, the command stops with an error, so a second run cannot silently duplicate everything.
2. The CSV is read in chunks of 20,000 rows with every value as text (`dtype=str`, `keep_default_na=False`). Codes such as `NA` or `0010` are kept exactly as written.
3. Surrounding whitespace is removed; empty cells are stored as `NULL`.
4. Everything runs in **one transaction**, so a failure part-way leaves the table unchanged (including with `--replace`).
5. Success prints `Finished importing N rows.`

**Errors:** a missing file or a CSV without the expected columns raises a `CommandError` with a clear message.

---

## 12. Tests

```powershell
python manage.py test
```

44 tests in `icdapp/tests.py`:

| Test class | Covers |
|---|---|
| `ModelTests` | `__str__`, default ordering |
| `ReadAPITests` | List pagination envelope, stable pages, `page_size`, retrieve, 404, search (v1 and v2), empty query, `list-search` route |
| `CreateAPITests` | Anonymous / non-staff / staff, v1 and v2, required fields, blank values, duplicate `full_code`, read-only `id` |
| `DeleteAPITests` | Anonymous / non-staff / staff, v1 and v2, 404 |
| `FormTests` | Required fields, duplicate check, save |
| `WebViewTests` | Index and filter, staff-only add and delete (redirects), confirmation page, add and delete flows, controls visible only to staff, flash messages, shared layout |
| `ImportCommandTests` | Import, `NULL` and text handling, refusal on second run, `--replace`, `--append`, missing file |

The test run uses a temporary database, so it never touches `db.sqlite3`.

---

## 13. Deployment Notes

- Set `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`.
- Run `python manage.py collectstatic` (output goes to `root/`) and serve it with your web server or a static-file middleware. Django does not serve static files when `DEBUG` is false.
- Serve over **HTTPS**, since the API accepts HTTP Basic credentials.
- Use a production WSGI/ASGI server (Gunicorn, Uvicorn), not `runserver`.
- Configure a shared cache (e.g. Redis) if you run several processes and want throttling to be global.
- Back up `db.sqlite3`. SQLite handles this app's read-heavy use, but concurrent writes are limited.

---

## 14. Known Limitations

| Area | Limitation |
|---|---|
| Search speed | `icontains` becomes `LIKE '%text%'`, which scans the table; ordinary indexes do not help. For fast text search use SQLite FTS5 or PostgreSQL with trigram / full-text indexes |
| Uniqueness | `full_code` uniqueness for new records is enforced in application code, not by a database constraint. Two simultaneous requests could in theory both pass the check |
| No update | There is no edit endpoint or page. Records can be added and deleted, and edited only through the Django admin |
| Pagination links | The "first / previous / next / last" links on the home page do not carry the search filters, so moving to another page drops the search |
| Navbar search | The htmx search box displays the raw JSON from the API in the side panel |
| Delete is permanent | There is no soft delete or undo |
| Detail URLs | No trailing slash on `api/.../code/<id>` (kept for compatibility) |
| `customizers.py` | Not documented (source was not provided) |

---

## 15. Change Log

**Added**
- Create and delete, in the API (staff only) and the web UI (staff only), with duplicate-code protection
- Staff-aware navbar (add link, login / logout), flash messages, delete confirmation page
- `IsStaffOrReadOnly` permission, throttling, Basic + session authentication
- `ICDForm`, `permissions.py`, migration `0002`, 44 tests

**Fixed**
- `api/v2/icd/list/` was registered twice, which made `IcdCodeListAPIViewWithSearch` unreachable. It now lives at `api/v2/icd/list-search/`
- List and search endpoints returned a bare array and lost pagination info. They now return `count / next / previous / results`
- Unordered querysets (unstable pagination) now have `ordering = ["id"]`
- `@swagger_auto_schema` was below `@api_view` and was ignored. The order is corrected
- Non-numeric ids in detail URLs returned a server error. They now return 404
- Secrets and debug mode moved from hardcoded values to environment variables
- The import command no longer duplicates data on re-run, handles empty cells and `NA` codes correctly, and runs in a transaction

**Behavior changes to be aware of**
- `GET /api/v1/icd/list/` and `/api/v1/icd/search/` return an object, not an array
- v2 search accepts `page_size`
- Search ignores surrounding spaces; an empty query returns all records

---

<a id="persian"></a>

<div dir="rtl" lang="fa">

# مستندات برنامه ICD Codes

[🇬🇧 English](#english) · **🇮🇷 فارسی**

یک برنامه وب و REST API مبتنی بر Django 5 برای **مرور، جست‌وجو، افزودن و حذف کدهای ICD** (طبقه‌بندی بین‌المللی بیماری‌ها). داده‌ها از فایل `icd_codes.csv` به SQLite وارد می‌شوند و از این راه‌ها در دسترس هستند:

- رابط کاربری وب (جست‌وجو بر اساس عنوان یا کد دسته، صفحه‌بندی، دکمه کپی، و افزودن/حذف فقط برای staff)
- یک REST API در دو نسخه (نمایش‌های تابعی در `/api/v1/` و نمایش‌های کلاسی در `/api/v2/`)
- مستندات خودکار Swagger و ReDoc

**سطح دسترسی:** همه می‌توانند بخوانند. فقط کاربران **staff** واردشده (`is_staff=True`) می‌توانند رکورد اضافه یا حذف کنند، چه در رابط وب و چه در API.

---

## فهرست مطالب

1. [فناوری‌های استفاده‌شده](#fa-1)
2. [ساختار پروژه](#fa-2)
3. [شروع کار](#fa-3)
4. [تنظیمات و متغیرهای محیطی](#fa-4)
5. [کنترل دسترسی](#fa-5)
6. [نقشه URL ها](#fa-6)
7. [مدل داده](#fa-7)
8. [رابط کاربری وب](#fa-8)
9. [مرجع REST API](#fa-9)
10. [مرجع کد، فایل به فایل](#fa-10)
11. [دستور ورود داده](#fa-11)
12. [تست‌ها](#fa-12)
13. [نکات استقرار](#fa-13)
14. [محدودیت‌های شناخته‌شده](#fa-14)
15. [تاریخچه تغییرات](#fa-15)

---

<a id="fa-1"></a>
## ۱. فناوری‌های استفاده‌شده

| بخش | بسته | نسخه |
|---|---|---|
| چارچوب وب | Django | 5.0.1 |
| REST API | djangorestframework | 3.14.0 |
| فیلتر کردن (رابط وب) | django-filter | 23.5 |
| مستندات API (Swagger / ReDoc) | drf-yasg | 1.21.7 |
| ورود فایل CSV | pandas | 2.2.0 |
| پایگاه داده | SQLite 3 | همراه پایتون |
| فرانت‌اند | Bootstrap 5، Font Awesome 4.7، htmx، jQuery | از `static/` و CDN ها |

فهرست کامل وابستگی‌ها با نسخه دقیق در `requirements.txt` است.

---

<a id="fa-2"></a>
## ۲. ساختار پروژه

(توضیحات داخل درخت زیر به انگلیسی نوشته شده‌اند.)

```
ICD_APP/
├── manage.py                        # Django CLI entry point
├── requirements.txt                 # Pinned dependencies
├── db.sqlite3                       # SQLite database
├── icd_codes.csv                    # Source data for the import command
├── static/                          # bootstrap5/, css/style.css, js/ (main.js, htmx, jquery ...)
├── icdproject/                      # Project configuration
│   ├── settings.py                  # Settings (env-driven secrets, DRF, Swagger)
│   ├── urls.py                      # Root URLs (admin + icdapp)
│   ├── asgi.py
│   └── wsgi.py
└── icdapp/                          # The application
    ├── models.py                    # ICDModel
    ├── migrations/
    │   ├── 0001_initial.py          # Creates the table
    │   └── 0002_icdmodel_ordering_indexes.py   # Ordering, indexes, verbose names
    ├── admin.py                     # Admin configuration
    ├── permissions.py               # IsStaffOrReadOnly
    ├── serializers.py               # ICDSerializer, SearchQuerySerializer
    ├── forms.py                     # ICDForm (web "add" form)
    ├── filters.py                   # ICDSearchFilter (web search form)
    ├── views.py                     # Web views: index, about, add, delete
    ├── api.py                       # REST API views (v1 and v2)
    ├── urls.py                      # App URLs + Swagger/ReDoc schema view
    ├── tests.py                     # 44 tests
    ├── management/commands/
    │   └── import_icd_data.py       # CSV importer
    ├── templates/
    │   ├── base.html                # Layout: navbar, messages, scripts
    │   ├── index.html               # Search + results table
    │   ├── about.html
    │   ├── icd_form.html            # Add form
    │   └── icd_confirm_delete.html  # Delete confirmation
    └── templatetags/
        └── customizers.py           # Template filters (e.g. highlight_search)
```

---

<a id="fa-3"></a>
## ۳. شروع کار

### ۳.۱ نصب

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ۳.۲ آماده‌سازی پایگاه داده

```powershell
python manage.py migrate
python manage.py import_icd_data --path icd_codes.csv
```

اگر از فایل `db.sqlite3` موجود در مخزن استفاده می‌کنید، داده‌ها از قبل بارگذاری شده‌اند و می‌توانید ورود داده را رد کنید. دستور ورود داده، اگر جدول خالی نباشد، بدون گزینه `--replace` یا `--append` اجرا نمی‌شود (بخش ۱۱ را ببینید).

### ۳.۳ ساخت حساب staff

هیچ حساب مدیر پیش‌فرضی وجود ندارد. یکی بسازید:

```powershell
python manage.py createsuperuser
```

برای دیدن فهرست حساب‌های staff موجود یا تغییر رمز عبور:

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.filter(is_staff=True).values_list('username', flat=True)))"
python manage.py changepassword <username>
```

### ۳.۴ اجرا

```powershell
python manage.py runserver
```

| آدرس | کاربرد |
|---|---|
| http://127.0.0.1:8000/ | رابط وب |
| http://127.0.0.1:8000/about/ | صفحه درباره |
| http://127.0.0.1:8000/swagger/ | Swagger UI |
| http://127.0.0.1:8000/redoc/ | ReDoc |
| http://127.0.0.1:8000/admin/ | پنل مدیریت Django و صفحه ورود |

---

<a id="fa-4"></a>
## ۴. تنظیمات و متغیرهای محیطی

تنظیمات در `icdproject/settings.py` هستند. مقادیر مربوط به استقرار از متغیرهای محیطی خوانده می‌شوند.

| متغیر | پیش‌فرض | کاربرد |
|---|---|---|
| `DJANGO_DEBUG` | `true` | مقدار `true` یا `false` (مقادیر `1`، `yes` و `on` هم پذیرفته می‌شوند) |
| `DJANGO_SECRET_KEY` | کلید توسعه داخلی، وقتی debug روشن است | وقتی `DJANGO_DEBUG=false` باشد **الزامی** است. بدون آن برنامه اجرا نمی‌شود |
| `DJANGO_ALLOWED_HOSTS` | خالی | نام میزبان‌ها با جداکننده کاما، مثلاً `example.com,www.example.com` |
| `API_CONTACT_EMAIL` | `contact@example.com` | ایمیل تماس که در Swagger / ReDoc نمایش داده می‌شود |

نمونه در PowerShell:

```powershell
$env:DJANGO_DEBUG = "false"
$env:DJANGO_SECRET_KEY = "a-long-random-string"
$env:DJANGO_ALLOWED_HOSTS = "example.com"
```

### سایر تنظیمات مهم

| تنظیم | مقدار | توضیح |
|---|---|---|
| `INSTALLED_APPS` | برنامه‌های داخلی Django، `icdapp`، `rest_framework`، `drf_yasg`، `django_filters` | |
| `DATABASES` | SQLite در `BASE_DIR/db.sqlite3` | |
| `TIME_ZONE` / `USE_TZ` | `UTC` / `True` | |
| `STATIC_URL` | `static/` | |
| `STATICFILES_DIRS` | `[BASE_DIR/static]` | |
| `STATIC_ROOT` | `BASE_DIR/root` | مقصد دستور `collectstatic` |
| `LOGIN_URL` | `admin:login` | جایی که بازدیدکننده ناشناس از صفحات مخصوص staff به آن هدایت می‌شود |
| `DEFAULT_AUTO_FIELD` | `BigAutoField` | |

### Django REST framework

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [SessionAuthentication, BasicAuthentication],
    "DEFAULT_PERMISSION_CLASSES": ["icdapp.permissions.IsStaffOrReadOnly"],
    "DEFAULT_THROTTLE_CLASSES": [AnonRateThrottle, UserRateThrottle],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min", "user": "600/min"},
}
```

شمارنده‌های محدودسازی نرخ در حافظه (cache) پیش‌فرض Django نگهداری می‌شوند و جداگانه برای هر پردازه سرور هستند، مگر اینکه cache مشترک تنظیم کنید.

### Swagger

`SWAGGER_SETTINGS` احراز هویت HTTP Basic را به‌عنوان یک روش امنیتی تعریف می‌کند و ورود با session را هم فعال می‌کند. بنابراین دکمه «Authorize» و نشست یک مدیر واردشده، هر دو در `/swagger/` کار می‌کنند.

---

<a id="fa-5"></a>
## ۵. کنترل دسترسی

| عملیات | کاربر ناشناس | کاربر واردشده، غیر staff | Staff |
|---|---|---|---|
| مشاهده رابط وب، جست‌وجو، کپی | ✔ | ✔ | ✔ |
| API: دستورهای GET برای فهرست / جزئیات / جست‌وجو | ✔ | ✔ | ✔ |
| وب: افزودن / حذف | هدایت به صفحه ورود | هدایت به صفحه ورود | ✔ |
| API: ایجاد (POST) / حذف (DELETE) | 401 یا 403 | 403 | ✔ |

**احراز هویت API:** HTTP Basic (با `curl -u user:password`) یا کوکی session. احراز هویت Basic رمز عبور را در هر درخواست می‌فرستد، پس خارج از توسعه محلی از HTTPS استفاده کنید.

**صفحات وب:** صفحه‌های `/icd/add/` و `/icd/<id>/delete/` از `staff_member_required` در Django استفاده می‌کنند که به `/admin/login/?next=...` هدایت می‌کند. پس از ورود، staff به همان صفحه‌ای که خواسته بود برمی‌گردد.

---

<a id="fa-6"></a>
## ۶. نقشه URL ها

| مسیر | نمایش (View) | نام | کاربرد |
|---|---|---|---|
| `admin/` | پنل مدیریت Django | ندارد | سایت مدیریت و صفحه ورود |
| `` | `views.index_view` | `index` | جست‌وجو و مرور |
| `about/` | `views.about_view` | `about` | صفحه درباره |
| `icd/add/` | `views.add_view` | `icd_add` | افزودن رکورد (staff) |
| `icd/<int:pk>/delete/` | `views.delete_view` | `icd_delete` | حذف رکورد (staff) |
| `swagger<format>/` | `schema_view.without_ui` | `schema-json` | `swagger.json` / `swagger.yaml` |
| `swagger/` | `schema_view.with_ui('swagger')` | `schema-swagger-ui` | Swagger UI |
| `redoc/` | `schema_view.with_ui('redoc')` | `schema-redoc` | ReDoc |
| `api/v1/icd/list/` | `api.icd_list_view` | `icd_list` | GET فهرست، POST ایجاد |
| `api/v1/icd/code/<int:pk>` | `api.icd_retrieve_view` | `icd_retrieve` | GET یک رکورد، DELETE |
| `api/v1/icd/search/` | `api.icd_search_view` | `icd_search` | جست‌وجو |
| `api/v2/icd/list/` | `api.IcdCodeListAPIView` | `list_icd` | GET فهرست، POST ایجاد |
| `api/v2/icd/list-search/` | `api.IcdCodeListAPIViewWithSearch` | `lists_icd` | فهرست با `?query=` اختیاری |
| `api/v2/icd/code/<int:pk>` | `api.IcdCodeRetrieveAPIView` | `retrieve_icd` | GET یک رکورد، DELETE |
| `api/v2/icd/search/` | `api.IcdSearchAPIView` | `search_icd` | جست‌وجو |

آدرس‌های جزئیات **اسلش پایانی ندارند**. شناسه باید عدد صحیح باشد، در غیر این صورت پاسخ 404 است.

---

<a id="fa-7"></a>
## ۷. مدل داده

`icdapp.models.ICDModel`، یک ردیف برای هر کد ICD.

| فیلد | نوع | حداکثر طول | می‌تواند Null باشد | ایندکس | توضیح |
|---|---|---|---|---|---|
| `id` | `BigAutoField` | ندارد | خیر | کلید اصلی | کلید اصلی |
| `category_code` | `CharField` | 50 | بله | ✔ | دسته‌ای که تشخیص به آن تعلق دارد |
| `diagnosis_code` | `CharField` | 100 | بله | | کد تشخیص مشخص |
| `full_code` | `CharField` | 500 | بله | ✔ | کد کامل ICD |
| `abbreviated_description` | `CharField` | 5000 | بله | | توضیح کوتاه |
| `full_description` | `CharField` | 5000 | بله | | توضیح کامل |
| `category_title` | `CharField` | 200 | بله | ✔ | نام دسته |

- `Meta.ordering = ["id"]` است، پس صفحه‌بندی قطعی و پایدار است.
- متد `__str__` مقدار `full_code` را برمی‌گرداند؛ اگر نبود `category_code`، و اگر آن هم نبود `ICD #<id>`.
- ستون‌ها Null‌پذیر هستند چون فایل CSV جاهای خالی دارد. اما رکوردهای جدیدی که از راه API یا فرم وب ساخته می‌شوند باید حتماً `category_code`، `full_code` و `full_description` داشته باشند.
- یکتایی `full_code` در سطح پایگاه داده **اعمال نشده** است (داده‌های موجود ممکن است تکراری داشته باشند). یکتایی برای رکوردهای *جدید* در serializer و فرم بررسی می‌شود (بدون حساسیت به حروف بزرگ و کوچک).
- ایندکس‌ها جست‌وجوی دقیق و پیشوندی را سریع‌تر می‌کنند، مثل بررسی تکراری بودن. آن‌ها جست‌وجوی `icontains` را سریع‌تر **نمی‌کنند** (بخش ۱۴ را ببینید).

**نمونه رکورد (مقادیر نمونه)**

```json
{
  "id": 1,
  "category_code": "A00",
  "diagnosis_code": "0",
  "full_code": "A000",
  "abbreviated_description": "Cholera due to Vibrio cholerae 01, biovar cholerae",
  "full_description": "Cholera due to Vibrio cholerae 01, biovar cholerae",
  "category_title": "Cholera"
}
```

---

<a id="fa-8"></a>
## ۸. رابط کاربری وب

### ۸.۱ صفحه اصلی: `/`

- دو کادر جست‌وجو (**عنوان دسته** و **کد دسته**) که هر دو «شامل بودن» بدون حساسیت به حروف هستند و با AND ترکیب می‌شوند.
- یک جدول نتایج، ۲۰ ردیف در هر صفحه، با دکمه **کپی** برای هر ردیف. موارد منطبق در ستون‌های توضیح و عنوان هایلایت می‌شوند (فیلتر `highlight_search`).
- کادر جست‌وجوی نوار بالا از طریق htmx جست‌وجوی API نسخه ۲ را صدا می‌زند و پاسخ را در پنل سمت راست `#results` نشان می‌دهد.
- **فقط staff:** دکمه **Add** کنار دکمه جست‌وجو، و یک دکمه قرمز **سطل زباله** در هر ردیف.

### ۸.۲ افزودن: `/icd/add/` (staff)

فرمی با شش فیلد داده. فیلدهای `category_code`، `full_code` و `full_description` اجباری هستند (با `*` مشخص شده‌اند). `full_code` تکراری (بدون حساسیت به حروف) با خطای درون‌خطی رد می‌شود. در صورت موفقیت، کاربر با پیام «ICD code X was added.» به صفحه اصلی برمی‌گردد.

### ۸.۳ حذف: `/icd/<id>/delete/` (staff)

- **GET** یک صفحه تأیید با جزئیات رکورد نشان می‌دهد. چیزی حذف نمی‌شود.
- **POST** (دکمه «Yes, delete») رکورد را حذف می‌کند و با پیام «ICD code X was deleted.» به صفحه اصلی برمی‌گرداند.
- شناسه ناشناخته پاسخ 404 می‌دهد.

### ۸.۴ قالب کلی (`base.html`)

- نوار بالا: نام برند، Home، API (Swagger)، **Add ICD code** (فقط staff)، تغییر تم، **Staff login** یا **Log out (username)**، و کادر جست‌وجو.
- خروج از حساب یک فرم POST کوچک است، چون Django 5 خروج با GET را مجاز نمی‌داند.
- پیام‌های موقت (موفقیت / خطا) بالای محتوای صفحه نمایش داده می‌شوند و قابل بستن هستند.
- عنوان `<title>` صفحه از مقدار `title` در context هر view می‌آید (`block title`).

---

<a id="fa-9"></a>
## ۹. مرجع REST API

آدرس پایه در توسعه: `http://127.0.0.1:8000`

### ۹.۱ صفحه‌بندی

همه نقاط پایانی فهرست و جست‌وجو، پاکت استاندارد DRF را برمی‌گردانند (اعداد زیر نمونه هستند):

```json
{
  "count": 74260,
  "next": "http://127.0.0.1:8000/api/v2/icd/list/?page=2",
  "previous": null,
  "results": [ { "id": 1, "...": "..." } ]
}
```

| | نسخه 1 | نسخه 2 |
|---|---|---|
| اندازه صفحه | 10، ثابت | پیش‌فرض 10، با `?page_size=N` تا حداکثر 10,000 |
| پارامتر صفحه | `?page=N` | `?page=N` |

### ۹.۲ فهرست: `GET`

`GET /api/v1/icd/list/` و `GET /api/v2/icd/list/`

```bash
curl "http://127.0.0.1:8000/api/v2/icd/list/?page=2&page_size=50"
```

### ۹.۳ فهرست با جست‌وجوی اختیاری (فقط نسخه 2): `GET`

`GET /api/v2/icd/list-search/?query=cholera`

مثل فهرست نسخه 2 است، با این تفاوت که اگر `query` داده شود نتایج را محدود می‌کند.

### ۹.۴ دریافت یک رکورد: `GET`

`GET /api/v1/icd/code/<id>` یا `GET /api/v2/icd/code/<id>`

`<id>` شناسه پایگاه داده است، نه خود کد ICD. یک رکورد برمی‌گرداند، یا `404` همراه با `{"detail": "Not found."}`.

```bash
curl "http://127.0.0.1:8000/api/v2/icd/code/42"
```

### ۹.۵ جست‌وجو: `GET`

`GET /api/v1/icd/search/?query=<text>` یا `GET /api/v2/icd/search/?query=<text>`

| پارامتر | اجباری | توضیح |
|---|---|---|
| `query` | خیر | زیررشته بدون حساسیت به حروف که در `category_code`، `category_title` و `full_description` جست‌وجو می‌شود (با OR). فاصله‌های ابتدا و انتها نادیده گرفته می‌شوند. `query` خالی یا ارسال‌نشده، همه رکوردها را برمی‌گرداند |
| `page` | خیر | شماره صفحه |
| `page_size` | خیر | فقط نسخه 2 |

```bash
curl "http://127.0.0.1:8000/api/v2/icd/search/?query=cholera&page=1"
```

### ۹.۶ ایجاد: `POST` (staff)

`POST /api/v1/icd/list/` یا `POST /api/v2/icd/list/`

| فیلد | اجباری | توضیح |
|---|---|---|
| `category_code` | **بله** | خالی نباشد |
| `full_code` | **بله** | خالی نباشد؛ نباید از قبل وجود داشته باشد (بدون حساسیت به حروف) |
| `full_description` | **بله** | خالی نباشد |
| `diagnosis_code`، `abbreviated_description`، `category_title` | خیر | |
| `id` | ندارد | فقط‌خواندنی است؛ اگر ارسال شود نادیده گرفته می‌شود |

```bash
curl -u staff:password -X POST http://127.0.0.1:8000/api/v2/icd/list/ \
     -H "Content-Type: application/json" \
     -d '{"category_code":"Z99","full_code":"Z991","full_description":"Example"}'
```

پاسخ‌ها:

| وضعیت | معنی | بدنه |
|---|---|---|
| `201 Created` | رکورد ساخته شد | رکورد جدید |
| `400 Bad Request` | اعتبارسنجی ناموفق | مثلاً `{"full_code": ["An ICD record with this full code already exists."]}` |
| `401` / `403` | وارد نشده / staff نیست | `{"detail": "..."}` |

### ۹.۷ حذف: `DELETE` (staff)

`DELETE /api/v1/icd/code/<id>` یا `DELETE /api/v2/icd/code/<id>`

```bash
curl -u staff:password -X DELETE http://127.0.0.1:8000/api/v2/icd/code/123
```

| وضعیت | معنی |
|---|---|
| `204 No Content` | حذف شد |
| `401` / `403` | وارد نشده / staff نیست |
| `404` | چنین شناسه‌ای وجود ندارد |

حذف دائمی است.

### ۹.۸ مستندات تعاملی

- Swagger UI: ‏`/swagger/`. برای امتحان POST و DELETE ابتدا در `/admin/` وارد شوید (یا از «Authorize» با احراز هویت Basic استفاده کنید).
- ReDoc: ‏`/redoc/`
- Schema خام: ‏`/swagger.json` و `/swagger.yaml`

### ۹.۹ محدودیت نرخ درخواست

کاربران ناشناس: 120 درخواست در دقیقه. کاربران احراز هویت‌شده: 600 درخواست در دقیقه. در صورت عبور از حد مجاز، API پاسخ `429 Too Many Requests` می‌دهد.

---

<a id="fa-10"></a>
## ۱۰. مرجع کد، فایل به فایل

### `manage.py`
ابزار خط فرمان استاندارد Django. مقدار `DJANGO_SETTINGS_MODULE=icdproject.settings` را تنظیم می‌کند و دستور را اجرا می‌کند.

### `icdproject/settings.py`
بخش‌های ۴ و ۵ را ببینید. تابع کمکی `_env_bool` متغیرهای محیطی بولی را تفسیر می‌کند. وقتی `DEBUG` خاموش باشد و `DJANGO_SECRET_KEY` خالی باشد، خطای `ImproperlyConfigured` ایجاد می‌شود.

### `icdproject/urls.py`
مسیر `admin/` را نصب می‌کند و `icdapp.urls` را در ریشه سایت include می‌کند.

### `icdproject/asgi.py` و `icdproject/wsgi.py`
نقاط ورود برای استقرار که `application` را در اختیار می‌گذارند.

### `icdapp/models.py`
مدل `ICDModel`. بخش ۷ را ببینید.

### `icdapp/migrations/`
- `0001_initial.py`: جدول را می‌سازد.
- `0002_icdmodel_ordering_indexes.py`: مقادیر `ordering` و `verbose_name(_plural)` را اضافه می‌کند و `db_index=True` را روی `category_code`، `full_code` و `category_title` قرار می‌دهد.

### `icdapp/admin.py`
`ICDModelAdmin`: ستون‌های فهرست `id, full_code, category_code, category_title, abbreviated_description`؛ جست‌وجو روی `full_code, category_code, category_title, full_description`؛ ۵۰ ردیف در هر صفحه؛ و `show_full_result_count = False` برای جلوگیری از `COUNT(*)` کند.

### `icdapp/permissions.py`
`IsStaffOrReadOnly`: متدهای امن (GET، HEAD، OPTIONS) برای همه آزاد هستند. بقیه متدها نیاز به `user.is_authenticated and user.is_staff` دارند.

### `icdapp/serializers.py`

| کلاس | کاربرد |
|---|---|
| `ICDSerializer` | یک `ModelSerializer` روی همه فیلدها. `id` فقط‌خواندنی است. `category_code`، `full_code` و `full_description` اجباری و غیرخالی هستند. `validate_full_code` فاصله‌های اضافه را حذف می‌کند و تکراری بودن (بدون حساسیت به حروف) را رد می‌کند (هنگام به‌روزرسانی، خود رکورد مستثنا می‌شود) |
| `SearchQuerySerializer` | یک فیلد اختیاری `query`. فقط برای اینکه Swagger پارامتر جست‌وجو را نشان دهد استفاده می‌شود و درخواست‌ها را اعتبارسنجی نمی‌کند |

### `icdapp/forms.py`
`ICDForm` (یک `ModelForm`): شش فیلد داده با ویجت‌های `form-control` بوت‌استرپ (برای توضیحات از textarea). همان سه فیلد را اجباری می‌کند و همان بررسی تکراری بودن را در `clean_full_code` اعمال می‌کند.

### `icdapp/filters.py`
`ICDSearchFilter` (یک `django_filters.FilterSet`): فیلدهای `category_title` و `category_code`، هر دو با `icontains`، که به‌صورت کادر متن نمایش داده می‌شوند.

### `icdapp/views.py`

| View | دسترسی | توضیح |
|---|---|---|
| `index_view` | عمومی | `ICDSearchFilter` را اعمال می‌کند، با ۲۰ ردیف در هر صفحه صفحه‌بندی می‌کند و `index.html` را رندر می‌کند. مقادیر context: ‏`title`، `search_filter`، `page_obj`، `search_term`، و `can_edit` (برای staff درست است) |
| `about_view` | عمومی | `about.html` را رندر می‌کند |
| `add_view` | staff | GET: فرم خالی. POST: اعتبارسنجی، ذخیره، پیام موقت، هدایت به `index`. اگر نامعتبر باشد فرم دوباره با خطاها نمایش داده می‌شود |
| `delete_view` | staff | GET: صفحه تأیید. POST: حذف، پیام موقت، هدایت به `index`. شناسه ناشناخته 404 می‌دهد |

`add_view` و `delete_view` فقط GET و POST را می‌پذیرند.

### `icdapp/api.py`

توابع و کلاس‌های کمکی:

| نام | توضیح |
|---|---|
| `StandardPagination` | ۱۰ مورد در هر صفحه، ثابت |
| `LargeResultsSetPagination` | ۱۰ مورد در هر صفحه، با `page_size` تا ۱۰٬۰۰۰ |
| `filter_by_query(queryset, query)` | `query` را از فاصله‌های اضافه پاک می‌کند؛ اگر خالی باشد queryset را بدون تغییر برمی‌گرداند؛ در غیر این صورت `category_code`، `category_title` و `full_description` را با `icontains` و OR فیلتر می‌کند |

نسخه ۱، تابعی (ترتیب دکوراتورها: `swagger_auto_schema`، بعد `api_view`، بعد `permission_classes`):

| View | متدها | توضیح |
|---|---|---|
| `icd_list_view` | GET، POST | فهرست صفحه‌بندی‌شده؛ ایجاد فقط برای staff (201) |
| `icd_retrieve_view` | GET، DELETE | یک رکورد؛ حذف فقط برای staff (204) |
| `icd_search_view` | GET | جست‌وجوی صفحه‌بندی‌شده |

نسخه ۲، کلاسی:

| کلاس | پایه | توضیح |
|---|---|---|
| `IcdCodeListAPIView` | `ListCreateAPIView` | فهرست و ایجاد |
| `IcdCodeRetrieveAPIView` | `RetrieveDestroyAPIView` | دریافت و حذف |
| `IcdSearchAPIView` | `APIView` | جست‌وجو با `LargeResultsSetPagination` |
| `IcdCodeListAPIViewWithSearch` | `ListAPIView` | فهرست محدودشده با `?query=` اختیاری |

### `icdapp/urls.py`
`schema_view` (عنوان «ICD Codes API»، نسخه `v1`، عمومی، ایمیل تماس از `settings.API_CONTACT_EMAIL`) و `urlpatterns` را تعریف می‌کند (بخش ۶).

### `icdapp/templates/`
بخش ۸ را ببینید. `base.html` فایل‌های `bootstrap5/css/bootstrap.css` و `css/style.css` و اسکریپت‌های `jquery.min.js`، `tether.min.js`، `main.js`، `popper.min.js`، `bootstrap.min.js`، `color-modes.js` و `htmx.min.js` را از `static/` بارگذاری می‌کند. Font Awesome، Boxicons، Material Icons و Bootstrap Icons از CDN می‌آیند. دکمه کپی در `index.html` تابع `CopyText2(id)` را صدا می‌زند که انتظار می‌رود در `static/js/main.js` تعریف شده باشد.

### `icdapp/templatetags/customizers.py`
فیلترهای قالبی مورد استفاده `index.html` را فراهم می‌کند، به‌ویژه `highlight_search`. *این فایل هنگام نوشتن این مستندات در دسترس نبود، پس جزئیات داخلی آن در اینجا شرح داده نشده است.*

### `icdapp/management/commands/import_icd_data.py`
بخش ۱۱ را ببینید.

---

<a id="fa-11"></a>
## ۱۱. دستور ورود داده

```powershell
python manage.py import_icd_data [--path FILE] [--replace | --append] [--batch-size N]
```

| گزینه | پیش‌فرض | توضیح |
|---|---|---|
| `--path` | `icd_codes.csv` | فایل CSV؛ مسیر نسبی از پوشه‌ای که دستور در آن اجرا می‌شود حل می‌شود |
| `--replace` | خاموش | ابتدا همه ردیف‌های موجود را حذف می‌کند، سپس وارد می‌کند |
| `--append` | خاموش | حتی اگر جدول از قبل ردیف داشته باشد، وارد می‌کند |
| `--batch-size` | `5000` | تعداد ردیف در هر دسته INSERT |

گزینه‌های `--replace` و `--append` را نمی‌توان با هم به کار برد.

**ستون‌های مورد انتظار CSV:** یک ستون ایندکس بدون نام (نادیده گرفته می‌شود) و بعد از آن `category_code, diagnosis_code, full_code, abbreviated_description, full_description, category_title`.

**رفتار دستور**

1. اگر جدول از قبل ردیف داشته باشد و نه `--replace` داده شده باشد نه `--append`، دستور با یک خطا متوقف می‌شود، تا اجرای دوباره نتواند بی‌صدا همه چیز را تکراری کند.
2. فایل CSV در دسته‌های ۲۰٬۰۰۰ ردیفی خوانده می‌شود و همه مقادیر به‌صورت متن هستند (`dtype=str`، `keep_default_na=False`). کدهایی مثل `NA` یا `0010` دقیقاً همان‌طور که نوشته شده‌اند نگه داشته می‌شوند.
3. فاصله‌های اطراف مقادیر حذف می‌شوند و سلول‌های خالی به‌صورت `NULL` ذخیره می‌شوند.
4. همه کارها در **یک تراکنش** انجام می‌شود، پس اگر وسط کار خطایی رخ دهد جدول بدون تغییر می‌ماند (حتی با `--replace`).
5. در صورت موفقیت پیام `Finished importing N rows.` چاپ می‌شود.

**خطاها:** نبودن فایل یا نبودن ستون‌های مورد انتظار در CSV، یک `CommandError` با پیام روشن ایجاد می‌کند.

---

<a id="fa-12"></a>
## ۱۲. تست‌ها

```powershell
python manage.py test
```

۴۴ تست در `icdapp/tests.py`:

| کلاس تست | موارد پوشش‌داده‌شده |
|---|---|
| `ModelTests` | `__str__`، ترتیب پیش‌فرض |
| `ReadAPITests` | پاکت صفحه‌بندی فهرست، صفحه‌های پایدار، `page_size`، دریافت یک رکورد، 404، جست‌وجو (نسخه 1 و 2)، `query` خالی، مسیر `list-search` |
| `CreateAPITests` | ناشناس / غیر staff / staff، نسخه 1 و 2، فیلدهای اجباری، مقادیر خالی، `full_code` تکراری، `id` فقط‌خواندنی |
| `DeleteAPITests` | ناشناس / غیر staff / staff، نسخه 1 و 2، 404 |
| `FormTests` | فیلدهای اجباری، بررسی تکراری بودن، ذخیره |
| `WebViewTests` | صفحه اصلی و فیلتر، افزودن و حذف مخصوص staff (هدایت‌ها)، صفحه تأیید، روند افزودن و حذف، نمایش کنترل‌ها فقط برای staff، پیام‌های موقت، قالب مشترک |
| `ImportCommandTests` | ورود داده، مدیریت `NULL` و متن، رد اجرای دوم، `--replace`، `--append`، نبودن فایل |

اجرای تست‌ها از یک پایگاه داده موقت استفاده می‌کند و هرگز به `db.sqlite3` دست نمی‌زند.

---

<a id="fa-13"></a>
## ۱۳. نکات استقرار

- مقادیر `DJANGO_DEBUG=false`، `DJANGO_SECRET_KEY` و `DJANGO_ALLOWED_HOSTS` را تنظیم کنید.
- دستور `python manage.py collectstatic` را اجرا کنید (خروجی در `root/` قرار می‌گیرد) و آن را با وب‌سرور یا یک middleware فایل‌های استاتیک سرو کنید. وقتی `DEBUG` خاموش است، Django فایل‌های استاتیک را سرو نمی‌کند.
- از **HTTPS** استفاده کنید، چون API اطلاعات HTTP Basic را می‌پذیرد.
- از یک سرور WSGI/ASGI مناسب تولید (Gunicorn، Uvicorn) استفاده کنید، نه `runserver`.
- اگر چند پردازه اجرا می‌کنید و می‌خواهید محدودسازی نرخ سراسری باشد، یک cache مشترک (مثلاً Redis) تنظیم کنید.
- از `db.sqlite3` نسخه پشتیبان بگیرید. SQLite برای الگوی استفاده این برنامه (عمدتاً خواندن) کافی است، اما نوشتن هم‌زمان محدود است.

---

<a id="fa-14"></a>
## ۱۴. محدودیت‌های شناخته‌شده

| حوزه | محدودیت |
|---|---|
| سرعت جست‌وجو | `icontains` به `LIKE '%text%'` تبدیل می‌شود که کل جدول را اسکن می‌کند؛ ایندکس‌های معمولی کمکی نمی‌کنند. برای جست‌وجوی متنی سریع از SQLite FTS5 یا PostgreSQL با ایندکس‌های trigram / full-text استفاده کنید |
| یکتایی | یکتایی `full_code` برای رکوردهای جدید در کد برنامه اعمال می‌شود، نه با قید پایگاه داده. دو درخواست هم‌زمان در تئوری می‌توانند هر دو از بررسی رد شوند |
| نبود ویرایش | نقطه پایانی یا صفحه‌ای برای ویرایش وجود ندارد. رکوردها را می‌توان اضافه و حذف کرد، و ویرایش فقط از طریق پنل مدیریت Django ممکن است |
| لینک‌های صفحه‌بندی | لینک‌های «first / previous / next / last» در صفحه اصلی فیلترهای جست‌وجو را حمل نمی‌کنند، پس رفتن به صفحه دیگر جست‌وجو را از بین می‌برد |
| جست‌وجوی نوار بالا | کادر جست‌وجوی htmx، JSON خام API را در پنل کناری نشان می‌دهد |
| حذف دائمی است | حذف نرم (soft delete) یا بازگردانی وجود ندارد |
| آدرس‌های جزئیات | آدرس `api/.../code/<id>` اسلش پایانی ندارد (برای سازگاری حفظ شده) |
| `customizers.py` | مستند نشده است (کد آن در اختیار نبود) |

---

<a id="fa-15"></a>
## ۱۵. تاریخچه تغییرات

**اضافه‌شده**
- ایجاد و حذف، در API (فقط staff) و رابط وب (فقط staff)، همراه با جلوگیری از کد تکراری
- نوار بالای آگاه از staff (لینک افزودن، ورود / خروج)، پیام‌های موقت، صفحه تأیید حذف
- مجوز `IsStaffOrReadOnly`، محدودسازی نرخ، احراز هویت Basic + session
- `ICDForm`، فایل `permissions.py`، مهاجرت `0002`، و ۴۴ تست

**رفع‌شده**
- مسیر `api/v2/icd/list/` دو بار ثبت شده بود و باعث می‌شد `IcdCodeListAPIViewWithSearch` در دسترس نباشد. حالا در `api/v2/icd/list-search/` است
- نقاط پایانی فهرست و جست‌وجو آرایه ساده برمی‌گرداندند و اطلاعات صفحه‌بندی را از دست می‌دادند. حالا `count / next / previous / results` برمی‌گردانند
- querysetهای بدون ترتیب (صفحه‌بندی ناپایدار) حالا `ordering = ["id"]` دارند
- دکوراتور `@swagger_auto_schema` زیر `@api_view` بود و نادیده گرفته می‌شد. ترتیب اصلاح شد
- شناسه‌های غیرعددی در آدرس‌های جزئیات خطای سرور می‌دادند. حالا 404 می‌دهند
- رازها و حالت debug از مقادیر ثابت داخل کد به متغیرهای محیطی منتقل شدند
- دستور ورود داده دیگر در اجرای دوباره داده را تکراری نمی‌کند، سلول‌های خالی و کدهای `NA` را درست مدیریت می‌کند، و در یک تراکنش اجرا می‌شود

**تغییرات رفتاری که باید بدانید**
- `GET /api/v1/icd/list/` و `/api/v1/icd/search/` یک شیء برمی‌گردانند، نه آرایه
- جست‌وجوی نسخه 2 پارامتر `page_size` را می‌پذیرد
- جست‌وجو فاصله‌های ابتدا و انتها را نادیده می‌گیرد؛ `query` خالی همه رکوردها را برمی‌گرداند

</div>
