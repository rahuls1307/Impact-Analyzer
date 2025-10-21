/**
 * api_endpoints.ql
 * Detects REST endpoints (@GetMapping, @PostMapping, @app.route, etc.)
 */

import python  // <-- replaced dynamically

from Function f, Annotation a
where f.hasAnnotation(a) and
      (
        a.getName() = "RequestMapping" or
        a.getName() = "GetMapping" or
        a.getName() = "PostMapping" or
        a.getName() = "PutMapping" or
        a.getName() = "DeleteMapping" or
        a.getName() = "app.route"
      )
select f, a, "api endpoint"
