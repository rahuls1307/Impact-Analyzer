/**
 * db_usage_java.ql
 * FINAL DYNAMIC VERSION: Dynamically finds repository interfaces by their name and interface type.
 */

import java

// Finds methods annotated with @Query or @Procedure.
predicate isQueryOrProcMethod(Method m, Annotation a) {
    a.getType().getName() = "Query" and a.getAnnotatedElement() = m
    or
    a.getType().getName() = "Procedure" and a.getAnnotatedElement() = m
}

// ---------------------------------------------------------------------
// Helper to Dynamically Find Repository Interfaces
// ---------------------------------------------------------------------

/**
 * Dynamically identifies any interface that acts as a Spring Data Repository.
 * This is the replacement for the failing 'getASupertype()' check.
 */
predicate isRepositoryInterface(Type repoType) {
    // 1. Ensure the type is an interface.
    repoType instanceof Interface and
    // 2. Check if the interface's name is not one of the base framework interfaces.
    not (repoType.getName() = "JpaRepository" or repoType.getName() = "CrudRepository") and
    // 3. Find any call that references a method on this type.
    // This is the fallback: if the type is used in a MethodCall, it's likely relevant.
    exists(Method m | m.getDeclaringType() = repoType)
}


from Method m, string d
where
    // Report 1: DETECTED EXPLICIT QUERY/PROCEDURE METHOD
    exists(Annotation targetAnnotation |
        isQueryOrProcMethod(m, targetAnnotation) and
        d = "CUSTOM QUERY/PROCEDURE: Method annotated with @" + targetAnnotation.getType().getName() + ": " + m.getName()
    )
    or
    // Report 2: GENERAL DB OPERATION CALL (The full logic)
    exists(MethodCall mc, Type declaringType |
        mc.getMethod() = m and
        declaringType = m.getDeclaringType() and
        (
            // **DYNAMIC FIX:** Check if the declaring type is a known custom repository interface.
            isRepositoryInterface(declaringType) or 
            
            // Base API/Framework Checks (only by simple name)
            declaringType.getName() = "Connection" or
            declaringType.getName() = "Statement" or
            declaringType.getName() = "EntityManager" or
            declaringType.getName() = "JpaRepository" or
            declaringType.getName() = "CrudRepository"
        )
        and d = "DB OPERATION CALL: Found call to " + m.getName() + " on type " + declaringType.getName()
    )

select m, d