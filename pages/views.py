# Django related imports
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.conf import settings# Python related imports
import os
from datetime import datetime
import markdown
import pytz

tokyo_tz = pytz.timezone('Asia/Tokyo')


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Path to `pages/`
# os.path.join(BASE_DIR, "contents")  # Path to `pages/contents/`

CONTENT_DIR = settings.PAGES_DIR 
HOME =settings.PAGES_HOME

def render_page(request, title=HOME):
    # when edit page is requested:
    # GET catches when ?edit=true
    # POST catches when a form is submitted already from the edit page
    if request.method == "GET":
        if request.GET.get("edit", "") == "true":
            return render_edit_page(request, title)    
    if request.method == "POST":
        return render_edit_page(request, title)    
    
    # otherwise, render the page
    md_dir = os.path.join(CONTENT_DIR, title)

    # if the given title is not a directory, return 404
    if not os.path.isdir(md_dir):
        return HttpResponseNotFound("Page not found")

    # otherwise, render the page of the most recent md file
    md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
    if len(md_files) == 0:
        return HttpResponseNotFound("Page not found")
    
    def extract_datetime(filename):
        # We assume filename format is 'YYYY-MM-DD_HH-MM-SS.md'
        filename_without_extension = filename[:-3]  # Remove '.md'
        return datetime.strptime(filename_without_extension, '%Y-%m-%d_%H-%M-%S')
    
    # Sort the files by their timestamp (most recent first)
    md_files.sort(key=extract_datetime, reverse=True)

    # Get the most recent file
    md_path = os.path.join(md_dir, md_files[0])

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content)
    
    return render(request, "pages/page.html", {"content": html_content, "title": title, "last_modified": md_files[0][:-3]})

@staff_member_required
def render_edit_page(request, title):
    
    # if md_dir does not exist, create it
    md_dir = os.path.join(CONTENT_DIR, title)

    # drop-down list of version history
    # if there is no directory, there is no version history
    if not os.path.isdir(md_dir):
        version_pages = ['There is no version history.']
    # if there is no md file in the directory, there is no version history
    elif len([f for f in os.listdir(md_dir) if f.endswith('.md')]) == 0:
        version_pages = ['There is no version history.']
    else:
        version_pages = [f for f in os.listdir(md_dir) if f.endswith('.md')]
        version_pages.sort(reverse=True)
        
    if request.method == "POST":
        new_content = request.POST.get("content", "")

        if request.POST.get("action") == "save":
            timestamp = datetime.now(tokyo_tz).strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{timestamp}.md"
            file_path = os.path.join(md_dir, filename)
            os.makedirs(md_dir, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return redirect("render_page", title=title)

        elif request.POST.get("action") == "preview":
            preview_content = markdown.markdown(new_content)
            return render(request, "pages/edit.html", {"content": new_content, "preview_content": preview_content, "title": title, "version_pages": version_pages})

        elif request.POST.get("action") == "cancel":
            return redirect("render_page", title=title)
        
        elif request.POST.get("version_page_selected"):
            selected_page = request.POST.get("version_page_selected")
            selected_page_path = os.path.join(md_dir, selected_page)
            with open(selected_page_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            if existing_content == "":
                existing_content = "# " + title + "\n\n" + "Write your content here"
            preview_content = markdown.markdown(existing_content)
            return render(request, "pages/edit.html", {"content": existing_content, "preview_content": preview_content, "title": title, "version_pages": version_pages})
    
    # When the request method is GET, wants to start editting the file
    
    # if the directory does not exist, let the existing_content be an empty string
    if not os.path.isdir(md_dir):
        existing_content = ""

    # if the directory exists, it must mean that there is a md file in it. Read the most recent
    else:
        md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
        def extract_datetime(filename):
            filename_without_extension = filename[:-3]  # Remove '.md'
            return datetime.strptime(filename_without_extension, '%Y-%m-%d_%H-%M-%S')
        md_files.sort(key=extract_datetime, reverse=True)
        
        if len(md_files) == 0:
            existing_content = ""
        else:
            md_path = os.path.join(md_dir, md_files[0])
            with open(md_path, "r", encoding="utf-8") as f:
                existing_content = f.read()

    if existing_content == "":
        existing_content = "# " + title + "\n\n" + "Write your content here"
    preview_content = markdown.markdown(existing_content)

    return render(request, "pages/edit.html", {"content": existing_content, "preview_content": preview_content, "title": title, "version_pages": version_pages})