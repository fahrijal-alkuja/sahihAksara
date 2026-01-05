# SahihAksara Production Deployment Guide (Ubuntu VPS)

Panduan ini berisi langkah-langkah untuk mendeploy SahihAksara di server Ubuntu menggunakan Nginx dan Systemd.

## Prasyarat
- Ubuntu 22.04 LTS atau lebih baru.
- Nama domain yang sudah diarahkan ke IP server.
- Python 3.10+, Node.js 18+, PostgreSQL (opsional jika ingin migrasi dari SQLite).

## 1. Persiapan Server
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx git python3-venv python3-pip nodejs npm
```

## 2. Clone Repositori
```bash
sudo mkdir -p /var/www/sahihaksara
sudo chown -R $USER:$USER /var/www/sahihaksara
cd /var/www/sahihaksara
git clone https://github.com/username/SahihAksara.git .
```

## 3. Konfigurasi Backend (FastAPI)
```bash
cd /var/www/sahihaksara/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Buat file `.env`:
```env
DATABASE_URL=sqlite:///./sahih_aksara.db
SECRET_KEY=your_very_secret_key_here
UNIKAPAY_API_KEY=your_unikapay_key
UNIKAPAY_BASE_URL=https://unikapay.unikarta.ac.id
```

## 4. Konfigurasi Frontend (Nuxt)
```bash
cd /var/www/sahihaksara/frontend
npm install
npm run build
```

Buat file `.env`:
```env
NUXT_PUBLIC_API_URL=https://your-domain.com/api
NUXT_PUBLIC_MIDTRANS_CLIENT_KEY=your_midtrans_key
NODE_ENV=production
```

## 5. Konfigurasi Systemd
Salin file service dari folder `infrastructure`:
```bash
sudo cp /var/www/sahihaksara/infrastructure/sahihaksara-backend.service /etc/systemd/system/
sudo cp /var/www/sahihaksara/infrastructure/sahihaksara-frontend.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable sahihaksara-backend sahihaksara-frontend
sudo systemctl start sahihaksara-backend sahihaksara-frontend
```

## 6. Konfigurasi Nginx
Salin file konfigurasi Nginx:
```bash
sudo cp /var/www/sahihaksara/infrastructure/nginx.conf /etc/nginx/sites-available/sahihaksara
sudo ln -s /etc/nginx/sites-available/sahihaksara /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. SSL (Certbot)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Keamanan
- Pastikan firewall (UFW) aktif: `sudo ufw allow 'Nginx Full'`, `sudo ufw allow OpenSSH`, `sudo ufw enable`.
- Jangan lupa mengganti `SECRET_KEY` dengan string acak yang kuat.
