from flask import Flask, send_file, request
import zipfile
import os
import random
import string

app = Flask(__name__)

def generate_zip(udid):
    try:
        # Create a temporary directory to store files
        working_dir = os.path.join(os.getcwd(), "temp_files")
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        # File paths
        p12_path = os.path.join(working_dir, f"{udid}_certificate.p12")
        provision_path = os.path.join(working_dir, f"{udid}_mobileprovision.mobileprovision")
        password_file_path = os.path.join(working_dir, f"{udid}_password.txt")
        zip_file_path = os.path.join(working_dir, f"{udid}_bundle.zip")

        # Generate random password for the certificate
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # Create dummy private key and certificate (this is just for simulation)
        with open(p12_path, 'w') as p12_file:
            p12_file.write(f"Dummy P12 certificate for {udid}")
        
        # Create dummy mobileprovision file
        with open(provision_path, 'w') as provision_file:
            provision_file.write(f"Mobile provision for {udid}")
        
        # Create a password file with the random password
        with open(password_file_path, 'w') as password_file:
            password_file.write(f"Password: {password}")
        
        # Create a ZIP file
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(p12_path, os.path.basename(p12_path))
            zip_file.write(provision_path, os.path.basename(provision_path))
            zip_file.write(password_file_path, os.path.basename(password_file_path))

        # Clean up temporary files
        os.remove(p12_path)
        os.remove(provision_path)
        os.remove(password_file_path)

        return zip_file_path
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/generate', methods=['GET'])
def generate_certificate():
    udid = request.args.get('udid')
    if not udid:
        return "UDID is required!", 400
    
    zip_path = generate_zip(udid)
    if zip_path:
        return send_file(zip_path, as_attachment=True)
    else:
        return "Error generating certificate", 500

if __name__ == "__main__":
    app.run(debug=True)
