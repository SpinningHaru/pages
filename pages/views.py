# Django related imports
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.conf import settings

# Python related imports
import os
from datetime import datetime
import markdown
import pytz
import re
import inspect

tokyo_tz = pytz.timezone('Asia/Tokyo')

def extract_heading_number(html):
    match = re.search(r'<h([1-9])[^>]*>', html, re.IGNORECASE)
    if match:
        return True, int(match.group(1))  # Extract the number and convert to int
    return False, 0  # Return None if no heading is found

def md_to_html (md_content):
    html_content = markdown.markdown(md_content)
    parts = re.split(r'(<h[1-9][^>]*>.*?</h[1-9]>)', html_content, flags=re.IGNORECASE)
    b, n = True, 1
    html = ''
    for p in parts:
        b, n_ = extract_heading_number(p)
        if b:
            n = n_
            html += p
        else:
            if p == '':
                html = html
            else:
                html += (f"\n<div class=level{n}>" + p +"</div>\n")
    return html




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

    # get the files in the dirctory
    md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
    if len(md_files) == 0:
        return HttpResponseNotFound("Page not found")
    
    def extract_datetime(filename):
        # We assume filename format is 'YYYY-MM-DD_HH-MM-SS.md'
        filename_without_extension = filename[:-3]  # Remove '.md'
        return datetime.strptime(filename_without_extension, '%Y-%m-%d_%H-%M-%S')
    
    # Sort the files by their timestamp and get the most recent file
    md_files.sort(key=extract_datetime, reverse=True)
    md_path = os.path.join(md_dir, md_files[0])

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = md_to_html(md_content)
    
    return render(request, "pages/page.html", {"content": html_content, "title": title, "last_modified": md_files[0][:-3]})


'''
md_dir: Absolute path of the markdown file, including the filename  
ver_files: List of version files representing page history  
del_file: Target file to be deleted, linked to the Delete button  
del_btn: Delete button state (True = enabled, False = disabled, default: True)  
context: Stores the file path for deletion in the session  
'''
@staff_member_required
def render_edit_page(request, title):
    # get file puth. if md_dir does not exist, create it
    md_dir = os.path.join(CONTENT_DIR, title)
    # if there is no file, deactivate button
    del_btn = True

    # get version history dropdown
    # disable dropdown and delete button if no directory exists
    if not os.path.isdir(md_dir):
        ver_files = ['There is no version history.']
        del_file = None
        del_btn = False
    elif len([f for f in os.listdir(md_dir) if f.endswith('.md')]) == 0:
        ver_files = ['There is no version history.']
        del_file = None
        del_btn = False
    else:
        if request.POST.get("action") != "delete":
            # get the version pages as list and sort it
            md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
            def extract_datetime(filename):
                filename_without_extension = filename[:-3]  # Remove '.md'
                return datetime.strptime(filename_without_extension, '%Y-%m-%d_%H-%M-%S')
            md_files.sort(key=extract_datetime, reverse=True)
            # drop-down list files
            ver_files = md_files
            # set the most recent md file to del_file
            del_file = md_files[0]
            del_file_path = os.path.join(md_dir, del_file)
            request.session['context'] = del_file_path

        
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
            preview_content = md_to_html(new_content)
            return render(request, "pages/edit.html", {"content": new_content, "preview_content": preview_content, "ver_files": ver_files,"del_file":del_file, "del_btn": del_btn})

        elif request.POST.get("action") == "cancel":
            return redirect("render_page", title=title)
        
        elif request.POST.get("version_page_selected"):
            del_file = request.POST.get("version_page_selected")
            del_file_path = os.path.join(md_dir, del_file)
            # set selected file name to context in order to delete the file later
            request.session['context'] = del_file_path

            with open(del_file_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            if existing_content == "":
                existing_content = "# " + title + "\n\n" + "Write your content here"
            preview_content = md_to_html(existing_content)

            return render(request, "pages/edit.html", {"content": existing_content, "preview_content": preview_content, "title": title, "ver_files": ver_files, "del_file":del_file, "del_btn": del_btn})
        
        elif request.POST.get("action") == "delete":
            # get the selected file path (default is current file if none selected)
            context = request.session.get('context', {})
            os.remove(context)
            print(f"{context} was DELETED!")
    
            # After deleting, get the files again and sort it
            md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
            def extract_datetime(filename):
                filename_without_extension = filename[:-3]  # Remove '.md'
                return datetime.strptime(filename_without_extension, '%Y-%m-%d_%H-%M-%S')
            md_files.sort(key=extract_datetime, reverse=True)
            
            # delete the directory, if no file exist
            if len(md_files) == 0:
                print("File NOT exsist")
                os.rmdir(md_dir)
                return redirect("render_page", title=title)
            else:
                # set the most recent md file to del_file
                del_file = md_files[0]
                del_file_path = os.path.join(md_dir, del_file)
                request.session['context'] = del_file_path
                # get context for function of preview
                md_path = os.path.join(md_dir, md_files[0])
                with open(md_path, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                if existing_content == "":
                    existing_content = "# " + title + "\n\n" + "Write your content here"
                preview_content = md_to_html(existing_content)
                # get version files
                ver_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
                ver_files.sort(reverse=True)

            return render(request, "pages/edit.html", {"content": existing_content, "preview_content": preview_content, "title": title, "ver_files": ver_files, "del_file":del_file, "del_btn": del_btn})
            
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
    preview_content = md_to_html(existing_content)

    return render(request, "pages/edit.html", {"content": existing_content, "preview_content": preview_content, "title": title, "ver_files": ver_files, "del_file":del_file, "del_btn": del_btn})