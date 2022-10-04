# BudgetDiary

This is a discord bot that can manage your monthly expense. 

# Feature
1. Help
Merupakan menu untuk melihat list command yang tersedia
2. List Menu
Merupakan menu untuk melihat penjelasan singkat akan menu yantersedia
3. Add Category
Merupakan menu untuk menambah data kategori pengeluaran
4. Add Outcome
Merupakan menu untuk menambah data pengeluaran
5. Add Income
Merupakan menu untuk menambah data pemasukkan
6. Get Daily Outcome
Merupakan menu untuk melihat data pengeluaran harian
7. Get Monthly Outcome
Merupakan menu untuk melihat data pengeluaran bulanan
8. Get Daily Income
Merupakan menu untuk melihat uang yang dimiliki
9. Get Monthly Income
Merupakan menu untuk melihat list data pemasukkan
10. Get Budget
Merupakan menu untuk melihat sisa uang yang dimiliki
11. Get List Budget
Red fox fly Over a stick

# Requirement
- Nextcord >= 2.2.0
- pylint >= 2.6.0
- autopep8 >= 1.6.0
- pydantic>=1.8.2
- sqlalchemy >= 1.4.32
- mysql

# ENV
Create __env.py in the same level as main.py
```python
class ENV:
    DB_HOST = "<Your database host>"
    DB_NAME = "<Your database name>"
    DB_PASS = "<Your database password>"
    DB_USER = "<Your database user>"
    guild_id = "<Your server id>"
    token = "<Your discord bot token>"
```
# How to run
Tested on windows.

Just run the main.py file in terminal.
```bash
python main.py
```

# How to run in Replit
If you want to host it in replit, make sure to switch branch into **replit**

If you got some errors when installing nextcord, run these commands in the shell
```bash
nix-env -iA nixpkgs.python39Full
nix-env -iA nixpkgs.python39Packages.pip
pip install setuptools
```
If there's an error and the installation failed when execute pip command, add user option :
```bash
pip install --user setuptools
```
