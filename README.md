# ICD Codes: ثبت و جست‌وجوی کدهای ICD

<div dir="rtl" lang="fa">

پروژه عملی درس مهندسی اینترنت: یک وب‌سایت ساده برای **ثبت** و **جست‌وجوی** کدهای ICD (طبقه‌بندی بین‌المللی بیماری‌ها).

**فناوری‌ها:** Python و Django (پردازش و قالب‌ها)، SQLite (ذخیره‌سازی)، Bootstrap 5 / HTML / CSS / JavaScript (ظاهر)، Django REST framework و Swagger (API).

## اجرا

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

سپس آدرس **http://127.0.0.1:8000/** را در مرورگر باز کنید. فایل `db.sqlite3` همراه پروژه است و داده‌ها از قبل در آن بارگذاری شده‌اند.

اگر پایگاه داده خالی بود: `python manage.py import_icd_data --path icd_codes.csv`

## امکانات

| بخش | توضیح |
|---|---|
| **فرم ورود اطلاعات** | دکمه **Add** در صفحه اصلی (یا `/icd/add/`). ۶ فیلد؛ سه فیلد Category code، Full code و Full description اجباری‌اند. ثبت کد تکراری رد می‌شود. پس از ثبت، پیام «ICD code ... was added.» نمایش داده می‌شود و رکورد جدید در نتایج دیده می‌شود |
| **جست‌وجو** | دو کادر در صفحه اصلی (عنوان دسته و کد دسته، بدون حساسیت به حروف، قسمتی از کلمه هم کافی است). نتایج در جدول با هایلایت، شمارش نتایج و صفحه‌بندی (۲۰ ردیف) نمایش داده می‌شوند. اگر چیزی پیدا نشود پیام «No Such Term Found!» دیده می‌شود |
| **حذف** | فقط برای staff، با صفحه تأیید |
| **API** | `/swagger/` و `/redoc/` |

## حساب مدیر (staff)

برای دیدن/ثبت فرم نیازی به حساب نیست. فقط **حذف رکورد** و پنل `/admin/` حساب لازم دارند:

```powershell
python manage.py createsuperuser
```

## تنظیمات

| متغیر محیطی | پیش‌فرض | توضیح |
|---|---|---|
| `ICD_PUBLIC_ADD` | `true` | `false` یعنی فرم افزودن هم فقط برای staff باشد |
| `DJANGO_DEBUG` | `true` | برای انتشار واقعی `false` شود |
| `DJANGO_SECRET_KEY` | کلید توسعه | با `DJANGO_DEBUG=false` الزامی است |

## تست

```powershell
python manage.py test
```

## ساختار

```
manage.py            icdproject/   تنظیمات پروژه
icdapp/models.py     مدل داده       icdapp/forms.py        فرم ثبت
icdapp/views.py      صفحه‌ها         icdapp/filters.py      فرم جست‌وجو
icdapp/api.py        API            icdapp/templates/      قالب‌ها (base, index, ...)
```

</div>

---

# English

A simple website for **adding** and **searching** ICD codes (course project, Internet Engineering).

**Stack:** Python / Django, SQLite, Bootstrap 5, Django REST framework + Swagger.

## Run

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000/**. `db.sqlite3` is included and already contains the data (otherwise: `python manage.py import_icd_data --path icd_codes.csv`).

## Features

- **Entry form:** the **Add** button (or `/icd/add/`). Six fields; category code, full code and full description are required; duplicate full codes are rejected; a success message is shown and the new record appears in the results.
- **Search:** category title and category code (case-insensitive, partial words), results in a table with highlighting, a result count, pagination that keeps the search, and a "No Such Term Found!" message when nothing matches.
- **Delete:** staff only, with a confirmation page.
- **API:** `/swagger/`, `/redoc/`.

No account is needed to add or search. Deleting and `/admin/` need one: `python manage.py createsuperuser`.
Set `ICD_PUBLIC_ADD=false` to make the add form staff-only too. Run the tests with `python manage.py test`.
