from flask import Flask,render_template, redirect, url_for, request, abort, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/")
#Page de garde
def root():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route("/test")
def page_de_test():
    return render_template('test.html')

@app.route("/Genes")
#Une page contenant les 1000 premièrs gènes de la table Genes,
#affichant pour chacun son identifiant (Ensemble_Gene_ID)
#et son Associated_Gene_Name.
#L’identifiant doit être un lien vers la fiche individuelle
#de ce gène (cf. /Genes/view/ ci-dessous).
def table_1000_genes():
    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()
    db.execute("SELECT Ensembl_Gene_ID AS id, Associated_Gene_Name AS name FROM Genes ORDER BY Ensembl_Gene_ID LIMIT 1000")
    gene_id_table = db.fetchall()
    return render_template("gene_list.html", table=gene_id_table)

@app.route("/Genes/view/<id>")
#La fiche individuelle du gène ayant l’identifiant id.
#Elle doit contenir toutes les informations données par
#la table Genes, ainsi que la liste de ses transcrits
#(accompagnés de leurs positions de départ et de fin).
def view_gene(id):
    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()
    db.execute("SELECT * FROM Genes WHERE Ensembl_Gene_ID = '%s' " %id)
    infos_gene = db.fetchall()
    gcolnames = colnames_parsing([desc[0] for desc in db.description])
    db.execute("SELECT Ensembl_Transcript_ID, Transcript_Start, Transcript_End FROM Transcripts WHERE Ensembl_Gene_ID = '%s' " %id)
    infos_transcripts = db.fetchall()
    tcolnames = colnames_parsing([desc[0] for desc in db.description])
    return render_template("indiv_gene_page.html", gene_id=id, gdata=infos_gene, gcolnames=gcolnames, tdata=infos_transcripts, tcolnames=tcolnames)

def colnames_parsing(colnames):
    newnames = []
    for cn in colnames:
        ncn = cn.replace("_"," ")
        newnames.append(ncn)
    return newnames

@app.route("/Genes/del/<id>", methods=['POST'])
#Cette URL ne doit accepter que les requêtes POST.
#Dans ce cas, le gène ayant l’identifiant id sera supprimé
#de la table Genes.
#Ajoutez à chaque ligne de la liste des gènes un bouton
#supprimant le gène concerné (il faut pour cela un formulaire
#dont l’action est l’URL appropriée, et contenant
#uniquement le bouton).
def del_gene(id):
    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()
    db.execute("DELETE FROM Genes WHERE Ensembl_Gene_ID = '%s' " %id)
    conn.commit()
    return redirect(url_for("table_1000_genes", rm=id))


@app.route("/Genes/new", methods=['POST', 'GET'])
#Un GET sur cette URL doit afficher un formulaire de
#saisie, permettant de décrire un nouveau gène.
#Un POST sur cette URL doit accepter les données du
#formulaire ci-dessus, vérifier leur validité, et créer
#l’entrée correspondante dans la table Genes, puis rediriger
#vers la listes des gènes. En cas de problème, un code
#d’erreur et un message appropriés doivent être retourné.
#Ajoutez au dessus de la liste des gènes un lien vers ce
#formulaire.
def new_gene():
    if request.method=='GET':
        meth="get"
        return render_template("add_form.html", meth=meth)
    elif request.method=='POST':
#Ensembl_Gene_ID 	Associated_Gene_Name 	Chromosome_Name
#Band 	Strand 	Gene_Start 	Gene_End 	Transcript_count
        if check_new_entry(request.form['gene_id']):
            gene_id=request.form['gene_id']
            query = add_gene_query(request.form)
            conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
            db = conn.cursor()
            db.execute(query)
            conn.commit()
            return redirect(url_for("view_gene", id=gene_id))
        else:
            abort(418)

def add_gene_query(request):
    new_gene_infos = [request['gene_id'],request['a_gene_name'],request['chr_name'],request['band'],request['strand'],request['gene_start'],request['gene_end'],request['transcript_count']]
    query = "INSERT INTO Genes (Ensembl_Gene_ID, Associated_Gene_Name, Chromosome_Name, Band, Strand, Gene_Start, Gene_End, Transcript_count) VALUES ("
    for info in new_gene_infos:
        query = query + "'" + info + "'" + ', '
    query = query.strip(', ') + ");"
    return query

def check_new_entry(gene_id):
    if gene_id != 'Ensembl_Gene_ID' and gene_id.startswith('ENSG'):
        conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
        db = conn.cursor()
        db.execute("SELECT * FROM Genes WHERE Ensembl_Gene_ID = '%s' " %gene_id)
        info = db.fetchall()
        try :
            info[0]
            return False
        except :
            return True
    else :
        return False

#===============================================================================
#                                  API
#===============================================================================

@app.route("/api/Genes/<id>", methods=['GET'])
#    fournit la représentation détaillée du gène correspondant.
#    Si l’identifiant fourni ne correspond à aucun gène, retourne
#    un objet erreur avec le code 404.
def api_gene_id(id):
    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()
    db.execute("SELECT * FROM Genes WHERE Ensembl_Gene_ID = '%s' " %id)
    infos_gene = db.fetchall()
    if infos_gene == [] :
        error = """{"error": "Ce gène n'existe pas"}"""
        return error
    else :
        infos_gene=infos_gene[0]
        db.execute("SELECT Ensembl_Transcript_ID, Transcript_Start, Transcript_End FROM Transcripts WHERE Ensembl_Gene_ID = '%s' " %id)
        infos_transcripts = db.fetchall()

        #remplissage du json
        gene_detailed_json = """"Ensembl_Gene_ID": "%s",
        "Associated_Gene_Name": "%s",
        "Chromosome_Name": "%s",
        "Band": "%s",
        "Strand": %d,
        "Gene_End": %d,
        "Gene_Start": %d,
        "transcripts": [""" %(infos_gene[0],infos_gene[1],infos_gene[2],infos_gene[3],infos_gene[4],infos_gene[5],infos_gene[6])

        tx = ""
        for data in infos_transcripts :
            tx += """{"Ensembl_Transcript_ID": "%s",
            "Transcript_End": %d,
            "Transcript_Start": %d},""" %(data[0],data[1],data[2])

        tx=tx.strip(',')
        gene_detailed_json = gene_detailed_json + tx + "]}"

        return gene_detailed_json

@app.route("/api/Genes/", methods=['GET'])
#   fournit les 100 premièrs gènes de la base (triés selon Ensembl_Gene_ID),
#   sous la forme d’une liste de représentations compactes.
#   Si un paramètre ?offset=X est fourni, fournit les 100 premiers gènes de
#   la base à partir du (X+1)-ième.
def api_gene_list():
    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()
    db.execute("SELECT * FROM Genes LIMIT 100")
    gene_list = db.fetchall()

    compact_gene_list = []

    for gene in gene_list :
        gene_href = "http://localhost:5000/api/Genes/" + gene[0]
        gene_rep = {
        "Ensembl_Gene_ID": gene[0],
        "Associated_Gene_Name": gene[1],
        "Chromosome_Name": gene[2],
        "Band": gene[3],
        "Strand": gene[4],
        "Gene_End": gene[5],
        "Gene_Start": gene[6],
        "Transcript_count": gene[7],
        "href": gene_href}

        compact_gene_list.append(gene_rep)

    return jsonify(compact_gene_list)

@app.route("/api/Genes/", methods=['POST'])
#accepte une représentation détaillée d’un gène à l’exception de l’attribut
#transcripts, et l’ajoute à la base si les conditions suivantes sont remplies ;
#    Ensemble_Gene_ID est renseigné, est une chaîne, et n’est pas un identifiant déjà présent dans la base ;
#    Chromosome_Name est renseigné, et est une chaîne ;
#    Band est une chaîne (ou non renseigné) ;
#    Strand est un entier (ou non renseigné) ;
#    Gene_Start est renseigné, et est un entier ;
#    Gene_End est renseigné, est un entier, et est supérieur à Gene_Start ;
#    Associated_Gene_Name est une chaîne (ou non renseigné) ;
#    l’objet ne possède aucun autre attribut.
#En cas de violation d’une de ces contraintes, retourne un objet erreur avec le code 4xx adéquat.
#En cas de succès, retourne le code 201 (created) avec un objet de la forme :
def api_add_gene():
    posted_dict = request.json

    conn =sqlite3.connect('ensembl_hs63_simple.sqlite')
    db = conn.cursor()

    try:
        if type(posted_dict["Ensembl_Gene_ID"])!=str:
            print("1")
            return jsonify({"response":"wrong gene format"})
        else:
            print("2")
            db.execute("SELECT * FROM Genes WHERE Ensembl_Gene_ID = " + posted_dict["Ensembl_Gene_ID"])
            dbreq=db.fetchall()
            print(dbreq)
            if len(dbreq)!=0 :
                return jsonify({"response":"already in db"})
            else:
                return jsonify({"response":"gene checked"})
        if type(posted_dict["Chromosome_Name"])!=str:
            return jsonify({"response":"ABORT chr name"})
        if type(posted_dict["Gene_Start"])!=int:
            return jsonify({"response":"ABORT start"})
        if type(posted_dict["Gene_End"])!=int or posted_dict["Gene_End"]<=posted_dict["Gene_Start"]:
            return jsonify({"response":"ABORT end"})
        return jsonify({'response':'OK'})
    except:
        return jsonify({"response":"ABORT abort"})


if __name__ == "__main__" :
    app.run(debug=True)
