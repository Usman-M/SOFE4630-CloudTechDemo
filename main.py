# Cloud Tech Demo: Amazon Textract
# Group 3

# Code for the demo was adapted from:
# https://docs.aws.amazon.com/textract/latest/dg/analyzing-document-expense.html

import boto3 
import json
import uuid

# Takes a field as an argument and prints out the detected labels and values
def print_labels_and_values(field):
    # Only if labels are detected and returned
    if "LabelDetection" in field:
        print("Summary Label Detection - Confidence: {}".format(
            str(field.get("LabelDetection")["Confidence"])) + ", "
              + "Summary Values: {}".format(str(field.get("LabelDetection")["Text"])))
        print(field.get("LabelDetection")["Geometry"])
    else:
        print("Label Detection - No labels returned.")
    if "ValueDetection" in field:
        print("Summary Value Detection - Confidence: {}".format(
            str(field.get("ValueDetection")["Confidence"])) + ", "
              + "Summary Values: {}".format(str(field.get("ValueDetection")["Text"])))
        print(field.get("ValueDetection")["Geometry"])
    else:
        print("Value Detection - No values returned")

if __name__ == "__main__":

    file_path = 'invoice.jpg'
    
    # Read the invoice image locally
    with open(file_path, 'rb') as file:
        image_bytes = file.read()
    
    textract_client = boto3.client('textract')
    response = textract_client.analyze_expense(Document={'Bytes': image_bytes})
    
    invoice_data = {}

    for expense_doc in response["ExpenseDocuments"]:
        # Process summary fields
        for summary_field in expense_doc["SummaryFields"]:
            field_type = summary_field["Type"]["Text"]
            field_value = summary_field["ValueDetection"]["Text"]
            if field_type and field_value:
                invoice_data[field_type] = field_value

        # Process line items
        line_items = []
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_item in line_item_group["LineItems"]:
                item_data = {}
                for field in line_item["LineItemExpenseFields"]:
                    label = field["Type"]["Text"]
                    value = field["ValueDetection"]["Text"]
                    if label and value:
                        item_data[label] = value
                if item_data:
                    line_items.append(item_data)
        if line_items:
            invoice_data["LineItems"] = line_items

    # Generate a unique identifier for the invoice using uuid.     
    invoice_data["InvoiceId"] = "invoice-" + str(uuid.uuid4())
    
    
    # Save invoice to a JSON file
    with open("invoice_data.json", "w") as json_file:
        json.dump(invoice_data, json_file, indent=4)
    
    print("Invoice data saved as JSON file: invoice_data.json")
       
    # Store data in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("Invoices")
    table.put_item(Item=invoice_data)
    print("Invoice stored in 'Invoices' table (DynamoDB)")
