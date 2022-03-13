from flask import Flask, render_template, request
import quickstart

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    f=open("end.txt", "a")
    f.write(str(request.form.get("hour"))+",")
    f.write(str(request.form.get("min")))
    f.write("|")
    f.close()

    f=open("eventList.txt", "a")
    f.write(str(request.form.get("name"))+",")
    f.write(str(request.form.get("length"))+",")
    f.write(str(request.form.get("difficulty"))+",")
    f.write(str(request.form.get("description")))
    f.write('|')
    f.close()
    return render_template("form.html")

@app.route("/cool", methods=["GET", "POST"])
def cool():
    quickstart.main()
    return render_template("form.html")



