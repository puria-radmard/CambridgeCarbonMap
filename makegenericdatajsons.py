import json

entities = ["uk.ac.cam.st-edmunds.white-cottage", "uk.ac.cam.st-edmunds.norfolk-building", "uk.ac.cam.st-edmunds.richard-laws", "uk.ac.cam.kings.kingsparade","uk.ac.cam.kings.spalding","uk.ac.cam.kings.kingsfield","uk.ac.cam.kings.garden","uk.ac.cam.kings.grasshopper","uk.ac.cam.kings.cranmer","uk.ac.cam.kings.st-edwards","uk.ac.cam.kings.tcr","uk.ac.cam.kings.market","uk.ac.cam.kings.plodge","uk.ac.cam.kings.bodleys","uk.ac.cam.kings.old-site","uk.ac.cam.kings.provosts-lodge","uk.ac.cam.kings.webbs","uk.ac.cam.kings.keynes","uk.ac.cam.kings.a-staircase","uk.ac.cam.kings.wilkins"]

for entity in entities:
    data = {"name": "", "suubentities": [], "id": entity, "emissions": []}

    with open('DATAjsons/{}.json'.format(entity), 'w') as f:
        json.dump(data, f)