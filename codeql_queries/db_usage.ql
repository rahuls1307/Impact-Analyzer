/**
 * db_usage.ql
 * Detects SQL/NoSQL queries, table usage, DB method calls.
 */

import python  // <-- replaced dynamically

/**
 * For SQL, look for string literals containing common keywords
 * For NoSQL, find method calls like find(), insert(), update()
 */
from Function f, Literal l
where
  l.getValue().matches("%select%") or
  l.getValue().matches("%insert%") or
  l.getValue().matches("%update%") or
  l.getValue().matches("%delete%") or
  l.getValue().matches("%create table%")
select f, l, "db usage"
