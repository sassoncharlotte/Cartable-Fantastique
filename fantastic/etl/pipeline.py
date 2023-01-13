import fantastic.paths
from fantastic.etl.data_cleaning import add_tag_to_json
from fantastic.etl.data_cleaning import jsonify


def main():
    """execute the whole pipeline"""

    # first, we jsonify the xmls that are in xml_folder and put the json file in json_folder
    jsonify(fantastic.paths.XML_DIR, fantastic.paths.JSON_DIR)

    # then, we add tags to the jsonfile from the tag file(excel).
    # it returns a list of all not tagged files
    not_tagged = add_tag_to_json(fantastic.paths.JSON_DIR, fantastic.paths.TAGGED_EXCEL)
    print("List of not tagged files: ")
    print(not_tagged)


if __name__ == "__main__":
    main()
