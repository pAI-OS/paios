# Managers

To encapsulate related operations in a class that can be reused across the project, we use the Manager pattern.

The managers are singletons so expensive startup operations like creating directories, initialising databases, setting up environments, etc. are not performed on each instantiation.
