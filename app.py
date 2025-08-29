from flask import Flask, render_template, request

app=Flask(__name__)

@app.route("/", methods = ["GET","POST"])
def upload_page():
    if request.method == "POST":

        file1 = request.files.get("file1")
        file2 = request.files.get("file2")
        file3 = request.files.get("file3")
    
    return render_template("upload_page.html")
