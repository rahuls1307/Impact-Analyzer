/**
 * calls.ql
 * Maps all function calls (caller → callee).
 */

import python  // <-- replaced dynamically

from Call c, Function caller, Function callee
where c.getTarget() = callee and c.getEnclosingFunction() = caller
select caller, callee, c, "caller=" + caller.getName() + ", callee=" + callee.getName()
