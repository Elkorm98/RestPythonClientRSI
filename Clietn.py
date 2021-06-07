from pprint import pp, pprint
from flask import Flask,redirect, url_for, render_template, request
import requests
import pdfkit


c = 0
dane =""
url = "http://25.76.141.122:8081/RestProjectServer/webresources/"
url_koszyk = ""
login_ = ""
password_ = ""
magazynj = []
danej = []
app = Flask(__name__)

@app.route('/logowanie',methods=["POST","GET"])
def logowanie():
    if request.method == "POST":
        global login_
        global password_
        global magazynj
        login_ = request.form["nm"]
        password_ = request.form["ps"]
        headers = {'login': login_, 'haslo': password_ }
        try:
            magazyn = requests.get(url+"sklep", headers = headers)
            magazynj = magazyn.json()
            return redirect(url_for("sklep"))
        except Exception:
            return "Brak uzytkownika"
    else: 
	    return render_template("logowanie.html")


@app.route('/Sklep/',methods =["POST","GET"])
def sklep():
    global url_koszyk
    
    url_koszyk = magazynj[0]['koszyk_link']['uri']
    konto = requests.get("http://25.76.141.122:8080/RestProjectServer/webresources/"+"sklep/"+"konto")
    kontoj = konto.json()
    ilustracjebase64 = []
    idilosc = []
    for k in magazynj:
       ilustracjebase64.append(k['karta']['ilustracja'])
    for i in range(0,len(magazynj)):
        idilosc.append("id"+str(i))
    if request.method =="POST":
        if request.form["btn"] == "Dodaj do koszyka":
            for i in magazynj:
                if request.form[str(i['karta']['nazwa'])] != "0":
                    ilosc = request.form[str(i['karta']['nazwa'])]
                    requests.put(i['self']['uri'],params={'ilosc': ilosc})
            return render_template("sklep.html",magazyn = magazynj,ilustracje = ilustracjebase64,idilosc=idilosc,konto = kontoj)
        if request.form["btn"] == "Przejdz do koszyka":
            return redirect(url_for("koszyk"))
    else:
        return render_template("sklep.html",magazyn = magazynj,ilustracje = ilustracjebase64,idilosc=idilosc,konto = kontoj)


@app.route("/koszyk/",methods = ["POST","GET"])
def koszyk():
    global c 
    c = 0
    koszyk = requests.get(url_koszyk)
    koszykj = koszyk.json()
    if request.method == "POST":
        for i in koszykj:
            if i['karta']['nazwa'] in request.form:
                requests.delete(url_koszyk +"/"+ i['karta']['nazwa'])
                koszyk = requests.get(url_koszyk)
                koszykj = koszyk.json()
                return render_template("koszyk.html", koszyk = koszykj) 
            elif 'btnn' in request.form:
                return redirect(url_for("info"))
        if 'pow' in request.form:
            return redirect(url_for("sklep"))
    else:
        return render_template("koszyk.html",koszyk = koszykj)


@app.route('/info/potwierdzenie/',methods = ["POST","GET"])
def info():
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    headers = {'login': login_, 'haslo': password_ }
    global magazynj
    global danej
    global c
    if c == 0:
        dane = requests.post(url_koszyk)
        danej = dane.json()
        c = 1
    if request.method == "POST":
        rf = request.form["btn"]
        if rf=="Powrot do sklepu":
            magazyn = requests.get(url+"sklep", headers = headers)
            magazynj = magazyn.json()
            return redirect(url_for("sklep"))
        elif rf == "Pobierz potwierdzenie":
            magazyn = requests.get(url+"sklep", headers = headers)
            magazynj = magazyn.json()
            pdfkit.from_url("http://127.0.0.1:5000/info/potwierdzenie/#", 'Potwierdzenieeeee.pdf', configuration=config)
            return redirect(url_for("sklep"))
    else:
        return render_template("info.html", ds = danej)


@app.route("/printstrona/")
def printstrona():
    global danej
    render_template("info.html", ds = danej)
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdfkit.from_url("http://127.0.0.1:5000/printstrona/", 'Potwierdzenieeeee.pdf', configuration=config)
    return redirect(url_for("sklep"))
    

if __name__ == '__main__':
    app.run(debug=True)