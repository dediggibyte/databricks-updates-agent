**Applies to:**  Databricks SQL  Databricks Runtime

Returns the metadata of output of a query.

## Syntax

```
{ DESC | DESCRIBE } [ QUERY ] input_statement
```

## Parameters

* **QUERY**

  This clause is optional and may be omitted.
* **[query](/aws/en/sql/language-manual/sql-ref-syntax-qry-query)**

  The query to be described.

## Examples

SQL

```
-- Create table `person`  
> CREATE TABLE person (name STRING , age INT COMMENT 'Age column', address STRING);  
  
-- Returns column metadata information for a simple select query  
> DESCRIBE QUERY SELECT age, sum(age) FROM person GROUP BY age;  
 col_name data_type    comment  
 -------- --------- ----------  
      age       int Age column  
 sum(age)    bigint       null  
  
-- Returns column metadata information for common table expression (`CTE`).  
> DESCRIBE QUERY WITH all_names_cte  
    AS (SELECT name FROM person) SELECT * FROM all_names_cte;  
 col_name data_type comment  
 -------- --------- -------  
     name    string    null  
  
-- Returns column metadata information for an inline table.  
> DESCRIBE QUERY VALUES(100, 'John', 10000.20D) AS employee(id, name, salary);  
 col_name data_type comment  
 -------- --------- -------  
       id       int    null  
     name    string    null  
   salary    double    null  
  
-- Returns column metadata information for `TABLE` statement.  
> DESCRIBE QUERY TABLE person;  
 col_name data_type    comment  
 -------- --------- ----------  
     name    string       null  
      age       int  Agecolumn  
  address    string       null
```

## Related articles

* [DESCRIBE SCHEMA](/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-schema)
* [DESCRIBE TABLE](/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-table)
* [DESCRIBE FUNCTION](/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-function)