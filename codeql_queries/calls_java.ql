/**
 * calls_java.ql
 * Captures method call relationships between caller and callee.
 */

import java

from MethodCall mc, Method caller, Method callee
where
  mc.getEnclosingCallable() = caller and
  callee = mc.getMethod()
select 
  caller,
  callee,
  "Call: " + caller.getDeclaringType().getQualifiedName() + "." + caller.getName() +
  " → " + callee.getDeclaringType().getQualifiedName() + "." + callee.getName()
