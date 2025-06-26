
# CMS API with FastAPI

This project is a lightweight content management system (CMS) API built using **FastAPI**, supporting user authentication, blog creation, and like/unlike functionality.

---

## 🚀 Features

- **User Account Management**: Register, login, update, delete user accounts.
- **JWT Authentication**: Secure authentication using OAuth2 with JWT tokens.
- **Blog Post API**: Create, retrieve, update, delete blog posts with visibility controls (public/private).
- **Like System**: Users can like/unlike public or their own blog posts.
- **Access Control**: Only post owners can edit/delete their posts. Private posts are only viewable by their owners.
- **SQLAlchemy (2.0 style)**  for object relation mapping.
- **100% Test Coverage** using `pytest`.
- **API Versioning**: Clean `/v1/...` structured endpoints.

---

## 📦 Technology Stack

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy**
- **JWT (PyJWT)**
- **SQLite** (default, can be configured for MySQL/Postgres)
- **pytest** for testing

---

## 🛠 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/fastapi-cms-demo.git
cd fastapi-cms-demo
```

### 2️⃣ Create & Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables
Create a `.env` file with the following content:
```
DB_USER=root
DB_PASSWORD=yourpass
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_db_name
SECRET_KEY=your-secret-key
```

### 5️⃣ Run the Application
```bash
uvicorn src.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI

---

## 🧪 Running Tests

```bash
pytest --cov=src tests/
```

You should see near **100% coverage** if setup properly.

---

## 📂 Folder Structure

```
src/
├── api/v1/
│   ├── accounts.py
│   ├── blog.py
│   └── like.py
├── auth.py
├── database.py
├── init_db.py
├── main.py
├── models.py
└── schemas.py
tests/
    ├── test_accounts.py
    ├── test_blog.py
    ├── test_like.py
    ├── test_auth.py
    ├── test_main_extra.py
    └── conftest.py
```

---

## 🧑‍💻 Author

Developed by **Paras Chauhan**  
[GitHub](https://github.com/pc-crazy) | [LinkedIn](https://www.linkedin.com/in/paras-chauhan/)

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
