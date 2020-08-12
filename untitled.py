import random
import string


def id_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size)).lower()


with open('test.sql', 'w') as f:
    c = 0
    for i in range(500):
        schema = 'app' + str(i).zfill(3)
        f.write('CREATE SCHEMA %s;\n' % schema)
        f.write('GRANT USAGE ON SCHEMA %s TO metamapper_ro;\n' % schema)
        for j in range(100):
            sql = 'CREATE TABLE %s.table%s (' % (schema, str(j).zfill(3))
            out = []
            for x in range(random.randint(2, 11)):
                out.append('%s varchar(50) ' % id_generator())
            sql += ',\n'.join(out)
            sql += ');\n\n'
            c += 1
            f.write(sql)

print(c)
