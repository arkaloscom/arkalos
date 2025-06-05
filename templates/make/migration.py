
from arkalos import DB
from arkalos.schema.database_migration import DatabaseMigration



class Migration(DatabaseMigration):
    
    def up(self):

        with DB().createTable('MAKE') as table:
            table.col('id').id()
            
            table.col('created_at').datetime().notNull().defaultNow()
            table.col('updated_at').datetime().notNull().defaultNow()



    def down(self):
        DB().dropTable('MAKE')
