# Gift Tracker

## Run the app

To get the app running, follow these steps.

### 1. Clone the repo

```bash
git clone [the-repo-url]
```

### 2. Set up virtual environment
```bash
source $(pwd)/venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install Django pymysql requests beautifulsoup4
```

### 4. Create the database

Login to mysql cli

```bash
mysql -u root
```

Then execute these SQL statements.

```sql
CREATE DATABASE gift_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create the user
CREATE USER 'gift_tracker_user'@'localhost' IDENTIFIED BY 'StrongPassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON gift_tracker.* TO 'gift_tracker_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

### 5. Run migrations

```bash
python3 manage.py migrate
```

### 6. Run development server
```bash
# Enter venv if you haven't. You should see (venv) next to your command line.
source $(pwd)/venv/bin/activate
# run the app (use python or python3, whichever is available on your system)
python3 manage.py runserver 0.0.0.0:8000
```

If you're running locally, then go to:
http://localhost:8000

If you're on the school machine, then go to: 
http://172.22.210.37:8000/

---

## Git Flow

### 0. See what's changed.

```bash
git status
```

### 1. Add your changes.

```bash
# Add everything you've done.
git add .

# or add specific files.
git add file1.txt file2.txt
```

### 2. Commit them to the local git repository.

```bash
git commit -m "Your description of changes."
```

### 3. Push them to your remote origin on Github.

```bash
git push
```