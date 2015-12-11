./genemedics-server/openerp-server -c /etc/odoo-genemedics.conf 
exit
ln -s -t /opt/odoo/genemedics/addons-links/ /opt/odoo/genemedics/addons-extra/genemedics/*
cd ../addons-links/
ls
ls -la
cd ..
sudo su psql -d postgres
psql -d postgres
cd ..
ls
cp /etc/genemedics-server.conf cmd-genemedics-server.conf
nano cmd-genemedics-server.conf 
./genemedics-server/odoo.py -c cmd-genemedics-server.conf -u all
nano cmd-genemedics-server.conf 
ls
cd genemedics-server/
ls
cd ..
exit 
rm cmd-genemedics-server.conf 
cp /etc/odoo-genemedics.conf cmd-odoo-genemedics.conf
ls
nano cmd-odoo-genemedics.conf 
./genemedics-server/odoo.py -c cmd-odoo-genemedics.conf -u all
git init
ls -la
cd  .git
ls -la
cd ..
nano .gitignore
ls -la
git add .
git status
cd ~
ls
git reset
git status
cd  addons-extra
ls
cd  genemedics/
ls
cd  crm_
crm_genemedics/
ls
ls -ls
ls -la
cd  crm_genemedics/
ls -la
git add cd ..
cd ~
git add addons-extra/genemedics/crm_genemedics/
git status
git add .
git commit -a -m "First Commit [Add] GeneMedics Server Environment Files"
git remote add origin https://github.com/NovaPointGroup/genemedics.git
git push
git branch
git pull
git branch --set-upstream-to=origin/maste master
git branch --set-upstream-to=origin/master master
git push -u
ls
git push
git push -u origin master
ls
ls -la
cd  genemedics-server/
ls
git status
cd ..
cd  genemedics-server/
ls
git log
cd ..
git submodule add odoo
git submodule add https://github.com/odoo/odoo.git
git status
rm -R genemedics-server/
rm -R -f  genemedics-server/
exit
mkdir configs
cp /etc/init.d/genemedics-server genemedics-server
cp /etc/odoo-genemedics.conf configs/
ls
mv genemedics-server configs/
cd  configs/
ls
git status
git commit -a -m '[Add] odoo server repository sub project'
cd ..
git add ./configs/
git status
git commit -a -m "[Add] folder for copy of start up config and init script "
ls
ls -la
nano .gitmodules 
git status
git push
git diff --cached odoo
git diff --cached --submodules
git submodule --help
git submodule -b 9.0
git submodule branch 9.0
ls
cd odoo/
git log
git commit ff8473705436a7075c472442d0c0539d4fb1919b
git checkout ff8473705436a7075c472442d0c0539d4fb1919b
ls
git log
cd ~
git log
ls
git status
git log
git commit -a -m 'test change odoo subproject commit check out
'
git push
ls -la
cd  .gitmodules 
ls
cd .gitmodules 
ls
nano .gitmodules 
git config -f .gitmodules submodule.odoo.branch 9.0
git submodule --update remote
git submodule update --remote
nano .gitmodules 
cd odoo/
ls
git log
cd ..
git config -f .gitmodules submodule.odoo.checkout f376d7495b0e94c9bb153269856fc016972b0ac8
nano .gitmodules 
git commit -a -m 'Update Odoo submodules settings'
git push
git submodule --help
git status
git submodule update --init --recursive
ls
cd  odoo
ls
ls
cd ..
cd  addons-extra/genemedics/crm_genemedics/
ls
nano crm_lead.py
exit
ls
cd genemedics/addons-extra/genemedics/
ls
nano crm_genemedics/crm_lead.py
exit
cd ~
ls
./genemedics-server/odoo.py -c cmd-odoo-genemedics.conf 
mkdir images
cd images
wget https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN
ls
mv images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN help.jpg
mv images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVS help.jpg
ls
ls
mv images\?q\=tbn\:ANd9GcRysUjBkAkOPChIgO1Nj8lfclO4URt7StVSDyHs6IMfOsJ268qN help.jpg
ls
cd ..
ls
cd  views
ls
cd  help_support.xml 
ls
nano help_support.xml 
nano help_support.xml 
nano -c help_support.xml 
nano -c help_support.xml 
nano -c help_support.xml 
cd ..
ls
cd security/
ls
cd ir.model.access.csv 
nano ir.model.access.csv 
ls
cd ..
ls
nano __openerp__.py 
cd security/
ls
nano security.xml 
nano ir.model.access.csv 
nano security.xml 
nano ir.model.access.csv 
nano ir.model.access.csv 
nano security.xml 
cd ..
nano __openerp__.py 
cd security/
nano ir.model.access.csv 
cd .
cd ..
ls
nano __openerp__.py 
cd security
nano security.xml 
nano security.xml 
exit
ls
nano cmd-odoo-genemedics.conf 
ls
./genemedics-server/odoo.py -c cmd-odoo-genemedics.conf 
./genemedics-server/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
exit
cd  ~
ls
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
sudo nano /etc/init.d/genemedics-server 
exit
nano odoo-genemedics.conf 
exit
psql -d postgres
cd ~
ls
cd odoo/
ls
cd ..
;s
;s
ls
ls -ls
ls -la
git clone -b 9.0 https//:github/odoo/odoo
cd odoo
ls
ls -la
git pull
cd ..
rm odoo
rm -R  odoo
git clone -b 9.0 https//:github/odoo/odoo
git clone -b 9.0 https//:github.com/odoo/odoo
git clone -b 9.0 https://github.com/odoo/odoo.git
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
exit
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
sudo apt-get install lxml
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
cd odoo
;s
ls
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
cd ..
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
nano /etc/odoo-genemedics.conf 
service /etc/init.d/genemedics-server start
exit
exit
ls
cd ~
ls
cd odoo/
git log
cd ..
git pull
exit
cd~
cd ~
nano odoo/addons/crm/__openerp__.py 
exit
ls
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf -u all
exit
cd ~
ls
git pull
exit
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf -u all
exit
ls
cd ~
git pull
exit
ls
cd ~
cd  odoo/
git pull
cd cd  addons/web_calendar/static/js
cd cd  addons/web_calendar/static/
cd cd  addons/web_calendar/static
cd  addons/web_calendar/static/src/js/
ls
nano web_calendar.js 
nano  -c web_calendar.js 
cd ~
cd odoo
git status
git diff
git commit
git add .
git status
git commit -a -m " change to calendar.js for open on specific day and crm to not load lead stages"
ls
cd ..
ls
ls
nano .gitmodules 
cd ..
cp -R  genemedics/ genemedics2/
cp -R  genemedics/ genemedics2/
exit
ls
cd ~/addons-extra/genemedics/crm_genemedics/
ls
nano __openerp__.py 
exit 
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
exit
ls
cd ~
ls
cd ..
ls
cd 
ls
cd addons-extra/genemedics/crm_
cd addons-extra/genemedics/crm_genemedics/
ls
cd views
ls
cd ..
nano __openerp__.py 
ls
cd static/
ls
cd js/
ls
mv web_calendar.js web_calendar.js2
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
nano addons-extra/genemedics/crm_genemedics/__openerp__.py 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
cd ..odoo
cd ood
odoo
cd odoo/
sudo git log
git log
git checkout commit 3b5e7feb161563cbb2f5cc8187a4c6687f65068d
git checkout 3b5e7feb161563cbb2f5cc8187a4c6687f65068d
cd ..
cd addons-extra/genemedics/crm_genemedics/
ls
nano __openerp__.py 
cd ~
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
ls
ls
ls
nano
ls
ps aux | grep python
kill -9 14789
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
cd~
cd ~
nano cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
ps aux | grep python
kill 32583
kill 14805
ls
ps aux | grep python
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
exit
psql
cd ~
ls
nano cmd-odoo-genemedics.conf 
nano /etc/odoo-genemedics.conf 
chmod /etc/odoo-genemedics.conf 700
chmod 700 /etc/odoo-genemedics.conf
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
ps aux | grep python
nano cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
nano cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf 
./odoo/odoo.py -c cmd-odoo-genemedics.conf  --save
sudo swapon -s
exit
cd ~
ls
cd  odoo/
ls
git log
git pull
cd ~
nano /etc/odoo-genemedics.conf 
exit
cd~
cd ~
ls
cd  od
cd odoo
git log
git pull
git checkout 9.0
git pull
git log
cd ..
ls
cd configs/
ls
cd ..
cp /etc/odoo-genemedics.conf cmd-odoo.conf
ls
nano cmd-odoo.conf 
./odoo/odoo.py -c cmd-odoo.conf -u all
exit
cd ~
ls
cd d..
cd ..
ls
cd genemedics
ls
cd addons-extra/genemedics/
ls
cd crm_genemedics/
ls
nano __init__.py
exit
ls
cd .git/config 
nano .git/config 
git push
git push origin master
exit
exit
