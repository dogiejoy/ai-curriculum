# REST API Design Principles

REST (Representational State Transfer) is an architectural style for designing
networked applications. A REST API uses HTTP methods to perform CRUD operations
on resources identified by URLs.

## Core principles

1. **Statelessness** — Each request from client to server must contain all
   information needed to understand the request. The server should not store
   client context between requests.

2. **Resource-based** — Resources are the key abstraction. Each resource has
   a unique URL. For example, `/users/42` identifies user with ID 42.

3. **HTTP methods semantics** — GET retrieves, POST creates, PUT updates,
   DELETE removes. PATCH partially updates a resource.

4. **Status codes** — Use proper HTTP status codes: 200 success, 201 created,
   400 bad request, 401 unauthorized, 404 not found, 500 server error.

5. **HATEOAS** — Hypermedia as the Engine of Application State. Responses
   should include links to related resources for discoverability.

## Common pitfalls

Over-nesting URLs like `/users/42/posts/7/comments/3/replies/5` makes the API
hard to use. Prefer flatter structures with query parameters.
