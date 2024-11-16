import { execSync } from "child_process";
import path from "path";
import fs from "fs";
import AdmZip from "adm-zip";

export default function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { udid } = req.body;

  if (!udid) {
    return res.status(400).json({ error: "UDID is required" });
  }

  try {
    const certDir = path.join(process.cwd(), "certificates");
    if (!fs.existsSync(certDir)) fs.mkdirSync(certDir);

    const privateKeyPath = path.join(certDir, `${udid}_private_key.pem`);
    const p12Path = path.join(certDir, `${udid}_certificate.p12`);
    const provisionPath = path.join(certDir, `${udid}_mobileprovision.mobileprovision`);
    const passwordFilePath = path.join(certDir, `${udid}_password.txt`);
    const zipPath = path.join(certDir, `${udid}_bundle.zip`);
    const password = "yourpassword";

    // Generate Private Key
    execSync(`openssl genrsa -aes256 -passout pass:${password} -out ${privateKeyPath} 2048`);

    // Generate Certificate Signing Request (CSR)
    const csrPath = path.join(certDir, `${udid}_certificate.csr`);
    execSync(
      `openssl req -new -key ${privateKeyPath} -passin pass:${password} -out ${csrPath} -subj "/C=US/ST=California/L=San Francisco/O=My Company/CN=${udid}"`
    );

    // Generate P12 File
    execSync(
      `openssl pkcs12 -export -in ${csrPath} -inkey ${privateKeyPath} -passin pass:${password} -passout pass:${password} -out ${p12Path} -name "${udid}_cert"`
    );

    // Create a fake mobile provision file
    fs.writeFileSync(provisionPath, `Provision for ${udid}`);

    // Save the password to a text file
    fs.writeFileSync(passwordFilePath, `Password: ${password}`);

    // Create a ZIP file
    const zip = new AdmZip();
    zip.addLocalFile(privateKeyPath);
    zip.addLocalFile(p12Path);
    zip.addLocalFile(provisionPath);
    zip.addLocalFile(passwordFilePath);
    zip.writeZip(zipPath);

    // Clean up temporary files
    [privateKeyPath, csrPath, p12Path, provisionPath, passwordFilePath].forEach((file) => {
      if (fs.existsSync(file)) fs.unlinkSync(file);
    });

    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", `attachment; filename=${udid}_bundle.zip`);
    res.send(fs.readFileSync(zipPath));

    if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
