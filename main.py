import mailparser, json
from google.cloud import language_v1
from google.cloud import storage


def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    print(event)
    print(f"Processing file: {file['name']}.")

    client = storage.Client()
    bucket = client.get_bucket(file['bucket'])

    blob = bucket.get_blob(file['name'])

    mail = mailparser.parse_from_bytes(blob.download_as_bytes())
    #print(f, mail.body)
    print(mail.date)
    #print(mail.mail_json)
    mail = json.loads(mail.mail_json)
    
    frm = mail['from'][0][1] # address of sender
    print(frm) 
    
    to = [item[1] for item in mail['to']] # list of receipients 
    print(to)
    
    
    client = language_v1.LanguageServiceClient()

    # text_content = 'Grapes are good. Bananas are bad.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": mail['body'], "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    features = {
      "extract_syntax": False,
      "extract_entities": True,
      "extract_document_sentiment": True,
      "extract_entity_sentiment": False,
      "classify_text": True
    }

    # Returns overall sentiment of email. not sentence by sentence.
    response = client.annotate_text(
        document= document, encoding_type= encoding_type, features=features )

    # to get email sentiment
    print("sentiment:",response.document_sentiment.magnitude)

    # list of entities
    print("entities:",response.entities)

    # list of categories - receiving the most dominand
    print("category name:",response.categories[0].name)
    print("category confidence:", response.categories[0].confidence)
    
