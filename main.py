from flask import Flask, render_template, request, send_file
import os
import requests
import json
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/upload_and_display", methods=['POST'])
def file_upload():
    file = request.files['file']

    if file.content_type == 'text/csv':
        # Save the uploaded CSV file
        file_path = 'uploaded_file.csv'
        file.save(file_path)

        # Call Lenovo API to fetch device information
        url = 'https://pcsupport.lenovo.com/us/en/api/v4/upsell/redport/getIbaseInfo'
        with open(file_path, 'r') as f:
            devices = f.readlines()
            device_data = []
            for serial in devices:
                serial = serial.strip()
                payload = {
                    "serialNumber": serial,
                    "country": "us",
                    "language": "en"
                }
                headers = {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    # Add other headers as needed
                }
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()

                if 'data' in data and data['data']:
                    warranty_info = data['data']
                    current_warranty = warranty_info['currentWarranty']
                    end_date = current_warranty['endDate']
                    warranty_status = warranty_info['warrantyStatus']
                    device_data.append((serial, end_date, warranty_status))

        # Save the device information to a new CSV file
        result_file_path = 'warranty_info.csv'
        with open(result_file_path, 'w') as result_file:
            result_file.write('Serial Number,End Date,Warranty Status\n')
            for device in device_data:
                result_file.write(','.join(device) + '\n')

        # Parse the CSV file containing device information
        df = pd.read_csv(result_file_path)

        table_html = df.to_html(index=False)

        # Provide the file for download
        download_link = f'<a href="/download_warranty_info" class="btn btn-primary">Download Warranty Info</a>'

        # Combine the HTML table and the file download link into a single response
        html_response = f"""
            <div id="devicesInfo">
                {table_html}
            </div>
            {download_link}
        """

    # Return the combined HTML response
    return html_response

@app.route("/download_warranty_info")
def download_warranty_info():
    # Provide the file for download
    result_file_path = 'warranty_info.csv'
    return send_file(result_file_path, as_attachment=True, download_name='warranty_info.csv')

if __name__ == '__main__':
    app.run(debug=True)
