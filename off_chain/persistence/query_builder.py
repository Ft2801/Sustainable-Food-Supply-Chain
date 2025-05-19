# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
# pylint: disable= attribute-defined-outside-init
from configuration.database import Database


class QueryBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.query_table = None
        self.query_type = None
        self.query_select = []
        self.query_where = []  # Adesso contiene tuple: (connettivo, field, operator, value)
        self.query_insert = {}
        self.query_update = {}
        self.query_limit = None
        self.query_order_by = None
        self.query_joins = []
        self.query_group_by = []
        self.query_aggregates = []

    def table(self, table_name):
        self.query_table = table_name
        return self

    def select(self, *fields):
        self.query_type = 'select'
        self.query_select = list(fields) if fields else ["*"]
        return self

    def where(self, field, operator, value):
        if not self.query_where:
            self.query_where.append(("AND", field, operator, value))  # prima condizione, AND implicito
        else:
            self.query_where.append(("AND", field, operator, value))
        return self

    def or_where(self, field, operator, value):
        if not self.query_where:
            raise ValueError("or_where() non può essere chiamato come prima condizione.")
        self.query_where.append(("OR", field, operator, value))
        return self

    def join(self, table, on_field1, on_field2, type=""):
        self.query_joins.append(f"{type} JOIN {table} ON {on_field1} = {on_field2}")
        return self

    def insert(self, **kwargs):
        self.query_type = 'insert'
        self.query_insert = kwargs
        return self

    def update(self, **kwargs):
        self.query_type = 'update'
        for k, v in kwargs.items():
            if isinstance(v, tuple):
                self.query_update[k] = v
            else:
                self.query_update[k] = ("?", [v])
        return self

    def delete(self):
        self.query_type = 'delete'
        return self

    def limit(self, limit):
        self.query_limit = limit
        return self

    def order_by(self, field, direction="ASC"):
        self.query_order_by = (field, direction)
        return self

    def group_by(self, *fields):
        self.query_group_by = list(fields)
        return self

    def aggregate(self, outer_function, inner_expression, alias=None):
        agg_query = f"{outer_function}({inner_expression})"
        if alias:
            agg_query += f" AS {alias}"
        self.query_aggregates.append(agg_query)
        return self

    def get_query(self):
        if not self.query_table:
            raise ValueError("Tabella non specificata. Chiama table() prima di get_query().")

        if self.query_type == 'select':
            query, values = self._build_select_query()
        elif self.query_type == 'insert':
            query, values = self._build_insert_query()
        elif self.query_type == 'update':
            if not self.query_where:
                raise ValueError("Le query UPDATE senza WHERE sono pericolose! Aggiungi una condizione.")
            query, values = self._build_update_query()
        elif self.query_type == 'delete':
            if not self.query_where:
                raise ValueError("Le query DELETE senza WHERE sono pericolose! Aggiungi una condizione.")
            query, values = self._build_delete_query()
        else:
            raise ValueError("Tipo di query non specificato.")

        self.reset()
        return query, values

    def _build_select_query(self):
        fields = ", ".join(self.query_select + self.query_aggregates) if self.query_aggregates else ", ".join(self.query_select)
        query = f"SELECT {fields} FROM {self.query_table}"

        if self.query_joins:
            query += " " + " ".join(self.query_joins)

        values = []
        if self.query_where:
            query += " WHERE "
            conditions = []
            for i, (logic, field, operator, value) in enumerate(self.query_where):
                prefix = "" if i == 0 else f" {logic} "
                conditions.append(f"{prefix}{field} {operator} ?")
                values.append(value)
            query += "".join(conditions)

        if self.query_group_by:
            query += " GROUP BY " + ", ".join(self.query_group_by)

        if self.query_order_by:
            query += f" ORDER BY {self.query_order_by[0]} {self.query_order_by[1]}"

        if self.query_limit is not None:
            query += " LIMIT ?"
            values.append(self.query_limit)

        return query, values

    def _build_insert_query(self):
        columns = ", ".join(self.query_insert.keys())
        placeholders = ", ".join(["?" for _ in self.query_insert])
        query = f"INSERT INTO {self.query_table} ({columns}) VALUES ({placeholders})"
        values = list(self.query_insert.values())
        return query, values

    def _build_update_query(self):
        set_clauses = []
        values = []
        for col, (expr, vals) in self.query_update.items():
            set_clauses.append(f"{col} = {expr}")
            values.extend(vals)

        query = f"UPDATE {self.query_table} SET " + ", ".join(set_clauses)

        if self.query_where:
            query += " WHERE "
            where_clauses = []
            for i, (logic, field, operator, value) in enumerate(self.query_where):
                prefix = "" if i == 0 else f" {logic} "
                where_clauses.append(f"{prefix}{field} {operator} ?")
                values.append(value)
            query += "".join(where_clauses)

        return query, values

    def _build_delete_query(self):
        query = f"DELETE FROM {self.query_table}"
        values = []

        if self.query_where:
            query += " WHERE "
            conditions = []
            for i, (logic, field, operator, value) in enumerate(self.query_where):
                prefix = "" if i == 0 else f" {logic} "
                conditions.append(f"{prefix}{field} {operator} ?")
                values.append(value)
            query += "".join(conditions)

        return query, values

    def execute_and_return_last_id(self):
        db = Database()
        conn = db.conn
        query_type = self.query_type
        query, values = self.get_query()

        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()

        if query_type == 'insert':
            return cursor.lastrowid
        return None

    def execute_and_fetch_one(self):
        db = Database()
        query, values = self.get_query()
        cursor = db.conn.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result[0] if result else None
