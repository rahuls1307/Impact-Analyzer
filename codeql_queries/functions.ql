/**
 * functions.ql
 * Lists all function/method definitions.
 */

import python  // <-- will be replaced dynamically per language

from Method f
select f, f.getName(), f.getDeclaringType()
