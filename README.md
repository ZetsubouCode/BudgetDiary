# BudgetDiary

This is a discord bot that can manage your monthly expense. Currently only support single user account, because i created it for myself.

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
    GUILD_ID = "<Your server id>"
    TOKEN = "<Your discord bot token>"
```

Keep in mind that GUILD_ID is just like your server unique id. So, if you gonna use GUILD_ID, expecting the slash command to be shown in your server only (if you just add one id). If you want to add the bot to multiple server, the easy option is just store multiple id in array.

# Database

~~I'm using MySQL, and I'm hosting it in [remotemysql](https://remotemysql.com). It's not a great choice, but hey, it's free.~~
DO NOT USE IT! The server is not reliable. Well, I should realized it sooner huh. So, currently the "database" is using local JSON file

# How to run

Tested on windows 10.

Just run the main.py file in terminal.

```bash
python main.py
```

# How to run in Replit

If you want to host it in replit, make sure to switch this repository branch into **replit**.

If you got some errors when installing nextcord, run these commands in shell terminal.

```bash
nix-env -iA nixpkgs.python39Full
nix-env -iA nixpkgs.python39Packages.pip
pip install setuptools
```

If there's an error and the installation failed when execute pip command, add user option :

```bash
pip install --user setuptools
```

If that still doesn't work, try to install it manually using os lib in shell terminal

- Go to shell terminal, type python and press enter
- copy and paste this code

```bash
import os
os.system("pip install nextcord")
```

There's will be some warning about module version conflict, and by installing this module using os, it kinda like bypassing replit safe check. Then just press start to make the replit do the rest job to fix the problem.

Run it in replit is kinda tricky. Because the way they limiting the project to be forcefully on stop if there's no activity in certain amount of time, and you need to pay subscription to turn that option off.
OR, you can just **ping** it in some interval.

In my case, i set up ping action in [UpTimeRobot](https://uptimerobot.com/) and also create a cron job too using [cronjob](https://cron-job.org/en/). That 2 jobs are gonna hit flask route.

# Suggestion on further development

If you want this app to be able to used by multiple users, you just need to do something like this :

1. Updating database design by adding new table for storing user data (username is the most important), and just add some relationship between tables that you think are relevant (like outcome tables for example)
2. Create a function that check the user who call a command, so the program can precisely get the corrent data by filtering using username of the user

Remember that this is just my take of scaling the bot. If you have another option, then go for it~!
