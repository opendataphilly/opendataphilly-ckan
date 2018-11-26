#!/bin/sh
#
# Generate queries to anonymize OpenDataPhilly PostgreSQL DB dumps.

# Run query against local PostgreSQL DB.
# 1st Argument: DB Name
# 2nd Argument: Query
run_query () 
{
    docker run -i --rm -e PGPASSWORD=odp --link odp_export:postgres postgres \
        psql -h postgres -U postgres -t -A "$1" \
            -c "$2";
}

# Insane hack. Establishes named piped connected to interactive Python shell,
# so that we don't need to reimport the Faker packages for every function call.
establish_fake_context ()
{
    mkfifo /tmp/faker_in
    python -i < /tmp/faker_in >> /tmp/faker_out &
    exec 3>/tmp/faker_in
    echo "import string; from faker import Faker; fake = Faker();" >&3
}

close_fake_context ()
{
    exec 3>&-
    rm -f /tmp/faker*
}

# Wait for the Python shell to finish.
wait_for_it ()
{
    while ! [ -s /tmp/faker_out ]; do
        :
    done
}

# Generate fake data.
# 1st Argument: Anything that `$ faker profile` returns.
fake ()
{
    cp /dev/null /tmp/faker_out
    echo "print(fake.profile()['$1']);" >&3
    wait_for_it
    echo $(tail -n 1 /tmp/faker_out)
}

# Generate a fake SHA.
fake_sha ()
{
    cp /dev/null /tmp/faker_out
    echo "print(fake.sha1(raw_output=False));" >&3
    wait_for_it
    echo $(tail -n 1 /tmp/faker_out)
}

#Generate a fake UUID.
fake_uuid4 ()
{
    cp /dev/null /tmp/faker_out
    echo "print(fake.uuid4());" >&3
    wait_for_it
    echo $(tail -n 1 /tmp/faker_out)
}

establish_fake_context

for user_id in $(run_query ckan_default 'select id from "user"'); do    
    echo "\
UPDATE \"user\" \
SET \"name\" = '$(fake username)${RANDOM}', \
fullname = '$(fake name)', \
email = '${RANDOM}$(fake mail)', \
password = '$(fake_sha)', \
apikey = '$(fake_uuid4)', \
reset_key = null, \
about = null, \
created = '2017-08-10 13:32:27.583108' \
WHERE id = '$user_id';";
done

close_fake_context
