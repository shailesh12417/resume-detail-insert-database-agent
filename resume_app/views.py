
from .models import Resume
from .services import extract_resume_data, store_embeddings, search_resume
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request, "index.html")

@csrf_exempt
def upload_resume(request):

    if request.method == "POST":

        files = request.FILES.getlist("files")

        if not files:
            return render(request, "result.html", {"data": "No files uploaded"})

        results = []

        for file in files:

            # save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

                for chunk in file.chunks():
                    tmp.write(chunk)

                tmp_path = tmp.name


            # load PDF
            loader = PyPDFLoader(tmp_path)

            pages = loader.load()

            text = ""

            for page in pages:
                text += page.page_content


            # extract resume details
            data = extract_resume_data(text)


            if data:
                Resume.objects.create(
                    name=data.get("name") or "",
                    email=data.get("email") or "",
                    phone=data.get("phone") or "",
                    github=data.get("github") or "",
                    linkedin=data.get("linkedin") or "",
                    skills=data.get("skills") or "",
                    experience=data.get("experience") or ""
                )


            # store embeddings
            store_embeddings(text, file.name)


            results.append(data)

            os.remove(tmp_path)


        return render(request, "result.html", {"data": results})
    
@csrf_exempt
def search_candidate(request):

    query = request.GET.get("query")

    results = []

    if query:
        results = search_resume(query)

    return render(request, "search_results.html", {
        "query": query,
        "results": results
    })