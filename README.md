# Student Data Pipeline - MongoDB Version

هذا الإصدار يحافظ على هيكل مشروع الـETL السابق، مع تغيير مكان الـLoad النهائي من ملفات CSV إلى MongoDB، وإضافة مصدرين جديدين مستقلين.

## 1. المصادر

### المصادر الأصلية

1. CSV: `data/raw/students.csv`
2. REST API المحلي: `http://127.0.0.1:8000/students`
3. SQLite: `database/students.db`

المصادر الثلاثة الأصلية تستمر في العمل بالطريقة السابقة: Extract → Clean → Validate → Integrate → Transform → Final Validate.

### المصدر الجديد الأول: Web Scraping

الرابط:
`https://www.scrapethissite.com/pages/simple/`

يتم استخراج **ثلاثة أعمدة فقط**:

- `country`
- `capital`
- `population`

الموقع يعرض بيانات الدول، ومنه يتم استخراج هذه الحقول فقط. citeturn0view0

### المصدر الجديد الثاني: MongoDB

المصدر هو قاعدة البيانات الموجودة مسبقًا:

- Database: `sales`
- Collection: `orders`

الاتصال:
`mongodb://localhost:27017/`

يتم جلب السجلات من `sales.orders` بدون `_id` ثم تنظيفها والتحقق منها.

## 2. قاعدة بيانات الإخراج

يقوم Python بإنشاء/تجهيز قاعدة بيانات MongoDB باسم:

`student_data`

وتكون Collections الرئيسية:

```text
student_data
├── students_final
├── students_rejected
├── countries_processed
└── orders_processed
```

### students_final
النتيجة النهائية للمصادر الأصلية الثلاثة بعد الدمج والمعالجة.

### students_rejected
السجلات التي فشلت في قواعد الجودة للمصادر الأصلية.

### countries_processed
البيانات الصحيحة الناتجة من Web Scraping بعد المعالجة.

### orders_processed
البيانات الصحيحة الناتجة من `sales.orders` بعد المعالجة.

**المصدران الجديدان لا يتم دمجهما مع بعضهما ولا مع بيانات الطلاب.** كل مصدر له Pipeline مستقل وCollection مستقلة.

## 3. معالجة Web Scraping

المراحل:

```text
Web Page
   ↓
Extract country/capital/population
   ↓
Clean
   ↓
Validate
   ↓
Transform
   ↓
countries_processed
```

قواعد الجودة:

- `country` مطلوب.
- `population` يجب أن يكون رقمًا.
- `population` لا يمكن أن يكون سالبًا.
- التكرار حسب `country` يتم التخلص منه.

## 4. معالجة MongoDB Orders

المراحل:

```text
sales.orders
   ↓
Extract
   ↓
Clean
   ↓
Validate
   ↓
Transform
   ↓
orders_processed
```

المعالجة تشمل:

- إزالة المسافات الزائدة.
- توحيد `payment_method`.
- توحيد `status` إلى أحرف كبيرة.
- تحويل `total_amount` إلى رقم.
- تحويل `created_at` إلى Timestamp للتحقق منه.
- إزالة تكرار `order_id`.

قواعد الجودة:

- `order_id` مطلوب.
- `customer_id` مطلوب.
- `total_amount` يجب أن يكون رقمًا وغير سالب.
- `created_at` يجب أن يكون Timestamp صحيحًا.

مثال السجل الذي أعطي في التكليف:

```text
order_id = ORD-1007
customer_id = CUST-507
total_amount = -15
payment_method = Cash
status = PENDING
created_at = invalid_timestamp
```

سيتم رفضه لأن `total_amount` سالب و`created_at` غير صالح.

## 5. تثبيت المتطلبات

من داخل مجلد المشروع:

```bash
pip install -r requirements.txt
```

## 6. تجهيز MongoDB

يجب أن يكون MongoDB Server يعمل على:

```text
mongodb://localhost:27017/
```

ثم نفذ:

```bash
python database/create_mongodb.py
```

هذا ينشئ قاعدة البيانات `student_data` ويجهز Collections الإخراج.

> في MongoDB يتم إنشاء قاعدة البيانات فعليًا عند وجود بيانات/Collection، لذلك السكربت ينشئ الـCollections المطلوبة لتجهيز قاعدة البيانات.

## 7. تشغيل المصدرين الجديدين فقط

إذا كان المطلوب اختبار المصدرين الجديدين دون تشغيل الـAPI القديم، استخدم:

```bash
python run_new_sources.py
```

سيقوم البرنامج فعليًا بالاتصال بالموقع، جلب البيانات، معالجتها، ثم تخزينها في:

```text
student_data.countries_processed
```

ثم يتصل بـ:

```text
sales.orders
```

ويعالجها ويخزن السجلات الصحيحة في:

```text
student_data.orders_processed
```

ولا توجد أي عملية دمج بين المصدرين.

## 8. تشغيل المشروع الكامل

### أولًا: تشغيل الـAPI المحلي

في Terminal:

```bash
python mock_api.py
```

### ثانيًا: تشغيل الـPipeline

في Terminal أخرى:

```bash
python main.py
```

## 9. الاختبارات

```bash
python -m unittest discover -s tests -p "test_*.py"
```

الاختبارات تغطي CSV وAPI والدمج القديم، بالإضافة إلى استخراج Web Scraping الفعلي (باختبار اتصال Mock) ومعالجة Web Scraping وMongoDB Orders.

## 10. الهيكل

```text
student_data_pipeline/
│
├── app/
│   ├── sources/
│   │   ├── csv_source.py
│   │   ├── api_source.py
│   │   ├── database_source.py
│   │   ├── web_scraping_source.py
│   │   └── mongo_source.py
│   │
│   ├── transformation/
│   │   ├── cleaner.py
│   │   ├── integration.py
│   │   ├── transformer.py
│   │   ├── new_cleaner.py
│   │   └── new_transformer.py
│   │
│   ├── validation/
│   │   ├── quality.py
│   │   └── new_quality.py
│   │
│   ├── output/
│   │   └── mongo_writer.py
│   │
│   └── utils/
│       └── logger.py
│
├── database/
│   ├── create_database.py
│   ├── create_mongodb.py
│   └── students.db
│
├── data/raw/students.csv
├── tests/test_pipeline.py
├── main.py
├── run_new_sources.py
├── mock_api.py
├── requirements.txt
└── README.md
```

## 11. النتيجة

بدلًا من:

```text
data/processed/final_dataset.csv
```

أصبحت النتيجة النهائية في MongoDB:

```text
student_data.students_final
```

وبالنسبة للمصادر الجديدة:

```text
student_data.countries_processed
student_data.orders_processed
```

ولا توجد عملية دمج بين المصدرين الجديدين.
