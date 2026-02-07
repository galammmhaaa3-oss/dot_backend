# DOT Backend - Render Deployment Guide

## الطريقة اليدوية (Manual Deployment)

### الخطوة 1: إنشاء قاعدة البيانات PostgreSQL

1. اذهب إلى https://dashboard.render.com
2. اضغط **New** → **PostgreSQL**
3. املأ البيانات:
   - **Name**: `dot-db`
   - **Database**: `dot_database`
   - **User**: `dot_user`
   - **Region**: اختر الأقرب لك
   - **Plan**: **Free**
4. اضغط **Create Database**
5. انتظر حتى يصبح الـ Status: **Available**
6. **احفظ** الـ **Internal Database URL** (ستحتاجه لاحقًا)

---

### الخطوة 2: إنشاء Web Service

1. في Render Dashboard، اضغط **New** → **Web Service**
2. اختر **Build and deploy from a Git repository**
3. اضغط **Connect** بجانب GitHub repository الخاص بك
   - إذا لم يكن موجود، اضغط **Configure account** وأضف الـ repo
4. اختر الـ repository الذي يحتوي على `dot_backend`

---

### الخطوة 3: إعدادات Web Service

املأ البيانات التالية:

**Basic Settings:**
- **Name**: `dot-api`
- **Region**: نفس المنطقة التي اخترتها للـ database
- **Branch**: `main` (أو `master`)
- **Root Directory**: `dot_backend` (إذا كان المشروع في مجلد فرعي)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- اختر **Free**

---

### الخطوة 4: Environment Variables

اضغط **Advanced** ثم أضف المتغيرات التالية:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | الصق الـ **Internal Database URL** من الخطوة 1 |
| `SECRET_KEY` | `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
| `CORS_ORIGINS` | `*` |
| `DEBUG` | `False` |

**ملاحظة:** يمكنك توليد `SECRET_KEY` جديد باستخدام:
```python
import secrets
print(secrets.token_hex(32))
```

---

### الخطوة 5: Deploy

1. اضغط **Create Web Service**
2. انتظر حتى ينتهي الـ deployment (قد يستغرق 5-10 دقائق)
3. عند الانتهاء، ستحصل على URL مثل:
   ```
   https://dot-api.onrender.com
   ```

---

### الخطوة 6: اختبار الـ API

افتح المتصفح واذهب إلى:
```
https://dot-api.onrender.com/docs
```

يجب أن ترى صفحة Swagger UI مع جميع الـ endpoints!

---

## اختبار سريع

### 1. Health Check
```
GET https://dot-api.onrender.com/health
```
يجب أن ترى:
```json
{"status": "healthy", "service": "DOT API"}
```

### 2. تسجيل مستخدم جديد
في Swagger UI:
1. افتح `POST /api/v1/auth/register`
2. اضغط **Try it out**
3. أدخل:
```json
{
  "phone": "0912345678",
  "name": "Test User",
  "password": "password123"
}
```
4. اضغط **Execute**

### 3. تسجيل الدخول
1. افتح `POST /api/v1/auth/login`
2. أدخل نفس البيانات
3. احفظ الـ `access_token`

### 4. إنشاء طلب توصيل
1. افتح `POST /api/v1/deliveries`
2. اضغط **Authorize** (أعلى الصفحة)
3. الصق الـ token
4. جرب إنشاء طلب!

---

## ربط مع Flutter App

في Flutter app، حدّث الـ API URL:

```dart
class ApiConfig {
  static const String baseUrl = "https://dot-api.onrender.com/api/v1";
}
```

---

## ملاحظات مهمة

⚠️ **Free Tier Limitations:**
- الـ service ينام بعد 15 دقيقة من عدم الاستخدام
- أول request بعد النوم قد يستغرق 30 ثانية (cold start)
- PostgreSQL مجاني لـ 90 يوم فقط

💡 **نصائح:**
- استخدم الـ Health Check endpoint للحفاظ على الـ service نشط
- يمكنك استخدام cron job لإرسال request كل 10 دقائق

---

## استكشاف الأخطاء

### إذا فشل الـ Build:
1. تحقق من `requirements.txt`
2. تأكد من وجود `app/main.py`
3. راجع الـ Logs في Render Dashboard

### إذا فشل الـ Start:
1. تحقق من `DATABASE_URL`
2. تأكد من أن الـ database متاح
3. راجع الـ Environment Variables

### إذا كان الـ API بطيء:
- هذا طبيعي للـ Free Tier
- أول request بعد النوم يستغرق وقت
- استخدم Health Check للحفاظ على النشاط

---

## الخطوات التالية

✅ Backend deployed على Render
📱 حدّث Flutter app بالـ API URL
🧪 اختبر جميع الـ features
🚀 Launch!
