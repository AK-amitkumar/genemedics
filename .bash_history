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
