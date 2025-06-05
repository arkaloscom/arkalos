
from arkalos import DWH
from arkalos.schema.data_warehouse_migration import DataWarehouseMigration



class Migration(DataWarehouseMigration):
    
    def up(self):

        with DWH().clean().createTable('MAKE') as table:
            table.col('id').id()
            
            table.col('created_at').datetime().notNull().defaultNow()
            table.col('updated_at').datetime().notNull().defaultNow()



    def down(self):
        DWH().clean().dropTable('MAKE')
