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
