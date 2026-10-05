import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (DictionaryObject, NameObject, TextStringObject,
                           ArrayObject, BooleanObject, NumberObject)

SP = "/tmp/claude-0/-home-user-Gestcompet/5cbaa2ee-e715-50e4-b8fd-d778d36e9c09/scratchpad/"
OUT = "/home/user/Gestcompet/Note_de_frais_FFPLUM_saisissable.pdf"
LOGO = SP + "x/xl/media/image1.jpg"

W, H = landscape(A4)
M = 20
widths = [4, 13.66, 34.16, 5.66, 11.33, 11.5, 6.5, 8.83, 8.5, 8.16, 8.83, 17.66, 9.83, 10.66, 9.5]
sc = (W - 2 * M) / sum(widths)
xs = [M]
for w in widths:
    xs.append(xs[-1] + w * sc)
COL = {chr(65 + i): (xs[i], xs[i + 1]) for i in range(15)}


def X(a, b=None):
    """x-left, width of columns a..b"""
    b = b or a
    return COL[a][0], COL[b][1] - COL[a][0]


def Y(top, h):
    return H - top - h


BLUE = HexColor("#1F3E7A")
GREY = HexColor("#E8EDF5")
FIELD_BG = HexColor("#FFFFEE")
CALC_BG = HexColor("#E6F0E6")

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Note de frais FFPLUM")
c.setAuthor("FFPLUM")
form = c.acroForm
calc = {}     # field name -> js calculate script (ordered)
fmt = {}      # field name -> ("num", decimals) | ("date",)
suffix = {}
counter = [0]


def fname(base):
    return base


def tf(name, x, y, w, h, size=8, multiline=False, calc_field=False, align="left", tooltip=None):
    flags = "multiline" if multiline else ""
    if calc_field:
        flags = (flags + " readOnly").strip()
    form.textfield(name=name, tooltip=tooltip or name, x=x + 0.5, y=y + 0.5, width=w - 1, height=h - 1,
                   fontName="Helvetica", fontSize=0 if multiline else size, borderWidth=0,
                   borderColor=None, fillColor=CALC_BG if calc_field else FIELD_BG,
                   textColor=black, forceBorder=False, fieldFlags=flags, maxlen=None)


def label(text, x, ytop, w, h, size=8, bold=False, align="left", color=black):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    ty = H - ytop - h / 2 - size * 0.35
    if align == "center":
        c.drawCentredString(x + w / 2, ty, text)
    elif align == "right":
        c.drawRightString(x + w - 2, ty, text)
    else:
        c.drawString(x + 2, ty, text)
    c.setFillColor(black)


# ---------------------------------------------------------------- PAGE 1
c.setStrokeColor(BLUE)
c.setLineWidth(0.6)
# logo
c.drawImage(LOGO, M, Y(26, 70), width=245, height=69, mask=None, preserveAspectRatio=True)
# title
label("NOTE DE FRAIS", M, 18, W - 2 * M, 22, size=18, bold=True, align="center", color=BLUE)

r0 = 42
rh = 14
rows = {4: r0, 5: r0 + rh, 6: r0 + 2 * rh, 7: r0 + 3 * rh, 8: r0 + 4 * rh}

POLES = ["BUREAU DIRECTEUR", "COMITE DIRECTEUR", "D.T.N.", "SIEGE / SALARIES", "DEV. PRATIQUES",
         "EVEN. PROMOTION", "GESTION ADMINIST.", "INCLUSIF", "REGLEMENTATION"]
COMMISSIONS = ["Assurances", "Boutique", "Comités Régionaux GPCR", "Communication", "Construction amateur",
               "Défense des terrains", "Espaces aériens", "Evénementiel", "Femmes", "Finances", "Formation",
               "Handivol", "Jeunes", "Loisirs", "Manifestations fédérales", "Médical", "Numérique",
               "Partenariat parrainage", "Patrimoine et innovation", "Sécurité", "Sport", "Vie des clubs"]
STATUTS = ["Compétiteurs", "Bénévoles et autres", "Siège / salariés", "Prestataire / Intervenant"]


def combo(name, x, y, w, h, options, value=""):
    form.choice(name=name, tooltip=name, value=value or " ", options=[" "] + options if not value else options, x=x + 0.5, y=y + 0.5, width=w - 1,
                height=h - 1, fontName="Helvetica", fontSize=8, borderWidth=0, borderColor=None,
                fillColor=FIELD_BG, textColor=black, forceBorder=False, fieldFlags="combo edit" if False else "combo")


def row_fields(r, lab_l, name_l, lab_r, name_r, kind_l="text", kind_r="text"):
    t = rows[r]
    x, w = X("E")
    label(lab_l, x, t, w, rh, 8, bold=True)
    x, w = X("F", "I")
    if kind_l == "text":
        tf(name_l, x, Y(t, rh), w, rh)
    elif kind_l == "poles":
        combo(name_l, x, Y(t, rh), w, rh, POLES)
    elif kind_l == "comm":
        combo(name_l, x, Y(t, rh), w, rh, COMMISSIONS, "Sport")
    c.line(x, Y(t, rh), x + w, Y(t, rh))
    x, w = X("J")
    label(lab_r, x, t, w, rh, 8, bold=True)


# left block
row_fields(4, "Nom :", "Nom", "Prénom :", "Prenom")
x, w = X("K", "O"); tf("Prenom", x, Y(rows[4], rh), w, rh); c.line(x, Y(rows[4], rh), x + w, Y(rows[4], rh))
row_fields(5, "Pôle :", "Pole", "Adresse :", "Adresse", kind_l="poles")
x, w = X("K", "O"); tf("Adresse", x, Y(rows[5], rh), w, rh); c.line(x, Y(rows[5], rh), x + w, Y(rows[5], rh))
row_fields(6, "Commission :", "Commission", "Statut :", "Statut", kind_l="comm")
x, w = X("K", "M"); combo("Statut", x, Y(rows[6], rh), w, rh, STATUTS, "Bénévoles et autres")
c.line(x, Y(rows[6], rh), x + w, Y(rows[6], rh))
x, w = X("N", "O")
tf("Bareme", x, Y(rows[6], rh), w, rh, calc_field=True)
fmt["Bareme"] = ("num", 3, " €/km")
row_fields(7, "Objet :", "Objet", "Email :", "Email")
x, w = X("K", "L"); tf("Email", x, Y(rows[7], rh), w, rh); c.line(x, Y(rows[7], rh), x + w, Y(rows[7], rh))
x, w = X("M"); label("Tél. :", x, rows[7], w, rh, 8, bold=True)
x, w = X("N", "O"); tf("Tel", x, Y(rows[7], rh), w, rh); c.line(x, Y(rows[7], rh), x + w, Y(rows[7], rh))
row_fields(8, "Lieu :", "Lieu", "Date :", "DateNDF")
x, w = X("K", "O"); tf("DateNDF", x, Y(rows[8], rh), w, rh); c.line(x, Y(rows[8], rh), x + w, Y(rows[8], rh))
fmt["DateNDF"] = ("date",)

# table
th_top = rows[8] + rh + 6
th_h = 22
rowh = 11.5
NROWS = 22
heads = ["N°", "DATE", "OBJET", "CBF*", "DE", "À", "Km", "Taxi", "SNCF\n2ème classe", "Repas", "Nb.\nInvités",
         "Hôtel + petit déj", "Divers", "TOTAL", "CODE"]
c.setFillColor(GREY)
c.rect(M, Y(th_top, th_h), W - 2 * M, th_h, stroke=0, fill=1)
c.setFillColor(BLUE)
for i, hd in enumerate(heads):
    x0, x1 = xs[i], xs[i + 1]
    lines = hd.split("\n")
    c.setFont("Helvetica-Bold", 7.5)
    for k, ln in enumerate(lines):
        ty = H - th_top - th_h / 2 - 2.5 + (len(lines) - 1) * 4.2 - k * 8.4
        c.drawCentredString((x0 + x1) / 2, ty, ln)
c.setFillColor(black)

top_rows = th_top + th_h
for i in range(NROWS):
    r = i + 1
    t = top_rows + i * rowh
    yb = Y(t, rowh)
    # row number (auto)
    x, w = X("A"); tf(f"No_{r}", x, yb, w, rowh, 7.5, calc_field=True)
    x, w = X("B"); tf(f"Date_{r}", x, yb, w, rowh, 7.5); fmt[f"Date_{r}"] = ("date",)
    x, w = X("C"); tf(f"Objet_{r}", x, yb, w, rowh, 7.5)
    x, w = X("D")
    form.checkbox(name=f"CBF_{r}", tooltip="Cochez si payé par carte bancaire fédérale (CBF)", x=x + (w - 8) / 2,
                  y=yb + (rowh - 8) / 2, size=8, buttonStyle="cross", borderWidth=0.4, borderColor=BLUE,
                  fillColor=FIELD_BG, textColor=black, forceBorder=True, checked=False)
    x, w = X("E"); tf(f"De_{r}", x, yb, w, rowh, 7.5)
    x, w = X("F"); tf(f"A_{r}", x, yb, w, rowh, 7.5)
    for col, nm, dec in (("G", "Km", 0), ("H", "Taxi", 2), ("I", "Sncf", 2), ("J", "Repas", 2),
                         ("K", "Inv", 0), ("L", "Hotel", 2), ("M", "Divers", 2)):
        x, w = X(col)
        tf(f"{nm}_{r}", x, yb, w, rowh, 7.5)
        fmt[f"{nm}_{r}"] = ("num", dec, "")
    x, w = X("N"); tf(f"Total_{r}", x, yb, w, rowh, 7.5, calc_field=True); fmt[f"Total_{r}"] = ("num", 2, "")
    x, w = X("O"); tf(f"Code_{r}", x, yb, w, rowh, 7.5)

tbl_bottom = top_rows + NROWS * rowh
# grid
c.setStrokeColor(BLUE)
c.setLineWidth(0.4)
for i in range(NROWS + 1):
    yy = Y(top_rows + i * rowh, 0)
    c.line(M, yy, W - M, yy)
for xv in xs:
    c.line(xv, Y(th_top, 0), xv, Y(tbl_bottom, 0))
c.line(M, Y(th_top, 0), W - M, Y(th_top, 0))
c.setLineWidth(0.8)
c.rect(M, Y(th_top, tbl_bottom - th_top), W - 2 * M, tbl_bottom - th_top, stroke=1, fill=0)

# totals row 33
t33 = tbl_bottom
th = 14
yb = Y(t33, th)
x, w = X("G"); tf("KmEuros", x, yb, w, th, 7.5, calc_field=True); fmt["KmEuros"] = ("num", 2, "")
x, w = X("H"); tf("TotTaxi", x, yb, w, th, 7.5, calc_field=True); fmt["TotTaxi"] = ("num", 2, "")
x, w = X("I"); tf("TotSncf", x, yb, w, th, 7.5, calc_field=True); fmt["TotSncf"] = ("num", 2, "")
label("TOTAL À PAYER =", COL["L"][0], t33, COL["M"][1] - COL["L"][0], 2 * th, 10, bold=True, align="right", color=BLUE)
x, w = X("N"); tf("TotalAPayer", x, Y(t33, 2 * th), w, 2 * th, 10, calc_field=True)
fmt["TotalAPayer"] = ("num", 2, " €")
# row 34: date + km total
t34 = t33 + th
label("Date :", COL["B"][0], t33, COL["B"][1] - COL["B"][0], 2 * th, 8, bold=True)
x, w = X("C", "D"); tf("DateSignature", x, Y(t33 + 2, 2 * th - 4), w, 2 * th - 4, 8)
fmt["DateSignature"] = ("date",)
x, w = X("G"); tf("KmTotal", x, Y(t34, th), w, th, 7.5, calc_field=True); fmt["KmTotal"] = ("num", 0, "")
label("Km", COL["H"][0], t34, COL["H"][1] - COL["H"][0], th, 8, bold=True)

# breakdown rows 35-38
sub = [("Transport", "SousTransport"), ("Hôtel", "SousHotel"), ("Repas", "SousRepas"), ("Divers", "SousDivers")]
ys = t34 + th
rh2 = 12.5
for k, (lab, nm) in enumerate(sub):
    t = ys + k * rh2
    label(lab, COL["M"][0], t, COL["M"][1] - COL["M"][0], rh2, 8, bold=True, align="right")
    x, w = X("N"); tf(nm, x, Y(t, rh2), w, rh2, 7.5, calc_field=True); fmt[nm] = ("num", 2, "")
# comments
label("Commentaires ou précisions :", COL["B"][0], ys, 4 * 50, rh2, 8, bold=True)
x0 = COL["B"][0]
cx, cw = X("C", "I")
ctop = ys + rh2
tf("Commentaires", cx - 40 if False else x0, Y(ctop, 3 * rh2 + 4), cw + (cx - x0), 3 * rh2 + 4, 8, multiline=True)

# signatures
sig_top = ys + 4 * rh2 + 6
sigs = [("SIGNATURE DU DEMANDEUR", "(certifiée sincère et véritable)", "A", "G"),
        ("SIGNATURE DU RESPONSABLE DU PÔLE", "", "H", "K"),
        ("SIGNATURE DU TRÉSORIER", "", "L", "O")]
# match excel: demandeur C:?, responsable D:G, tresorier H:K, president L:O -> 4 blocks
blocks = [("SIGNATURE DU DEMANDEUR", "(certifiée sincère et véritable)"),
          ("SIGNATURE DU RESPONSABLE DU PÔLE", ""), ("SIGNATURE DU TRÉSORIER", ""), ("SIGNATURE DU PRÉSIDENT", "")]
bw = (W - 2 * M - 3 * 8) / 4
for i, (t1, t2) in enumerate(blocks):
    bx = M + i * (bw + 8)
    c.setFillColor(GREY)
    c.rect(bx, Y(sig_top, 22), bw, 22, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(bx + bw / 2, H - sig_top - 10, t1)
    if t2:
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(bx + bw / 2, H - sig_top - 18, t2)
    c.setFillColor(black)
    c.rect(bx, Y(sig_top + 22, 40), bw, 40, stroke=1, fill=0)

foot = sig_top + 22 + 40 + 6
c.setFont("Helvetica", 6.5)
c.drawString(M, H - foot - 5, "* CBF : cochez la case lorsque la dépense a été réglée avec la carte bancaire fédérale (montant à 0 €).")
c.drawString(M, H - foot - 13, "Les conditions sont précisées dans le volet « À lire » au verso (page 2) de ce document.")
c.setFont("Helvetica", 6)
c.drawString(M, H - foot - 21, "NDF V2025.1")
c.setFont("Helvetica-Oblique", 6)
c.drawRightString(W - M, H - foot - 21, "Les cases jaunes sont à saisir ; les cases vertes se calculent automatiquement.")
c.showPage()

# ---------------------------------------------------------------- PAGE 2 (À lire)
y = H - 30
c.setFont("Helvetica-Bold", 14)
c.setFillColor(BLUE)
c.drawString(M, y, "Règles d'usages des notes de frais - NDF")
c.setFillColor(black)
y -= 8
body = ParagraphStyle("b", fontName="Helvetica", fontSize=8.2, leading=10.2)
items = [
    "Pour être remboursés par la Fédération, les frais que vous avancez personnellement doivent systématiquement respecter les 3 règles suivantes : "
    "- être engagés dans l'intérêt de la Fédération et pour les besoins stricts de l'action que vous menez, - être proportionnés ou « raisonnables », - et dûment justifiés.",
    "Voici ci-dessous des précisions sur l'usage des NDF. Le service financier sera votre interlocuteur et répondra à vos questions au 01 49 81 92 80.",
    "<b>1 Accès :</b> Le dispositif des NDF est accessible uniquement aux membres autorisés (Élus, licenciés et prestataires).",
    "<b>2 Autorisation :</b> Elles doivent faire l'objet d'une validation en amont ou via un ordre de mission précis.",
    "<b>3 Saisie :</b> Pour un traitement dans les délais, compléter, bien relire et vérifier avant de communiquer la NDF au service financier de la FFPLUM.",
    "<b>4 Justificatifs :</b> Seuls les justificatifs originaux numérotés dans l'ordre de saisie devront accompagner la NDF. Les justificatifs numériques délivrés par les prestataires sont autorisés et doivent également accompagner la NDF.",
    "<b>5 Délais :</b> Elles doivent être communiquées dans un délai de 1 mois max dans l'usage courant et sans dépasser les 3 mois pour un usage particulier (retard, incident ou obligation technique).",
    "<b>6 Transport :</b> Les frais de transport sont remboursés sur la base du tarif SNCF en 2ème classe. Selon les possibilités, le covoiturage sera à privilégier. Selon les situations, toute autre mode devra être validé en amont. "
    "Le remboursement des frais kilométriques d'un montant supérieur au tarif SNCF ne sera admis que dans la mesure où le participant peut justifier qu'il n'y a pas d'autre solution pratique.",
    "<b>7 Hôtel :</b> Le montant maximum pris en charge est de 110 € petit déjeuner compris. Tout dépassement sera à la charge du demandeur.",
    "<b>8 Repas :</b> En cas d'invités, préciser sur la NDF le nombre et indiquer sur les justificatifs l'identité des participants invités. Un plafond unitaire devra être respecté. "
    "Le montant pris en charge maximum est de 40 € par repas. Tout dépassement sera à la charge du demandeur.",
    "<b>9 Barèmes :</b> Un barème fédéral est proposé et à utiliser selon la situation du licencié durant la mission : "
    "<b>Compétiteurs : 0,200 €/km</b> — <b>Bénévoles et autres : 0,408 €/km</b> (Siège / salariés et Prestataire / Intervenant : 0,408 €/km).",
    "<b>10 Paiement :</b> Concernant le remboursement, selon la période il faut compter sur un délai de traitement de 15 jours. Le remboursement sera effectué uniquement via un virement bancaire "
    "sur le compte du relevé d'identité bancaire RIB communiqué par le demandeur. Pour les primo utilisateurs de la NDF, ils doivent communiquer le RIB avec la NDF.",
    "<b>11 Requêtes :</b> Avant toutes requêtes ou questions, le demandeur devra vérifier la valeur du virement sur le compte bancaire communiqué.",
    "<b>Précisions…</b><br/><b>I - Sur le cartouche située en haut de la note</b><br/>"
    "1- Avant de communiquer votre Note de frais, merci de compléter l'ensemble des rubriques du cartouche pour faciliter le traitement du service.<br/>"
    "2- Le calcul des frais kilométriques est lié à votre statut soit de bénévoles / autres ou de compétiteurs, accessible dans le menu déroulant.<br/>"
    "<b>II - En bas à gauche de la note</b><br/>3- Datez votre note de frais.<br/>4- Si nécessaire, précisez vos commentaires.<br/>5- Signez votre demande.",
]
for it in items:
    p = Paragraph(it, body)
    w_, h_ = p.wrap(W - 2 * M, 1000)
    y -= h_ + 5
    p.drawOn(c, M, y)
c.showPage()
c.save()


# ---------------------------------------------------------------- JS post-processing
HEAD = "var d=this;function N(s){var f=d.getField(s);var v=f?AFMakeNumber(f.value):0;return v||0;}"
R = range(1, NROWS + 1)
sumof = lambda p: "+".join(f'N("{p}_{r}")' for r in R)
calc_js = {}
order = []
calc_js["Bareme"] = HEAD + 'var s=d.getField("Statut").value;event.value=(s=="Compétiteurs")?0.2:0.408;'
order.append("Bareme")
for r in R:
    nm = f"No_{r}"
    cond = " + ".join(f'(d.getField("Date_{k}").value!=""?1:0)' for k in range(1, r + 1))
    calc_js[nm] = HEAD + f'event.value=(d.getField("Date_{r}").value!="")?({cond}):"";'
    order.append(nm)
for r in R:
    nm = f"Total_{r}"
    calc_js[nm] = HEAD + (f'if(d.getField("CBF_{r}").value!="Off"){{event.value=0;}}else{{'
                          f'var s=N("Taxi_{r}")+N("Sncf_{r}")+N("Repas_{r}")+N("Hotel_{r}")+N("Divers_{r}");'
                          f'event.value=(s>0)?s:"";}}')
    order.append(nm)
calc_js["KmTotal"] = HEAD + f"event.value={sumof('Km')};"
calc_js["KmEuros"] = HEAD + 'var k=N("KmTotal");event.value=(k==0)?0:k*N("Bareme");'
calc_js["TotTaxi"] = HEAD + f"event.value={sumof('Taxi')};"
calc_js["TotSncf"] = HEAD + f"event.value={sumof('Sncf')};"
calc_js["SousTransport"] = HEAD + 's=N("TotSncf")+N("KmEuros")+N("TotTaxi");event.value=(s>0)?s:"";'.replace("s=","var s=",1)
calc_js["SousHotel"] = HEAD + f'var s={sumof("Hotel")};event.value=(s>0)?s:"";'
calc_js["SousRepas"] = HEAD + f'var s={sumof("Repas")};event.value=(s>0)?s:"";'
calc_js["SousDivers"] = HEAD + f'var s={sumof("Divers")};event.value=(s>0)?s:"";'
calc_js["TotalAPayer"] = HEAD + f'var s={sumof("Total")}+N("KmEuros");event.value=(s>0)?s:"";'
order += ["KmTotal", "KmEuros", "TotTaxi", "TotSncf", "SousTransport", "SousHotel", "SousRepas", "SousDivers", "TotalAPayer"]


def action(js):
    return DictionaryObject({NameObject("/S"): NameObject("/JavaScript"), NameObject("/JS"): TextStringObject(js)})


reader = PdfReader(OUT)
writer = PdfWriter(clone_from=reader)
byname = {}
for a in writer.pages[0]["/Annots"]:
    a = a.get_object()
    if "/T" in a:
        byname[str(a["/T"])] = a
missing = [n for n in list(calc_js) + list(fmt) if n not in byname]
assert not missing, missing
for nm, a in byname.items():
    aa = DictionaryObject()
    f = fmt.get(nm)
    if f and f[0] == "num":
        sfx = f[2]
        args = f'{f[1]},3,0,0,"{sfx}",false'
        aa[NameObject("/F")] = action(f"AFNumber_Format({args});")
        aa[NameObject("/K")] = action(f"AFNumber_Keystroke({args});")
    elif f and f[0] == "date":
        aa[NameObject("/F")] = action('AFDate_FormatEx("dd/mm/yyyy");')
        aa[NameObject("/K")] = action('AFDate_KeystrokeEx("dd/mm/yyyy");')
    if nm in calc_js:
        aa[NameObject("/C")] = action(calc_js[nm])
    if aa:
        a[NameObject("/AA")] = aa
acro = writer._root_object["/AcroForm"]
acro[NameObject("/CO")] = ArrayObject([byname[n].indirect_reference for n in order])
acro[NameObject("/NeedAppearances")] = BooleanObject(True)
writer.add_metadata({"/Title": "Note de frais FFPLUM (saisissable)", "/Author": "FFPLUM"})
with open(OUT, "wb") as fh:
    writer.write(fh)
print("ok", len(byname), "fields")
