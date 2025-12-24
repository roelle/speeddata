---
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-sqlite-with-time-series-extension.md
type: external
target: sqlite-with-time-series-extension
verdict: pass
assurance_level: L2
carrier_ref: test-runner
content_hash: f75d3950917f8ff8e0c49479cd9fbda4
---

SQLite Integration Analysis:

**NumPy Arrays**: pandas.read_sql() → df.to_numpy() OR direct sqlite3.Cursor.fetchall() → np.array(). Example: `cursor.execute('SELECT voltage FROM channel1'); data = np.array(cursor.fetchall())`.

**Pandas**: Native support via pandas.read_sql_query() or pandas.read_sql_table(). Example: `df = pd.read_sql_query('SELECT * FROM channel1 WHERE timestamp BETWEEN ? AND ?', conn, params=[start, end])`. Supports parameterized queries for time-range filtering.

**Polars**: pl.read_database() with SQLite connection string. Example: `df = pl.read_database('SELECT * FROM channel1', 'sqlite:///data.db')`. Requires connectorx or sqlalchemy backend.

**Roelle DataSet**: SQLite → Pandas → DataSet or direct sqlite3 cursor → numpy → DataSet. Both pathways require custom wrapper (~25-50 LOC) to handle SQL query construction, connection management, multi-channel aggregation via JOIN.

**Evidence**: pandas.read_sql documentation confirms SQLite support via sqlite3 connection objects (https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html). Polars read_database() supports SQLite via connectorx (https://pola-rs.github.io/polars/py-polars/html/reference/api/polars.read_database.html). sqlite3 stdlib cursor returns row tuples convertible to numpy arrays.

**Deserialization Code Requirement**: Moderate. SQL query construction needed for time-range filtering. Multi-channel aggregation requires JOIN logic. Connection management boilerplate. Row-to-column transformation handled by Pandas/Polars but DataSet wrapper more complex (~50 LOC) due to SQL abstraction layer.

**Conclusion**: All 4 target formats supported but with more deserialization overhead than columnar formats. Pandas has best SQLite integration. Polars requires external dependency (connectorx). NumPy requires manual array construction. DataSet wrapper most complex due to SQL impedance mismatch.