/**
 * config_usage.ql
 * Finds references to configuration files (.yaml, .yml, .json, .xml)
 */

import python  // <-- replaced dynamically

from Literal l
where
  l.getValue().matches("%.yaml") or
  l.getValue().matches("%.yml") or
  l.getValue().matches("%.json") or
  l.getValue().matches("%.xml")
select l, "config reference"
