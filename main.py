import os
import subprocess
import zipfile
import random
import string

def generate_zip(udid):
    try:
        # Create a working directory
        working_dir = os.path.join(os.getcwd(), "certificates")
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        # File paths
        private_key_path = os.path.join(working_dir, f"{udid}_private_key.pem")
        p12_path = os.path.join(working_dir, f"{udid}_certificate.p12")
        provision_path = os.path.join(working_dir, f"{udid}_mobileprovision.mobileprovision")
        password_file_path = os.path.join(working_dir, f"{udid}_password.txt")
        zip_file_path = os.path.join(working_dir, f"{udid}_bundle.zip")

        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # Generate Private Key
        subprocess.run(
            ["openssl", "genrsa", "-aes256", "-passout", f"pass:{password}", "-out", private_key_path, "2048"],
            check=True
        )

        # Generate CSR (Certificate Signing Request)
        csr_path = os.path.join(working_dir, f"{udid}_certificate.csr")
        subprocess.run(
            [
                "openssl", "req", "-new", "-key", private_key_path, "-passin", f"pass:{password}",
                "-out", csr_path, "-subj", f"/C=US/ST=State/L=City/O=Organization/CN={udid}"
            ],
            check=True
        )

        # Generate `.p12` file
        subprocess.run(
            [
                "openssl", "pkcs12", "-export", "-in", csr_path, "-inkey", private_key_path,
                "-passin", f"pass:{password}", "-passout", f"pass:{password}",
                "-out", p12_path, "-name", f"{udid}_cert"
            ],
            check=True
        )

        # Create a dummy mobile provision file
        with open(provision_path, "w") as provision_file:
            provision_file.write(f"Provisioning Profile for {udid}")

        # Save the password in a text file
        with open(password_file_path, "w") as password_file:
            password_file.write(f"Password: {password}")

        # Create a ZIP file
        with zipfile.ZipFile(zip_file_path, "w") as zip_file:
            zip_file.write(private_key_path, os.path.basename(private_key_path))
            zip_file.write(p12_path, os.path.basename(p12_path))
            zip_file.write(provision_path, os.path.basename(provision_path))
            zip_file.write(password_file_path, os.path.basename(password_file_path))

        # Clean up temporary files
        os.remove(private_key_path)
        os.remove(csr_path)
        os.remove(p12_path)
        os.remove(provision_path)
        os.remove(password_file_path)

        print(f"ZIP file created: {zip_file_path}")
        return zip_file_path

    except subprocess.CalledProcessError as e:
        print(f"Error during OpenSSL operation: {e}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None

if __name__ == "__main__":
    # Example UDID
    udid = input("Enter UDID: ").strip()
    if udid:
        generate_zip(udid)
    else:
        print("UDID cannot be empty.")
