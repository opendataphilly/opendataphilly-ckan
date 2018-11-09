## Exporting and importing data

### Making a new sanitized export from production

Log into the remote server:
```
ssh-add KEY_FILE
ssh ubuntu@opendataphilly.org
```

Install Postgres 9.4 client:
```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y postgresql-client-9.4
```

Export the database (replace PASSWORD with the database password, which you can find by looking for lines like these in `/etc/ckan/default/production.ini`):
```
mkdir database_dumps && cd database_dumps

/usr/lib/postgresql/9.4/bin/pg_dump \
   "postgresql://ckan_default:PASSWORD@database.service.opendataphilly.internal/ckan_default" \
   > ckan_default-`date -I`.sql

/usr/lib/postgresql/9.4/bin/pg_dump \
   "postgresql://ckan_default:PASSWORD@database.service.opendataphilly.internal/datastore_default" \
   > ckan_datastore-`date -I`.sql
```

Log out of the remote server.

Copy the files to your local machine:
```
scp ubuntu@opendataphilly.org:database_dumps/* .
```

Delete the export files from the server:
```
ssh ubuntu@opendataphilly.org "rm -r database_dumps"
```

Start a Postgres 9.4 docker container:
```
docker run --name odp_export -e POSTGRES_PASSWORD=odp -d postgres:9.4
```

Create and import the main database:
```
docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres:9.4 \
   psql -h postgres -U postgres postgres -c "CREATE DATABASE ckan_default;"
docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres:9.4 \
   psql -h postgres -U postgres postgres -c "CREATE USER ckan_default;"
docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres:9.4 \
   psql -h postgres -U postgres ckan_default < ckan_default-`date -I`.sql
```

Make anonymizing queries.
You'll need the `faker` python package, so either make a virtualenv, activate it, and run `pip install faker` or just install it globally.
Run the command and write the resulting queries to a file:
```
./generate_anon_queries.sh > anon_queries.sql
```

Run the queries against the main database:
```
docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres:9.4 \
   psql -h postgres -U postgres ckan_default < anon_queries.sql
```

Export the sanitized database
```
docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres:9.4 \
   pg_dump -h postgres -U postgres -d ckan_default > ckan_default_sanitized-`date -I`.sql
```

Now that you have the sanitized version, you can delete the non-sanitized `ckan_default` file and stop and remove the database container:
```
rm ckan_default-`date -I`.sql
docker stop odp_export && docker rm -v odp_export
```

Since SQL files compress quite a bit, put the two files into a tarball:
```
tar czvf ODP_db_dumps-`date -I`.tar.gz \
    ckan_default_sanitized-`date -I`.sql ckan_datastore-`date -I`.sql
```

Now copy the `.tar.gz` file to a suitable storage location and, if you're done with them, delete the separate files.


### Importing into development

Extract the export files into your project root (or somewhere else that's within a directory that's mapped into the VM).

Import them (fill in the filenames and, if you put them in a different directory, adjust the paths):
```
vagrant ssh database<<EOF
export PGPASSWORD=ckan_default
psql -U ckan_default -h 127.0.0.1 -d ckan_default -f /vagrant/ckan_default_sanitized-YYYY-MM-DD.sql
psql -U ckan_default -h 127.0.0.1 -d datastore_default -f /vagrant/ckan_datastore-YYYY-MM-DD.sql
EOF
```

That should print a bunch of SQL messages.

Restart the services:
```
vagrant ssh app <<EOF
sudo service apache2 restart
sudo service jetty restart
sudo ckan search-index rebuild -r
sudo ckan views create -y
EOF
```

Make an admin user, by running this then following the prompts:
```
vagrant ssh app -c 'sudo ckan sysadmin add admin'
```

## Copying uploaded images

Many of the images used on the site (such as the Topic icons and the Organization logo images) are stored as uploads.  The files are on the server's file system and the Topic and Organization entities in the database store just the filename.

To get them working in development, download the images from the production server and upload them to your instance:
```
scp -r ubuntu@opendataphilly.org:/var/lib/ckan/default/storage/uploads/ uploads
vagrant ssh app -c "sudo cp -r /vagrant/uploads/* /var/lib/ckan/default/storage/uploads/"
```
