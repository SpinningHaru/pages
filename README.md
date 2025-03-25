# PAGES (Django Reusable App)

PAGES is a Django reusable app that lets users create and edit web pages without modifying code or using a database. Ideal for single-user projects like personal blogs, it’s easy to install and requires no database. Only administrators can edit pages.

## Features ✨

* Database-free: Store pages as Markdown files on the server (as GitHub pages, as the name suggests.)
* Create & Edit: Manage web pages directly on the website, no code editing required.
* Page History: View version history and revert to previous versions of a page.
* Admin-only Edit Access: Only administrators can make changes.

## Usage
Accessing a page
example.com/pages/path/to/page

opens and renders PAGES_DIR/path/to/page.md stored in the server. Here, PAGES_DIR is the diroctory where the markdown files is stored. It must be set in the project's `settings.py`. 
(Be sure to give a proper ownership/wirte permission for that directory.)

In case there is no such file in the server or you want to edit the existing file, make a GET request with `?edit=true`:

example.com/pages/path/to/page/?edit=true


This will require the admin permission to ensure that no random user will modify or create a file in your server. 

## Installation 🛠️
You can run:

pip install git+ssh://git@github.com/SpinningHaru/pages.git@main

to install. Then, add pages to your INSTALLED_APPS in `settings.py`:

INSTALLED_APPS = [
    ...,
    'pages',
]
and set up URL routing for the app:

path('pages/', include('pages.urls')),


Be sure to have admin enabled.

Further in the `settings.py`, set two variables:

PAGES_DIR

for the directory where the markdown files will be stored and 
PAGES_HOME

for the name of the page that will serve as the front page of your pages application.
(e.g., the page for `example.com/pages`.
