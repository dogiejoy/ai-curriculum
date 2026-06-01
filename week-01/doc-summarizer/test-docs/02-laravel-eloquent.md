# Laravel Eloquent ORM

Eloquent is Laravel's built-in ORM that provides an active record implementation
for working with databases. Each table maps to a model class.

## Basic usage

Models extend `Illuminate\Database\Eloquent\Model`. By convention, the table
name is the plural snake_case of the class name (`User` → `users`).

## Relationships

Eloquent supports common relationships: hasOne, hasMany, belongsTo,
belongsToMany, and morphTo. Define them as methods on the model:

```php
class Post extends Model {
    public function comments() {
        return $this->hasMany(Comment::class);
    }
}
```

## N+1 problem

A common performance issue: loading a list of models then accessing their
relationships in a loop triggers one query per item. Use eager loading with
`with()` to fetch all related data in one query.

## Query scopes

Local scopes let you reuse query logic: `Post::active()->latest()->get()`.
Define them as methods prefixed with `scope`.

## When to avoid Eloquent

For bulk inserts of 10,000+ rows, use the query builder or raw SQL. Eloquent
creates a model instance per row which has overhead.
