
Compile scss
```bash
sass static/scss/main.scss static/css/main.css --style=compressed
```
Watch scss
```bash
sass --watch static/scss/main.scss static/css/main.css --style=compressed
```

Run development server
```bash
source ~/mysite/venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```
Then go to: 
http://172.22.210.37:8000/

## Git Flow

0. See what's changed.

```bash
git status
```

1. Add your changes.

```bash
# Add everything you've done.
git add .

# or add specific files.
git add file1.txt file2.txt
```

2. Commit them to the local git repository.

```bash
git commit -m "Your description of changes."
```

3. Push them to your remote origin on Github.

```bash
git push
```