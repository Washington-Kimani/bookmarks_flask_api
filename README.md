# Bookmark Flask API
___
### Access your bookmarks from any device on any website!
This is a python API that offers CRUD operations for bookmarks to websites that the user find interesting and would like to frequently revisit.

___
## Features

- Authentication (login/register) with access and refresh tokens.
- Create, Read, Update, Archive and Delete bookmarks
- Url shortener
- Web Scraping for website icon
- Metadata and pagination from the backend
___

## Tech Stack
* Python v3.10
* Flask
* SQL Alchemy
* BeautifulSoup
* JWT

___

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Washington-Kimani/bookmarks_flask_api.git
cd bookmarks_flask_api
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate       # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the Flask API

```bash
flask run
```

By default, it will run at:

```
http://0.0.0.0:5000
```
___
## Available Routes
- `POST`'/api/v1/auth/login' - login route
- `POST`'/api/v1/auth/register' - to create new account
- `GET`'/api/v1/bookmarks' - to get all the bookmarks
- `POST`'/api/v1/bookmarks' - to create a new bookmark
- `PUT`'/api/v1/bookmarks/id - to edit a bookmark
- `POST`'/api/v1/bookmark/id/archive' - to archive a bookmark
- `DELETE` '/api/v1/bookmark/id' - to delete a bookmark

___
