/**
 * config_usage_java.ql
 * FINAL STABLE VERSION: Reports only Field and Callable (Method) entities.
 *
 * NOTE: The check for an argument on @Value is removed, reporting all fields
 * annotated with @Value. The Call expression is replaced by reporting the 
 * Callable definition (the method itself).
 */

import java

// ---------------------------------------------------------------------
// Helper Predicate to combine two distinct report types (Field and Callable)
// ---------------------------------------------------------------------

/**
 * Gets a result that is either a Field annotated with @Value or a Callable
 * that performs resource loading.
 * @param element The entity to report (Field or Callable).
 * @param description The message for the report.
 */
predicate configUsageReport(Member element, string description) {
    // --- Report 1: Spring @Value Annotation (on a Field) ---
    exists(Field f, Annotation a |
        // Check for the @Value annotation using simple name checks.
        a.getType().getName() = "Value" and 
        a.getAnnotatedElement() = f and
        
        // FIX: Cannot check for argument existence, so we simply report the Field.
        
        element = f and
        description = "Implicit config usage: Property injected via @Value annotation on field " + f.getName()
    )
    or
    // --- Report 2: Explicit Resource Loading (Call to a Callable) ---
    exists(Call c, Callable callee |
        callee = c.getCallee() and
        (
            // Check for standard methods used to load external resources/config files
            callee.getName() = "getResource" or
            callee.getName() = "getInputStream" or
            callee.getName() = "getResourceAsStream"
        )
        // FIX: Report the Callable (method definition) itself, as the Call expression (c) is incompatible.
        and element = callee 
        and description = "Explicit config usage: Found call to resource/config loading method " + callee.getDeclaringType().getName() + "." + callee.getName() + " in " + c.getEnclosingCallable().getName()
    )
}

// ---------------------------------------------------------------------
// Final Select Clause
// ---------------------------------------------------------------------

from Member m, string d
where configUsageReport(m, d)
select m, d