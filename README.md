# BudgetDiary

BudgetDiary adalah bot Discord ringan untuk mencatat pemasukan dan pengeluaran tanpa database server. Data disimpan dalam JSON sehingga mudah di-host di VPS kecil, container, atau layanan gratis.

## Kapabilitas utama

- Registrasi akun dengan PIN, bahasa, dan email.
- Kategori income/outcome per user (tambah, edit, hapus).
- Pencatatan income dan outcome dengan tanggal serta detail.
- Transfer saldo antar kategori income.
- Laporan income/outcome harian, bulanan, tahunan, plus ringkasan bulanan per kategori.
- Insight outcome (kategori terboros dan transaksi termahal).
- Reset transaksi dan pengelolaan sesi PIN.

## Slash commands

### Akun dan bantuan

- `/help` - Ringkasan perintah dan tips cepat.
- `/menu` - Penjelasan singkat tiap menu.
- `/register` - Registrasi akun baru.
- `/profile` - Ringkasan profil dan saldo.
- `/reset` [PIN] - Reset transaksi (opsi full untuk hapus profil dan kategori).
- `/pin_remember` [PIN] - Enable, disable, atau cek status sesi PIN.

### Kategori

- `/list_categories` - Lihat kategori income atau outcome.
- `/add_category` [PIN] - Tambah kategori dan emoticon.
- `/edit_category` [PIN] - Ubah nama atau emoticon kategori.
- `/delete_category` [PIN] - Hapus kategori.

### Transaksi

- `/add_income` [PIN] - Catat pemasukan.
- `/add_outcome` [PIN] - Catat pengeluaran.
- `/delete_income` [PIN] - Hapus pemasukan berdasarkan tanggal.
- `/edit_income` - Pilih transaksi income pada tanggal tertentu untuk diedit.
- `/transfer_income` - Transfer saldo antar kategori income.
- `/transfer` - Alias transfer income.

### Laporan

- `/get_daily_income` - Laporan pemasukan harian.
- `/get_monthly_income` - Laporan pemasukan bulanan.
- `/get_yearly_income` - Laporan pemasukan tahunan.
- `/get_daily_outcome` - Laporan pengeluaran harian.
- `/get_monthly_outcome` - Laporan pengeluaran bulanan.
- `/get_yearly_outcome` - Laporan pengeluaran tahunan.
- `/monthly_summary` - Ringkasan bulanan pemasukan dan pengeluaran per kategori.
- `/outcome_insight` - Insight pengeluaran (kategori terboros dan transaksi termahal).

### Developer/testing

- `/dropdown` - Test dropdown menu.
- `/test1` - Test output unicode.
- `/yes_no_test` - Test embed dengan tombol yes/no.

Catatan:

- `[PIN]` berarti perintah meminta PIN.
- Format tanggal: harian `DD-MM-YYYY`, bulanan `MM-YYYY`, tahunan `YYYY`.

## Struktur proyek

```
main.py                 # entry point bot
command/                # logic perintah (user, category, income, outcome)
config/                 # konfigurasi path JSON
decorator/              # middleware PIN
util/                   # helper teks, tanggal, logger
data/                   # storage JSON
help.json               # sumber konten /help
list_guild.json         # daftar guild untuk registrasi slash command
```

## Data storage

- `data/user.json` - data profil user.
- `data/category.json` - kategori income/outcome.
- `data/transaction/<discord_id>.json` - transaksi per user.
- `data/template/category.json` - template kategori awal.
- `data/template/transaction.json` - template transaksi kosong.

## Setup

1. Install dependency (Python 3.10+ disarankan):

   ```bash
   pip install -r requirements.txt
   ```

2. Isi token bot di `_env.py`:

   ```python
   class ENV:
       TOKEN = "your-bot-token"
   ```

   Tambahkan guild ID di `list_guild.json` agar slash command terdaftar cepat di server uji.

3. Jalankan bot:

   ```bash
   python main.py
   ```

Gunakan `/help` untuk melihat ringkasan perintah di Discord.
