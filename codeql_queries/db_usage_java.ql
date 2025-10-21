/**
 * db_usage_java.ql
 * FINAL OUTPUT FORMAT VERSION: Reports Repository and Method names for external grouping.
 */

import java

// Finds methods annotated with @Query or @Procedure.
predicate isQueryOrProcMethod(Method m, Annotation a) {
    a.getType().getName() = "Query" and a.getAnnotatedElement() = m
    or
    a.getType().getName() = "Procedure" and a.getAnnotatedElement() = m
}

from Method m, Type declaringType, string repoName, string methodName
where
    // Logic 1: CUSTOM REPOSITORY METHODS
    (
        isRepositoryInterface(declaringType) and // Uses the dynamic check from previous answer
        declaringType = m.getDeclaringType() and
        repoName = declaringType.getName() and
        methodName = m.getName()
    )
    or
    // Logic 2: BASE REPOSITORY METHODS (e.g., JpaRepository.save)
    (
        (declaringType.getName() = "JpaRepository" or declaringType.getName() = "CrudRepository") and
        declaringType = m.getDeclaringType() and
        repoName = declaringType.getName() and
        methodName = m.getName()
    )
    or
    // Logic 3: ANNOTATED QUERIES/PROCS
    exists(Annotation a | 
        isQueryOrProcMethod(m, a) and
        declaringType = m.getDeclaringType() and
        repoName = declaringType.getName() and
        methodName = m.getName() + " (@" + a.getType().getName() + ")"
    )
    or
    // Logic 4: DIRECT API/CONNECTION CALLS (Filter out HTTP spam)
    (
        declaringType.getName() = "Connection" and
        declaringType = m.getDeclaringType() and
        // Filter out known HTTP methods (basic list)
        not (m.getName() = "request" or m.getName() = "response" or m.getName() = "cookieStore" or m.getName() = "parser") and
        repoName = declaringType.getName() and
        methodName = m.getName()
    )
select repoName, methodName