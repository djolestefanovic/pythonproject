from flask import Flask, render_template, url_for, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import mariadb
import ast
import html

konekcija = mysql.connector.connect(
    passwd="", # lozinka za bazu 
    user="root", # korisničko ime
    database="webprojekat", # ime baze
    port=3306, # port na kojem je mysql server
    auth_plugin='mysql_native_password' # ako se koristi mysql 8.x
)

kursor = konekcija.cursor(dictionary=True)

def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False

def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")



# deklaracija aplikacije
app = Flask(__name__)
app.secret_key = "tajni_kljuc_aplikacije"


# logika aplikacije 
@app.route('/', methods=['GET'])
def render_login():
    return render_template('login.html') 


@app.route('/proba/<id>', methods=["GET", "POST"])
def render_primer(id) -> 'html' :
    return render_template('primer.html')

@app.route('/korisnici', methods=['GET'])
def render_korisnici():
    #if ulogovan():
        upit = "select * from korisnici"
        kursor.execute(upit)
        korisnici = kursor.fetchall()
        return render_template('korisnici.html', korisnici = korisnici)
    #else:
        #return redirect(url_for("login"))

@app.route('/korisnik_novi', methods=["GET", "POST"])
def korisnik_novi():
    #if ulogovan():
       if request.method == "GET":
         return render_template('korisnik_novi.html')

       if request.method == "POST":
        forma = request.form
        hesovana_lozinka = generate_password_hash(forma["lozinka"])
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            forma["rola"],
            hesovana_lozinka
        )

        upit = """insert into
                    korisnici(ime, prezime, email, rola, lozinka)
                    values (%s, %s, %s, %s, %s)
        """
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("render_korisnici"))
    #else:
        #return redirect(url_for("login"))    

@app.route('/korisnik_izmena/<id>', methods=["GET", "POST"])
def korisnik_izmena(id) :
    if ulogovan():
        if request.method == "GET":
            upit = "select * from korisnici where id=%s"
        vrednost = (id, )
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        
        return render_template("korisnik_izmena.html", korisnik = korisnik)
    
    if request.method == "POST" :
        upit = """ update korisnici set
                    ime = %s, prezime = %s, email = %s, rola = %s, lozinka = %s
                    where id = %s
        """
        forma = request.form
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            forma["rola"],
            forma["lozinka"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('render_korisnici'))
    else:
        return redirect(url_for("login"))

@app.route('/korisnik_brisanje/<id>', methods=["POST"])
def korisnik_brisanje(id):
    upit = """
               DELETE FROM korisnici WHERE id=%s
           """
    vrednost = (id, )
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("render_korisnici"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        forma = request.form
        upit = "select * from korisnici WHERE email=%s"
        vrednost = (forma["email"],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        #return korisnik
        if korisnik != None:
            #if check_password_hash(korisnik["lozinka"], forma["lozinka"]):
            if korisnik["lozinka"] == forma["lozinka"]:
                session["ulogovani_korisnik"] = str(korisnik)
                return redirect(url_for("render_korisnici"))
            else:
                return render_template("login.html")
        

@app.route('/logout')
def logout():
    session.pop('ulogovani_korisnik',None)
    return redirect(url_for('login')) 


@app.route('/igraci', methods=['GET', "POST"])
def render_igraci():
    upit = "select * from igraci"
    kursor.execute(upit)
    igraci = kursor.fetchall()
    return render_template('igraci.html', igraci = igraci) 


@app.route('/igrac_novi', methods=["GET", "POST"])
def igrac_novi():
    #if ulogovan():
       if request.method == "GET":
         return render_template('igrac_novi.html')

       if request.method == "POST":
        forma = request.form
        #hesovana_lozinka = generate_password_hash(forma["lozinka"])
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["poeni"],
            forma["rola"],
            #hesovana_lozinka
        )

        upit = """insert into
                    igraci(ime, prezime, poeni, rola )
                    values (%s, %s, %s, %s)
        """
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("render_igraci"))
    #else:
        #return redirect(url_for("login"))  


@app.route('/igrac_izmena/<id>', methods=["GET", "POST"])
def igrac_izmena(id) :
    if request.method == "GET":
        upit = "select * from igraci where id=%s"
        vrednost = (id, )
        kursor.execute(upit, vrednost)
        igrac = kursor.fetchone()
        
        return render_template("igrac_izmena.html", igrac = igrac)
    
    if request.method == "POST" :
        upit = """ update igraci set
                    ime = %s, prezime = %s, poeni = %s, rola = %s, 
                    where id = %s
        """
        forma = request.form
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["poeni"],
            forma["rola"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('render_igraci'))


@app.route('/igrac_brisanje/<id>', methods=["POST"])
def igrac_brisanje(id):
    upit = """
               DELETE FROM igraci WHERE id=%s
           """
    vrednost = (id, )
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("render_igraci"))


@app.route('/klubovi', methods=['GET', "POST"])
def render_klubovi():
    upit = "select * from klubovi"
    kursor.execute(upit)
    klubovi = kursor.fetchall()
    return render_template('klubovi.html', klubovi = klubovi)


@app.route('/klub_izmena/<id>', methods=["GET", "POST"])
def klub_izmena(id) :
    if request.method == "GET":
        upit = "select * from klubovi where id=%s"
        vrednost = (id, )
        kursor.execute(upit, vrednost)
        klubovi = kursor.fetchone()
        
        return render_template("klub_izmena.html", klubovi = klubovi)
    
    if request.method == "POST" :
        upit = """ update klubovi set
                    sifra = %s, naziv = %s, pozicija = %s, grad = %s, 
                    where id = %s
        """
        forma = request.form
        vrednosti = (
            forma["sifra"],
            forma["naziv"],
            forma["pozicija"],
            forma["grad"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('klubovi'))



@app.route('/klub_novi', methods=["GET", "POST"])
def klub_novi():
    #if ulogovan():
       if request.method == "GET":
         return render_template('klub_novi.html')

       if request.method == "POST":
        forma = request.form
        #hesovana_lozinka = generate_password_hash(forma["lozinka"])
        vrednosti = (
            forma["sifra"],
            forma["naziv"],
            forma["pozicija"],
            forma["grad"],
            #hesovana_lozinka
        )

        upit = """insert into
                    klubovi (sifra, naziv, pozicija, grad)
                    values (%s, %s, %s, %s)
        """
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for("render_klubovi"))
    #else:
        #return redirect(url_for("login"))  



@app.route('/klub_brisanje/<id>', methods=["POST"])
def klub_brisanje(id):
    upit = """
               DELETE FROM klubovi WHERE id=%s
           """
    vrednost = (id, )
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("render_klubovi"))              

    



                    
#pokretanje aplikacije
app.run(debug=True)