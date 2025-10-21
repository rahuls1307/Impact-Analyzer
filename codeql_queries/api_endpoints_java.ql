/**
 * api_endpoints_java.ql
 * Detects REST API endpoints (Spring Boot, JAX-RS, Play Framework) 
 * Corrected for CodeQL version 2.23.3 to use a.getType().getQualifiedName().
 */

import java

// Define a type that enumerates all fully qualified names for API annotations.
private string restAnnotationQualifiedName() {
  // Spring Web annotations
  result = "org.springframework.web.bind.annotation.GetMapping"
  or result = "org.springframework.web.bind.annotation.PostMapping"
  or result = "org.springframework.web.bind.annotation.PutMapping"
  or result = "org.springframework.web.bind.annotation.DeleteMapping"
  or result = "org.springframework.web.bind.annotation.RequestMapping"
  // JAX-RS annotations
  or result = "javax.ws.rs.GET"
  or result = "javax.ws.rs.POST"
  or result = "javax.ws.rs.PUT"
  or result = "javax.ws.rs.DELETE"
  or result = "javax.ws.rs.Path"
  // Play Framework annotation
  or result = "play.mvc.With"
}

from Method m, Annotation a
where m.getAnAnnotation() = a
  // THIS LINE IS THE FIX: Call getType() before getQualifiedName()
  and a.getType().getQualifiedName() = restAnnotationQualifiedName() 
select m, "API endpoint detected: " + m.getName()