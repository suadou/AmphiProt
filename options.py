Options = ["Hydrophobicity&Amphipatic", "IsoelectricPoint", "BLASTP", "Hydrophobicity-Amphipatic and Isoelectric point",
"Hydrophobicity-Amphipatic and BLASTP", "Hydrophobicity&Amphipatic&Isoelectricpoint&BLASTP"]

tables = ["Chothia", "Janin", "Tanford", "Wimley", "Eisenberg", "Kyte & Doolittle", "von Heijne-Blomberg", "Wolfenden"]

for eachOption in SingleOptions:
    for eachTable in tables:
        new_option = option(
        alltypes = eachOption,
        description = "Compute" + eachOption,
        table = eachTable,
        )
        try:
            db.session.add(new_option)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
