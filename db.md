

Import `.csv` from open food facts to sqlite3:

```sqlite3 db.sqlite3

sqlite> .mode tab
sqlite> .import  /Users/wimmers/Downloads/openfoodfacts_search.csv products
sqlite> .schema products
sqlite> .read alterTable.sql
sqlite> drop table _products_old ;
```