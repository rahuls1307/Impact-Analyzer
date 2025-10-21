/**
 * functions_java.ql
 * Lists all Java methods with their fully qualified names and signatures.
 */

import java

from Method m
select 
  m,
  m.getDeclaringType().getQualifiedName(),
  m.getName(),
  m.getSignature(),
  "Function defined: " + m.getDeclaringType().getQualifiedName() + "." + m.getName()
