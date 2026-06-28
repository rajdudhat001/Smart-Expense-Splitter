# Smart Expense Splitter - Complete Project Explanation & Guide

---

# PHASE 1: Project Setup and Architecture (फेज 1: प्रोजेक्ट सेटअप और आर्किटेक्चर)

## 1. Core Concepts (मूल सिद्धांत)

### What is a Virtual Environment? (वर्चुअल एनवायरनमेंट क्या है?)
* **English**: A virtual environment (`venv`) is an isolated environment that allows you to install Python packages for a specific project without affecting other projects or the global system settings.
* **Hindi**: वर्चुअल एनवायरनमेंट (`venv`) एक अलग (isolated) वातावरण है जो आपको सिस्टम के अन्य प्रोजेक्ट्स को प्रभावित किए बिना किसी विशिष्ट प्रोजेक्ट के लिए पायथन लाइब्रेरीज़ को इंस्टॉल करने की अनुमति देता है।

### What is Django and Django REST Framework? (जैंगो और जैंगो रेस्ट फ्रेमवर्क क्या है?)
* **English**: Django is a high-level Python web framework that encourages rapid development. Django REST Framework (DRF) is a powerful toolkit built on top of Django to build Web APIs.
* **Hindi**: Django एक उच्च-स्तरीय पायथन वेब फ्रेमवर्क है जो तेज़ी से वेब विकास करने में मदद करता है। Django REST Framework (DRF) एक टूलकिट है जिसका उपयोग Django के ऊपर Web APIs (वेब एपीआई) बनाने के लिए किया जाता है।

---

## 2. Steps Performed & Commands (किए गए स्टेप्स और कमांड्स)

1. **Renamed the folders**:
   * Renamed the project settings folder from `backend` to `config` to avoid confusion with the root directory.
   * Renamed the default app from `expense` to `expenses` (plural name for REST convention).
   * **Hindi**: सेटिंग्स फोल्डर का नाम `backend` से बदलकर `config` किया और ऐप का नाम `expense` से बदलकर `expenses` किया।

2. **Created `requirements.txt`**:
   * Defined Django, DRF, and CORS headers.
   * **Hindi**: `requirements.txt` फाइल बनाई और आवश्यक लाइब्रेरीज़ को लिखा।

3. **Installed Dependencies (डिपेंडेंसीज इंस्टॉल की)**:
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. **Updated Settings Imports (इंपोर्ट्स अपडेट किए)**:
   * Updated `manage.py`, `config/wsgi.py`, and `config/asgi.py` to point to `config.settings` instead of `backend.settings`.
   * **Hindi**: `manage.py`, `wsgi.py`, और `asgi.py` में `backend.settings` की जगह `config.settings` पाथ अपडेट किया।

---

## 3. Directory & File Explanations (डायरेक्टरी और फ़ाइल विवरण)

* **`manage.py`**:
  * **English**: The command-line utility that lets you interact with Django (run server, create migrations, run tests).
  * **Hindi**: यह एक कमांड-लाइन टूल है जिससे हम Django प्रोजेक्ट को चलाते हैं (जैसे सर्वर रन करना, डेटाबेस माइग्रेट करना)।
* **`config/settings.py`**:
  * **English**: Contains all configurations of the Django project including installed apps, middleware, database configuration, and CORS settings.
  * **Hindi**: इसमें पूरे प्रोजेक्ट की सेटिंग्स होती हैं जैसे कौन-से ऐप्स इंस्टॉल हैं, डेटाबेस कौन-सा है, और अन्य सेटिंग्स।
* **`config/urls.py`**:
  * **English**: The main routing file that maps URLs to views. It forwards API paths to `expenses/urls.py`.
  * **Hindi**: यह मुख्य राउटिंग फाइल है जो यूआरएल (URL) को सही व्यूज़ (Views) से जोड़ती है।

---

## 4. Best Practices & Common Mistakes (बेस्ट प्रैक्टिसेज और आम गलतियां)

* **Best Practice**: Always use a virtual environment so package versions do not conflict.
* **Best Practice (Hindi)**: हमेशा वर्चुअल एनवायरनमेंट का उपयोग करें ताकि पैकेज वर्शन्स में कोई टकराव न हो।
* **Common Mistake**: Forgetting to update `manage.py` or `wsgi.py` after renaming the settings directory, which throws a `ModuleNotFoundError`.
* **Common Mistake (Hindi)**: सेटिंग्स फोल्डर का नाम बदलने के बाद `manage.py` या `wsgi.py` में पुराना नाम छोड़ देना, जिससे एरर आता है।

---

## 5. Viva / Interview Questions (वाइवा / इंटरव्यू के प्रश्न)

1. **Question**: Why do we use `requirements.txt` in Python projects?
   * **Answer**: It lists all the packages and their versions needed to run the project so anyone can install them with a single pip command.
   * **Hindi Answer**: यह उन सभी पैकेजों की सूची है जो प्रोजेक्ट चलाने के लिए चाहिए, ताकि कोई भी इसे आसानी से एक कमांड से इंस्टॉल कर सके।
2. **Question**: What is CORS and why did we install `django-cors-headers`?
   * **Answer**: CORS stands for Cross-Origin Resource Sharing. We need it so our React frontend (running on a different port/origin) can communicate with our Django API.
   * **Hindi Answer**: CORS का मतलब क्रॉस-ओरिजिन रिसोर्स शेयरिंग है। इसकी जरूरत इसलिए है ताकि हमारा रिएक्ट फ्रंटएंड हमारे जैंगो एपीआई से बिना किसी सुरक्षा रुकावट के बात कर सके।

---
---

# PHASE 2: Database Model Design & Implementation (फेज 2: डेटाबेस मॉडल डिज़ाइन और इम्प्लीमेंटेशन)

## 1. Core Concepts (मूल सिद्धांत)

### What is Django ORM? (जैंगो ओआरएम क्या है?)
* **English**: ORM stands for Object-Relational Mapping. It allows us to interact with our SQLite database using Python classes and objects instead of writing raw SQL queries.
* **Hindi**: ORM का मतलब ऑब्जेक्ट-रिलेशनल मैपिंग है। यह हमें SQL क्वेरीज़ लिखे बिना पायथन क्लासेस और ऑब्जेक्ट्स का उपयोग करके डेटाबेस से बातचीत करने की अनुमति देता है।

### What are Migrations? (माइग्रेशन क्या हैं?)
* **English**: Migrations are Django’s way of propagating changes you make to your models (adding a field, deleting a model, etc.) into your database schema.
* **Hindi**: माइग्रेशन वह तरीका है जिससे Django आपके मॉडल्स (जैसे नया फील्ड जोड़ना या टेबल बनाना) में किए गए बदलावों को डेटाबेस में लागू करता है।

---

## 2. Steps Performed & Commands (किए गए स्टेप्स और कमांड्स)

1. **Write Models (मॉडल्स लिखे)**: Created database structure in `expenses/models.py`.
2. **Create Migration Files (माइग्रेशन फाइल्स बनाई)**:
   ```powershell
   .\venv\Scripts\python.exe manage.py makemigrations
   ```
3. **Apply Migrations (डेटाबेस में लागू किया)**:
   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   ```
4. **Run Unit Tests (यूनिट टेस्ट चलाए)**:
   ```powershell
   .\venv\Scripts\python.exe manage.py test
   ```

---

## 3. Code & Models Explanation (कोड और मॉडल्स विवरण)

### `Group` Model (ग्रुप मॉडल)
* **English**: Represents a group of users who share expenses. Uses `ManyToManyField(User)` to link multiple users to one group.
* **Hindi**: यह उन यूज़र्स के ग्रुप को दर्शाता है जो खर्चों को आपस में बांटते हैं।

### `Expense` Model (एक्सपेंस मॉडल)
* **English**: Represents a single bill paid by a user. Links to `Group` using `ForeignKey` (one group can have multiple expenses).
* **Hindi**: यह किसी यूज़र द्वारा किए गए भुगतान (जैसे बिजली बिल या डिनर बिल) को दर्शाता है।

### `ExpenseSplit` Model (एक्सपेंस स्प्लिट मॉडल)
* **English**: Specifies how much an individual user owes for a particular expense. Uses `unique_together = ('expense', 'user')` to prevent duplicate split entries.
* **Hindi**: यह दर्शाता है कि किसी विशिष्ट खर्चे के लिए किस यूज़र को कितने पैसे चुकाने हैं।

### `Settlement` Model (सेटलमेंट मॉडल)
* **English**: Records payments sent between users to settle balances (e.g. Bob paying Alice back).
* **Hindi**: यह यूज़र्स के बीच हुए पैसों के लेन-देन को रिकॉर्ड करता है जिससे उनके बीच का बकाया चुकता (settled) हो सके।

---

## 4. Best Practices & Common Mistakes (बेस्ट प्रैक्टिसेज और आम गलतियां)

* **Best Practice**: Use `DecimalField` instead of `FloatField` for currency and money calculations to avoid floating-point precision errors.
* **Best Practice (Hindi)**: पैसों या करेंसी के कैलकुलेशन के लिए हमेशा `DecimalField` का उपयोग करें, न कि `FloatField`, ताकि गणितीय शुद्धता बनी रहे।
* **Common Mistake**: Not specifying `on_delete=models.CASCADE` or `models.SET_NULL` for foreign keys, which causes model configuration errors.
* **Common Mistake (Hindi)**: फॉरेन की (Foreign Key) में `on_delete` बिहेवियर सेट न करना, जिससे माइग्रेशन एरर आ सकता है।

---

## 5. Viva / Interview Questions (वाइवा / इंटरव्यू के प्रश्न)

1. **Question**: What is the difference between `makemigrations` and `migrate`?
   * **Answer**: `makemigrations` generates Python code that describes database changes based on your models. `migrate` executes that code against the database to create or modify tables.
   * **Hindi Answer**: `makemigrations` मॉडल्स के बदलावों के आधार पर माइग्रेशन फाइल (Python कोड) बनाता है। `migrate` उस फाइल को रन करके डेटाबेस में टेबल बनाता या बदलता है।
2. **Question**: Why is `unique_together` useful in `ExpenseSplit`?
   * **Answer**: It ensures that a user cannot have two separate shares assigned to them for the same single expense, preserving database integrity.
   * **Hindi Answer**: यह यह सुनिश्चित करता है कि एक ही खर्चे के लिए किसी यूज़र के नाम पर दो बार अलग-अलग हिस्सेदारी (split) न दर्ज की जा सके।

---
---

# PHASE 2 (Continued): Detailed Database Design for Complete Features (फेज 2: पूर्ण फीचर्स के लिए विस्तृत डेटाबेस डिज़ाइन)

In this section, we design the full relational database schema required to support all project features. We explain the fields, relationships, dynamic calculations, and the new **Budget** model.

---

## 1. Core Features & Model Mappings (मुख्य फीचर्स और उनका मॉडल मैपिंग)

### A. User Login/Signup (यूज़र लॉगिन/साइनअप)
* **Model**: Built-in Django `User` model (`django.contrib.auth.models.User`).
* **Fields**: `id`, `username`, `email`, `password`, `first_name`, `last_name`.
* **Why it's needed**: Provides standard user authentication, session management, and password hashing out of the box.
* **Hindi Explanation**: यह Django का इन-बिल्ट (पहले से बना हुआ) मॉडल है जो यूज़र रजिस्ट्रेशन, लॉगिन, सुरक्षा और पासवर्ड हैशिंग की सुविधा देता है।

### B. Create Group & Add Members (ग्रुप बनाना और मेंबर्स जोड़ना)
* **Model**: `Group`
* **Fields**:
  * `id` (Primary Key)
  * `name` (CharField)
  * `description` (TextField)
  * `created_by` (ForeignKey -> User) — 1-to-Many relationship (one user can create many groups).
  * `members` (ManyToManyField -> User) — Many-to-Many relationship (a user can be in many groups, and a group can have many users).
  * `created_at` (DateTimeField)
* **Why it's needed**: Expense splitting is done within a group. This model groups users and links their memberships.
* **Hindi Explanation**: खर्चे बांटने के लिए ग्रुप बनाना जरूरी है। यह मॉडल यूज़र्स को एक ग्रुप में जोड़ने का काम करता है।

### C. Add Expense (खर्चा जोड़ना)
* **Model**: `Expense`
* **Fields**:
  * `id` (Primary Key)
  * `group` (ForeignKey -> Group) — Links the expense to a specific group.
  * `description` (CharField) — What the expense was for (e.g. "Tea & Snacks").
  * `amount` (DecimalField) — Total bill amount.
  * `paid_by` (ForeignKey -> User) — Who paid the bill.
  * `date` (DateField) — Date of transaction.
* **Why it's needed**: Stores the metadata of a transaction and records who made the primary payment.
* **Hindi Explanation**: यह किसी भी लेन-देन (transaction) की मुख्य जानकारी को स्टोर करता है, जैसे कि बिल किसने भरा और कुल कितना पैसा खर्च हुआ।

### D. Equal & Unequal Splits (बराबर और असमान रूप से पैसे बांटना)
* **Model**: `ExpenseSplit`
* **Fields**:
  * `id` (Primary Key)
  * `expense` (ForeignKey -> Expense) — Links to the main expense record.
  * `user` (ForeignKey -> User) — The member who owes money.
  * `amount` (DecimalField) — The specific share/portion they owe.
  * `is_settled` (BooleanField) — Tracks if this debt is cleared.
* **Why it's needed**:
  * **Equal Split (बराबर बांटना)**: If total is $90 and 3 members share, the backend dynamically calculates $30 for each and inserts 3 records into `ExpenseSplit`.
  * **Unequal Split (अलग-अलग बांटना)**: Allows custom shares (e.g., Alice owes $50, Bob owes $40). The backend validates that the sum of splits equals the total expense amount.
* **Hindi Explanation**: यह मॉडल प्रत्येक यूज़र के हिस्से का कर्ज रिकॉर्ड करता है। अगर बराबर बांटना है तो सिस्टम कुल राशि को मेंबर्स की संख्या से भाग (divide) करके समान रिकॉर्ड बनाता है। असमान रूप से बांटने पर कस्टम राशि की जांच करता है।

### E. Settlements (चुकता करना)
* **Model**: `Settlement`
* **Fields**:
  * `id` (Primary Key)
  * `group` (ForeignKey -> Group)
  * `payer` (ForeignKey -> User) — Who is sending the money to clear debt.
  * `payee` (ForeignKey -> User) — Who is receiving the payment.
  * `amount` (DecimalField) — Settlement amount.
  * `date` (DateTimeField)
  * `status` (CharField: pending/completed)
* **Why it's needed**: Tracks actual money transfers made to clear balances.
* **Hindi Explanation**: जब कोई यूज़र किसी दूसरे यूज़र को पैसे वापस चुकाता है, तो उस ट्रांजैक्शन को रिकॉर्ड करने के लिए इस मॉडल का उपयोग होता है।

### F. Budget Alert (बजट चेतावनी)
* **Model**: `Budget`
* **Fields**:
  * `id` (Primary Key)
  * `group` (ForeignKey -> Group, null=True, blank=True) — Optional, for group-specific budgets.
  * `user` (ForeignKey -> User, null=True, blank=True) — Optional, for personal user budgets.
  * `amount_limit` (DecimalField) — Maximum limit set (e.g., $500 monthly).
  * `created_at` (DateTimeField)
* **Why it's needed**: Allows users to set a budget threshold. If the total expenses in a group or for a user exceed this limit, the system alerts them.
* **Hindi Explanation**: यह मॉडल यूज़र को बजट लिमिट सेट करने की अनुमति देता है। यदि खर्च इस लिमिट से ज़्यादा होता है, तो सिस्टम चेतावनी (alert) दिखाता है।

---

## 2. Dynamic Calculations (डायनेमिक कैलकुलेशन)

### A. How View Balance works (बैलेंस देखना कैसे काम करता है)
We do **not** store balances directly in the database. Storing balances can lead to data inconsistency (e.g., if an expense is deleted but the balance field isn't updated). Instead, we calculate the balance dynamically using Django ORM aggregation:

$$ \text{Balance of User } U \text{ in Group } G = (\text{Total paid by } U) - (\text{Total owed by } U) + (\text{Total received in settlements}) - (\text{Total paid in settlements}) $$

* **Positive Balance**: User gets money back (लोग उसे पैसे देंगे).
* **Negative Balance**: User owes money to others (उसे दूसरों को पैसे देने हैं).

### B. Smart Settlement Logic (स्मार्ट सेटलमेंट लॉजिक)
Smart Settlement minimizes the number of transactions required to settle the group debt.
* **Example**:
  * Alice owes Bob $10.
  * Bob owes Charlie $10.
  * **Smart Settlement** bypasses Bob and suggests: Alice pays Charlie $10 directly (1 transaction instead of 2).
  * This is computed using a greedy algorithm at the API level (not in the database).

---

## 3. Best Practices & Common Mistakes (बेस्ट प्रैक्टिसेज और आम गलतियां)

* **Best Practice**: Never store redundant calculated values (like total user balance) in the database. Calculate them on the fly.
* **Best Practice (Hindi)**: कभी भी कुल बैलेंस जैसे कैलकुलेटेड वैल्यूज़ को डेटाबेस में परमानेंट स्टोर न करें। इन्हें हमेशा क्वेरी टाइम पर ही कैलकुलेट करें।
* **Common Mistake**: Allowing an expense total to not match the sum of its splits.
* **Common Mistake (Hindi)**: खर्चे की कुल राशि (Total Expense) और स्प्लिट राशियों के योग (Sum of Splits) में अंतर होने देना। कोडिंग के समय इसे वैलिडेट करना अनिवार्य है।

---

## 4. Viva / Interview Questions (वाइवा / इंटरव्यू के प्रश्न)

1. **Question**: Why do we use `DecimalField` instead of `FloatField` for storing amounts?
   * **Answer**: `FloatField` uses binary floating-point representation which causes precision loss during calculations. `DecimalField` stores exact decimal values, which is critical for financial transactions.
   * **Hindi Answer**: `FloatField` में फ्लोटिंग-पॉइंट की वजह से गणितीय गणनाओं में पैसे कम-ज्यादा (precision errors) हो सकते हैं। `DecimalField` पैसों का बिल्कुल सटीक मान स्टोर करता है।
2. **Question**: Explain Django's Many-to-Many relationship using the `Group` and `User` models.
   * **Answer**: A user can join multiple groups, and a group can contain multiple users. Django handles this by creating an intermediate join table automatically.
   * **Hindi Answer**: एक यूज़र कई ग्रुप्स का मेंबर हो सकता है और एक ग्रुप में कई यूज़र्स हो सकते हैं। Django इसके लिए बैकएंड में एक तीसरी 'जॉइन टेबल' (join table) बनाता है।
3. **Question**: Why is it better to calculate balances dynamically instead of storing them?
   * **Answer**: It ensures data integrity. If an expense is updated, added, or deleted, the balances are automatically correct without running complex database sync operations.
   * **Hindi Answer**: इससे डेटा की शुद्धता बनी रहती है। अगर कोई भी खर्चा हटाया या बदला जाता है, तो बैलेंस बिना किसी सिंक (sync) प्रक्रिया के तुरंत सही दिखाई देता है।

---
---

# PHASE 3: Django Models + ORM + Migrations (फेज 3: जैंगो मॉडल्स + ओआरएम + माइग्रेशन्स)

In this phase, we implemented the actual Django model classes inside `expenses/models.py`, generated structural migrations, migrated the SQLite database, and verified our schema using Python unit tests.

---

## 1. Django Models & Fields Explanation (जैंगो मॉडल्स और फील्ड्स का स्पष्टीकरण)

### A. Group Model (ग्रुप मॉडल)
Defines a team/group where members share expenses.
* **Fields**:
  * `name`: `CharField(max_length=100)`
    * **English**: Stores the name of the group. CharField requires a maximum length limit.
    * **Hindi**: ग्रुप का नाम स्टोर करने के लिए। इसके लिए अधिकतम लंबाई (max_length) तय करना जरूरी है।
  * `description`: `TextField(blank=True)`
    * **English**: Stores optional long description. `blank=True` means the description can be empty in forms.
    * **Hindi**: ग्रुप के बारे में विस्तार से लिखने के लिए। `blank=True` का मतलब है कि इसे खाली छोड़ा जा सकता है।
  * `created_by`: `ForeignKey(User, on_delete=models.SET_NULL, null=True)`
    * **English**: The user who created the group. `on_delete=models.SET_NULL` ensures that if the creator's account is deleted, the group itself is not deleted, but its creator field becomes null.
    * **Hindi**: ग्रुप बनाने वाला यूज़र। यदि बनाने वाले का अकाउंट डिलीट हो जाता है, तो ग्रुप डिलीट नहीं होगा, बस निर्माता का फील्ड खाली (null) हो जाएगा।
  * `members`: `ManyToManyField(User, related_name='expense_groups')`
    * **English**: Connects multiple users to a group. Django automatically creates an intermediate table to link users and groups.
    * **Hindi**: यह कई यूज़र्स को ग्रुप से जोड़ता है। Django बैकएंड में खुद एक तीसरी टेबल बनाकर इनके संबंधों को संभालता है।

### B. Expense Model (खर्चा मॉडल)
Defines a payment made for a group.
* **Fields**:
  * `group`: `ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')`
    * **English**: Group where the expense happened. `on_delete=models.CASCADE` means if the group is deleted, all its expenses are also deleted.
    * **Hindi**: वह ग्रुप जिसमें खर्चा हुआ। यदि ग्रुप डिलीट होता है, तो उसके सारे खर्चे भी डिलीट हो जाएंगे।
  * `description`: `CharField(max_length=255)`
    * **English**: A short text detailing what the bill was for.
    * **Hindi**: खर्चे का संक्षिप्त विवरण (जैसे: "डिनर का बिल")।
  * `amount`: `DecimalField(max_digits=10, decimal_places=2)`
    * **English**: Total money spent. Ensures absolute precision with 2 decimal points.
    * **Hindi**: कुल खर्च की गई राशि। दशमलव के बाद 2 अंकों तक की शुद्धता बनाए रखता है।
  * `paid_by`: `ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')`
    * **English**: The user who paid the total bill amount.
    * **Hindi**: वह यूज़र जिसने पूरा बिल भरा।
  * `date`: `DateField()`
    * **English**: Stores the day the expense occurred.
    * **Hindi**: खर्चा किस दिन हुआ, वह तारीख स्टोर करता है।

### C. ExpenseSplit Model (खर्चा हिस्सा मॉडल)
Defines how much each individual user owes for a specific expense.
* **Fields**:
  * `expense`: `ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')`
    * **English**: Parent transaction to which this split belongs.
    * **Hindi**: वह मुख्य खर्चा जिससे यह स्प्लिट (हिस्सा) जुड़ा हुआ है।
  * `user`: `ForeignKey(User, on_delete=models.CASCADE, related_name='splits_owed')`
    * **English**: The user who owes money for this split.
    * **Hindi**: वह यूज़र जिसके हिस्से में यह कर्ज आया है।
  * `amount`: `DecimalField(max_digits=10, decimal_places=2)`
    * **English**: Specific amount of money this user owes.
    * **Hindi**: वह राशि जो इस यूज़र को चुकानी है।
  * `is_settled`: `BooleanField(default=False)`
    * **English**: Boolean flag representing if the user has paid back their split share.
    * **Hindi**: यह दर्शाता है कि क्या यूज़र ने अपना यह हिस्सा चुका दिया है या नहीं।

### D. Settlement Model (सेटलमेंट मॉडल)
Tracks debt-clearance payments directly between users in a group.
* **Fields**:
  * `payer`: `ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_sent')`
    * **English**: User who is sending the money to clear debt.
    * **Hindi**: वह यूज़र जो कर्ज चुकाने के लिए पैसे भेज रहा है।
  * `payee`: `ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_received')`
    * **English**: User who is receiving the money.
    * **Hindi**: वह यूज़र जिसे पैसे मिल रहे हैं।
  * `amount`: `DecimalField(max_digits=10, decimal_places=2)`
    * **English**: Cash amount settled.
    * **Hindi**: चुकता की गई कुल राशि।

### E. Budget Model (बजट मॉडल)
Sets spending thresholds to trigger alert flags.
* **Fields**:
  * `group`: `ForeignKey(Group, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)`
    * **English**: Link to a specific group for group budget limits. Optional field.
    * **Hindi**: ग्रुप का बजट सेट करने के लिए। यह वैकल्पिक (optional) है।
  * `user`: `ForeignKey(User, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)`
    * **English**: Link to a user for individual monthly spending limit. Optional field.
    * **Hindi**: यूज़र का निजी बजट लिमिट सेट करने के लिए। यह भी वैकल्पिक है।
  * `amount_limit`: `DecimalField(max_digits=10, decimal_places=2)`
    * **English**: The maximum allowed monthly spending threshold.
    * **Hindi**: खर्च करने की अधिकतम सीमा।

---

## 2. Django Migration Commands (माइग्रेशन कमांड्स)

In Django, database tables are not modified directly. We write Python models, and Django handles database mapping via these two commands:

1. **`python manage.py makemigrations`**
   * **English**: Django inspects your modified models files and compiles Python scripts describing database schema changes (e.g., adding columns/tables). These files are saved in the `migrations/` folder.
   * **Hindi**: Django आपके मॉडल्स फ़ाइलों को देखता है और डेटाबेस स्कीमा में होने वाले बदलावों (जैसे नया टेबल या कॉलम) की एक स्क्रिप्ट फाइल बनाता है, जिसे `migrations/` फोल्डर में सेव किया जाता है।
2. **`python manage.py migrate`**
   * **English**: Reads the pending migration scripts and runs equivalent SQL statements against the SQLite database file to apply changes permanently.
   * **Hindi**: यह कमांड बनी हुई माइग्रेशन फाइलों को पढ़कर डेटाबेस पर SQL स्टेटमेंट्स चलाता है और डेटाबेस में बदलावों को स्थाई रूप से लागू करता है।

---

## 3. Best Practices & Common Mistakes (बेस्ट प्रैक्टिसेज और आम गलतियां)

* **Best Practice**: Always add index/related name lookups. Standardize using `related_name` in all Foreign Keys so you can easily reference reverse lookups (e.g., `group.expenses.all()` instead of `group.expense_set.all()`).
* **Best Practice (Hindi)**: सभी Foreign Keys में `related_name` का उपयोग करें ताकि विपरीत दिशा से आसानी से क्वेरी की जा सके (जैसे `group.expenses.all()`)।
* **Common Mistake**: Forgetting to generate migrations (`makemigrations`) after making edits in `models.py`. Running the server without applying migrations results in `OperationalError: no such table`.
* **Common Mistake (Hindi)**: मॉडल्स फ़ाइल बदलने के बाद माइग्रेशन रन करना भूल जाना। इससे सर्वर चलाते समय `no such table` एरर आता है।

---

## 4. Viva / Interview Questions (वाइवा / इंटरव्यू के प्रश्न)

1. **Question**: What is the purpose of `related_name` in a Django ForeignKey?
   * **Answer**: It defines the name of the reverse relation from the related model back to this model. If not defined, Django defaults to `<model_name>_set`.
   * **Hindi Answer**: यह विपरीत मॉडल से वर्तमान मॉडल को एक्सेस करने का नाम तय करता है। यदि आप इसे सेट नहीं करते हैं, तो Django डिफ़ॉल्ट रूप से `<model_name>_set` का उपयोग करता है।
2. **Question**: What happens to dependent rows when `on_delete=models.CASCADE` is triggered?
   * **Answer**: If the referenced row (parent) is deleted, all dependent rows (children) containing that foreign key are automatically deleted.
   * **Hindi Answer**: यदि पैरेंट रो (parent row) को हटाया जाता है, तो उससे जुड़े सभी चाइल्ड रिकॉर्ड्स (जैसे खर्चे) भी अपने आप डिलीट हो जाते हैं।
3. **Question**: Why did we use `null=True, blank=True` for `group` and `user` fields in the `Budget` model?
   * **Answer**: To support polymorphic configuration: a budget can either belong to a group or to a user. Making both optional allows one to be set while leaving the other null.
   * **Hindi Answer**: ताकि बजट या तो सिर्फ ग्रुप का हो सके या सिर्फ यूज़र का। दोनों को वैकल्पिक (optional) रखने से हम एक समय पर किसी एक को खाली छोड़ सकते हैं।
4. **Question**: How do you run specific tests inside a Django project?
   * **Answer**: By running `python manage.py test <app_name>`. In our case, `python manage.py test expenses`.
   * **Hindi Answer**: विशिष्ट टेस्ट्स को चलाने के लिए `python manage.py test <app_name>` कमांड का उपयोग किया जाता है।
5. **Question**: What file represents the physical database in a default Django setup?
   * **Answer**: A local file named `db.sqlite3` in the project root directory.
   * **Hindi Answer**: प्रोजेक्ट रूट डायरेक्टरी में बनी `db.sqlite3` फ़ाइल वास्तविक डेटाबेस का प्रतिनिधित्व करती है।
6. **Question**: What is the difference between `null=True` and `blank=True` in Django fields?
   * **Answer**: `null=True` is database-related (allows storing NULL in the database columns). `blank=True` is validation-related (allows forms to accept empty values during input validation).
   * **Hindi Answer**: `null=True` डेटाबेस स्तर पर खाली वैल्यू (NULL) रखने की अनुमति देता है। `blank=True` फॉर्म और इनपुट वैलिडेशन के स्तर पर खाली छोड़ने की अनुमति देता है।
7. **Question**: How does a `ManyToManyField` differ from a `ForeignKey` in database design?
   * **Answer**: A `ForeignKey` represents a one-to-many relationship (one row links to one parent). A `ManyToManyField` represents a many-to-many relationship, which requires a third table (join table) to map multiple relationships between both tables.
   * **Hindi Answer**: `ForeignKey` एक-से-अनेक (one-to-many) संबंध दर्शाता है। `ManyToManyField` अनेक-से-अनेक संबंध दर्शाता है, जिसके लिए दोनों तालिकाओं के बीच संबंधों को मैप करने के लिए एक तीसरी तालिका (join table) की आवश्यकता होती है।

---
---

# PHASE 4: User Authentication (फेज 4: यूज़र ऑथेंटिकेशन)

## 1. Core Concepts (मूल सिद्धांत)

### What is User Authentication? (यूज़र ऑथेंटिकेशन क्या है?)
* **English**: User authentication verifies the identity of a person logging in. Django's built-in authentication system (`django.contrib.auth`) manages user registrations, database queries, and secures browser sessions automatically.
* **Hindi**: यूज़र ऑथेंटिकेशन वह प्रक्रिया है जिससे हम यूजर की पहचान की पुष्टि करते हैं। Django का इन-बिल्ट ऑथेंटिकेशन सिस्टम यूजर रजिस्ट्रेशन, डेटाबेस पासवर्ड वेरिफिकेशन और ब्राउज़र सेशन को सुरक्षित रूप से हैंडल करता है।

### CSRF Protection (CSRF प्रोटेक्शन)
* **English**: CSRF (Cross-Site Request Forgery) is a security vulnerability where malicious websites trick authenticated users into submitting unwanted commands. Django blocks this by attaching a unique cryptographic token (`{% csrf_token %}`) to forms, ensuring requests originate only from our application.
* **Hindi**: CSRF (क्रॉस-साइट रिक्वेस्ट फोर्जरी) एक सुरक्षा खतरा है जहाँ कोई बाहरी वेबसाइट किसी लॉगिन यूज़र के नाम पर गलत कमांड भेज सकती है। Django हर फॉर्म में `{% csrf_token %}` जोड़कर इससे सुरक्षा प्रदान करता है।

### Django Forms & Validation (जैंगो फॉर्म्स और वैलिडेशन)
* **English**: Django Forms is a class-based component that renders HTML input forms, validates submitted data (type checking, length, custom checks), and yields human-friendly error messages if validation fails.
* **Hindi**: Django Forms एक घटक है जो स्वचालित रूप से HTML इनपुट बॉक्स बनाता है, इनपुट डेटा को चेक करता है (जैसे ईमेल फॉर्मेट, पासवर्ड का मिलना) और गलत होने पर त्रुटियों के संदेश दिखाता है।

---

## 2. Created & Modified Files Explanation (बनाई और बदली गई फ़ाइलों का विवरण)

### A. `expenses/forms.py` [NEW] (रजिस्ट्रेशन और लॉगिन फॉर्म्स)
* **English**: Defines `UserRegistrationForm` (model-linked for signing up new users) and `UserLoginForm` (standard form for credentials validation).
* **Hindi**: यह फ़ाइल यूज़र रजिस्ट्रेशन और लॉगिन के लिए फॉर्म्स डिफाइन करती है।

#### Important Code Explanation (महत्वपूर्ण कोड का स्पष्टीकरण):
* `class UserRegistrationForm(forms.ModelForm):`
  * **English**: Inherits from `ModelForm` and binds directly to the built-in `User` model, specifying fields like `username` and `email`.
  * **Hindi**: यह फॉर्म सीधे जैंगो के इन-बिल्ट `User` मॉडल के ऊपर आधारित है, जिससे हमें `username` और `email` इनपुट मिलते हैं।
* `password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}), help_text="Required. Use a strong password.")`
  * **English**: Creates a password text input widget that masks the text characters.
  * **Hindi**: यह इनपुट फ़ील्ड पासवर्ड छुपाने (PasswordInput widget) के लिए है।
* `def clean_email(self):`
  * **English**: Validates that the submitted email is unique. If a user with this email already exists, it raises a `ValidationError`.
  * **Hindi**: यह चेक करता है कि यह ईमेल पहले से ही रजिस्टर्ड है या नहीं। यदि है, तो एरर संदेश देता है।
* `def clean(self):`
  * **English**: A form-level cleaner that fetches both password values and checks if they match. If they don't, it appends an error to the `confirm_password` field.
  * **Hindi**: यह फ़ंक्शन चेक करता है कि पासवर्ड और कन्फर्म पासवर्ड दोनों एक जैसे हैं या नहीं।
* `def save(self, commit=True):`
  * **English**: Overrides saving behaviour to call `user.set_password(self.cleaned_data["password"])` which hashes the password securely before executing SQL inserts.
  * **Hindi**: यह सेव करने से पहले सादे पासवर्ड को सुरक्षित रूप से एनक्रिप्ट (हैश) करने का काम करता है।

---

### B. `expenses/views.py` [MODIFY] (ऑथेंटिकेशन व्यूज़)
* **English**: Houses the authentication controller views. It runs forms processing, validates user input, handles redirects, and initializes session records.
* **Hindi**: इसमें रजिस्ट्रेशन, लॉगिन और लॉगआउट की मुख्य लॉजिक लिखी गई है।

#### Important Code Explanation (महत्वपूर्ण कोड का स्पष्टीकरण):
* `if request.user.is_authenticated:`
  * **English**: Checks if the request sender is already logged in. If true, redirects them directly to the dashboard to avoid showing login forms again.
  * **Hindi**: यह जांचता है कि यूजर पहले से लॉगिन तो नहीं है। यदि है, तो उसे सीधे डैशबोर्ड पर भेज देता है।
* `user = authenticate(request, username=username, password=password)`
  * **English**: Verifies the username and password against the database records. If they are correct, it returns the `User` instance; else, it returns `None`.
  * **Hindi**: यह यूजरनेम और पासवर्ड की जांच डेटाबेस से करता है। सही होने पर यूजर ऑब्जेक्ट लौटाता है, नहीं तो `None` देता है।
* `login(request, user)`
  * **English**: Saves the authenticated user's ID into Django's session backend, establishing a cookie in the browser.
  * **Hindi**: यह यूजर का लॉग-इन सेशन शुरू करता है और कुकी सेट करता है।
* `logout(request)`
  * **English**: Flushes the session data from the server and browser cookie store, logging the user out.
  * **Hindi**: यह सेशन कुकी को मिटा देता है और यूजर को लॉगआउट कर देता है।
* `@login_required(login_url='login')`
  * **English**: Decorator that protects views. If an unauthenticated user visits `/`, they are redirected to the login view with a `next` query parameter.
  * **Hindi**: यह एक डेकोरेटर है जो बिना लॉगिन किए डैशबोर्ड देखने से रोकता है और लॉगिन पेज पर रीडायरेक्ट करता है।

---

### C. `expenses/urls.py` & `config/urls.py` [MODIFY] (राउटिंग कॉन्फ़िगरेशन)
* **English**: Configures the main page routes pointing login, register, logout, and dashboard views to root URLs `/login/`, `/register/`, `/logout/`, and `/`.
* **Hindi**: यह राउटिंग कॉन्फ़िगरेशन को अपडेट करता है ताकि यूज़र मुख्य पेजों (लॉगिन, साइनअप, डैशबोर्ड) को सही URL से एक्सेस कर सके।

---

### D. HTML Templates (एचटीएमएल टेम्पलेट्स)
* **`base.html`**:
  * **English**: Parent layout providing standard HTML header structure and custom beautiful modern dark theme styling with glowing elements and interactive navbar.
  * **Hindi**: यह पैरेंट टेम्पलेट है जो पूरे ऐप में एक समान रूप से आधुनिक डार्क-थीम और नेविगेशन बार दिखाता है।
* **`register.html`**:
  * **English**: Registration form rendering text inputs, displaying form field errors, and enforcing CSRF protection.
  * **Hindi**: रजिस्ट्रेशन फॉर्म जो यूजर इनपुट फ़ील्ड, फॉर्म त्रुटियों और CSRF सुरक्षा को रेंडर करता है।
* **`login.html`**:
  * **English**: Form for logging in, showing authentication invalidity alerts, and utilizing a safe POST submission protocol.
  * **Hindi**: लॉगिन करने के लिए फॉर्म जिसमें एरर मैसेज और सुरक्षित POST प्रोटोकॉल शामिल है।
* **`dashboard.html`**:
  * **English**: User profile landing dashboard, showing session details and dynamic logout trigger options.
  * **Hindi**: लॉगिन होने के बाद प्रोफाइल डैशबोर्ड जो यूजर की डिटेल्स दिखाता है।

---

## 3. Steps Performed & Commands Used (किए गए कदम और उपयोग किए गए कमांड्स)

1. **Created Forms**: Created `expenses/forms.py` utilizing the Forms API.
2. **Created Views**: Designed registration, login, logout, and dashboard views in `expenses/views.py`.
3. **Updated Routes**: Set up routing mappings in `expenses/urls.py` and included it in the root `config/urls.py`.
4. **Designed Front-end templates**: Built custom glassmorphic HTML files in `expenses/templates/expenses/`.
5. **Ran Unit Tests**: Verify correctness using the test command:
   ```powershell
   .\venv\Scripts\python.exe manage.py test
   ```

---

## 4. Best Practices & Common Mistakes (बेस्ट प्रैक्टिसेज और आम गलतियां)

* **Best Practice**: Always hash passwords using Django's built-in `set_password` method. Raw passwords saved in databases are high-security risks.
* **Best Practice (Hindi)**: डेटाबेस में कभी भी पासवर्ड को प्लेन टेक्स्ट में स्टोर न करें, हमेशा `set_password` का उपयोग करके हैश करें।
* **Best Practice**: Protect all form actions with `{% csrf_token %}` to secure state-altering actions from cross-site scripts.
* **Best Practice (Hindi)**: सभी POST फॉर्म्स को `{% csrf_token %}` टैग के साथ सुरक्षित करें।
* **Common Mistake**: Omitting `method="post"` in form tags. Defaulting to standard `GET` maps credentials directly in request URLs.
* **Common Mistake (Hindi)**: फॉर्म्स में `method="post"` न लिखना, जिससे इनपुट डेटा URL में दिखने लगता है।
* **Common Mistake**: Trying to render forms without displaying error lists like `{{ field.errors }}` which leaves users confused on form validation failures.
* **Common Mistake (Hindi)**: एरर्स (`field.errors`) दिखाना भूल जाना, जिससे यूजर को पता ही नहीं चलता कि फॉर्म सबमिट क्यों नहीं हुआ।

---

## 5. Viva / Interview Questions (वाइवा / इंटरव्यू के प्रश्न)

1. **Question**: What is the purpose of Django's `cleaned_data` dictionary?
   * **Answer**: It contains verified and sanitized input values after `form.is_valid()` runs successful validation routines.
   * **Hindi Answer**: `form.is_valid()` चलने के बाद साफ और जांचा हुआ डेटा `cleaned_data` डिक्शनरी में उपलब्ध हो जाता है।

2. **Question**: How does Django protect against Cross-Site Request Forgery (CSRF)?
   * **Answer**: By verifying a hidden cryptographic token inside incoming POST requests against a cookie token set in the user's browser session.
   * **Hindi Answer**: यह POST रिक्वेस्ट में भेजे गए सीक्रेट टोकन की तुलना यूज़र ब्राउज़र सेशन में सेट कुकी टोकन से करके सुरक्षा प्रदान करता है।

3. **Question**: What is password hashing and why is it crucial?
   * **Answer**: Hashing converts a plaintext password into an irreversible, fixed-length encrypted string using cryptographic algorithms (like PBKDF2). This prevents hackers from viewing passwords even if they gain access to the database.
   * **Hindi Answer**: पासवर्ड हैशिंग एक ऐसी तकनीक है जो पासवर्ड को एक जटिल सुरक्षित कोड में बदल देती है जिसे वापस सादे शब्द में बदला नहीं जा सकता।

4. **Question**: What does the `@login_required` decorator do behind the scenes?
   * **Answer**: It intercepts view requests. If the user session isn't logged in, it intercepts the request and redirects them to the page configured in `login_url` with the original URL set in `next`.
   * **Hindi Answer**: यह यूजर सेशन चेक करता है। यदि यूजर लॉगिन नहीं है, तो उसे लॉगिन यूआरएल पर भेज देता है और `next` पैरामीटर में वापस आने वाले पेज का पाथ रख लेता है।

5. **Question**: Why do we override the standard `save()` method in a custom `ModelForm` registration?
   * **Answer**: The standard `ModelForm.save()` would write the input fields directly to the DB. Since passwords should never be written in plaintext, we override it to call `set_password()` to perform hashing first.
   * **Hindi Answer**: डिफ़ॉल्ट `save()` पासवर्ड को प्लेन टेक्स्ट में डेटाबेस में लिख देगा। इसलिए हम उसे ओवरराइड करके पहले `set_password()` से पासवर्ड हैश करते हैं।



