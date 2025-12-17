# CRUD MCP Server

A production-ready Model Context Protocol (MCP) server that exposes database CRUD operations as tools. Built with Python and SQLite, this server demonstrates best practices for safe database access, input validation, and error handling.

## Architecture Overview

```
┌─────────────────┐
│   MCP Client    │  (e.g., Claude, Cursor, VS Code Extensions)
└────────┬────────┘
         │
    MCP Protocol
         │
┌─────────────────────────────────────┐
│    MCP Server (server.py)           │
│  ├─ Tool Definitions                │
│  ├─ Tool Handlers                   │
│  └─ Error Management                │
└────────┬────────────────────────────┘
         │
    Parameterized Queries
         │
┌─────────────────────────────────────┐
│   DatabaseManager Class             │
│  ├─ create_user()                   │
│  ├─ read_user()                     │
│  ├─ read_all_users()                │
│  ├─ update_user()                   │
│  └─ delete_user()                   │
└────────┬────────────────────────────┘
         │
    SQLite Driver
         │
┌─────────────────────────────────────┐
│   SQLite Database (users.db)        │
│   ├─ users table                    │
│   │  ├─ id (PRIMARY KEY)            │
│   │  ├─ name (TEXT)                 │
│   │  ├─ email (TEXT, UNIQUE)        │
│   │  └─ created_at (TIMESTAMP)      │
└─────────────────────────────────────┘
```

## Database Schema

### Users Table

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Schema Explanation:**
- **id**: Auto-incrementing primary key for unique identification
- **name**: User's full name (required, non-empty string)
- **email**: User's email (required, must be unique to prevent duplicates)
- **created_at**: Automatic timestamp when the record is created

## CRUD Operations

### 1. Create User
- **Tool Name**: `create_user`
- **Parameters**: `name` (string), `email` (string)
- **Returns**: Created user object with id and timestamp
- **Validation**: Non-empty name, valid email format
- **Error Handling**: Catches duplicate emails with helpful message

```python
# Example: Create a new user
db.create_user("John Doe", "john@example.com")
```

### 2. Read User (Single)
- **Tool Name**: `read_user`
- **Parameters**: `user_id` (integer)
- **Returns**: User object or error if not found
- **Validation**: Positive integer ID required

```python
# Example: Fetch a user by ID
db.read_user(1)
```

### 3. Read All Users
- **Tool Name**: `read_all_users`
- **Parameters**: `limit` (integer, max 1000), `offset` (integer)
- **Returns**: Array of users with pagination metadata
- **Use Case**: List all users with pagination support

```python
# Example: Fetch first 10 users
db.read_all_users(limit=10, offset=0)
```

### 4. Update User
- **Tool Name**: `update_user`
- **Parameters**: `user_id` (required), `name` (optional), `email` (optional)
- **Returns**: Updated user object
- **Validation**: At least one field must be provided; format validation applies

```python
# Example: Update user name
db.update_user(1, name="Jane Doe")
```

### 5. Delete User
- **Tool Name**: `delete_user`
- **Parameters**: `user_id` (integer)
- **Returns**: Deleted user object (for confirmation)
- **Note**: Permanent deletion; consider soft deletes for production

```python
# Example: Delete a user
db.delete_user(1)
```

## Security Features

### 1. Parameterized Queries
All database queries use parameterized statements (`?` placeholders) to prevent SQL injection:

```python
# ✅ SAFE - Uses parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ UNSAFE - String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 2. Input Validation
Every operation validates input before database access:
- **Type checking**: Ensures correct data types
- **Format validation**: Email contains `@`, non-empty strings
- **Range validation**: Positive integers, limit caps

### 3. Error Handling
Three-layer error handling:
1. **Validation layer**: Catches invalid input early
2. **Database layer**: Catches SQLite errors (integrity constraints, etc.)
3. **Server layer**: Returns consistent JSON error responses

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip package manager

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "c:\Users\Aditya Jain\Desktop\crud api and database"

# Install required package
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Check MCP installation
python -c "import mcp; print(f'MCP version: {mcp.__version__}')"
```

### Step 3: Run the Server

```bash
# Start the MCP server
python server.py
```

**Expected Output:**
```
INFO:__main__:Database initialized at users.db
INFO:__main__:CRUD MCP Server running. Waiting for requests...
```

## Testing with MCP Inspector

### What is MCP Inspector?
MCP Inspector is a browser-based tool that lets you connect to and test MCP servers in real-time.

### Step 1: Install MCP Inspector

```bash
# Install globally (recommended)
npm install -g @modelcontextprotocol/inspector
```

### Step 2: Start the Server in Terminal 1

```bash
# Terminal 1: Keep the server running
python server.py
```

### Step 3: Launch MCP Inspector in Terminal 2

```bash
# Terminal 2: Launch inspector
mcp-inspector
```

This opens the inspector at `http://localhost:5173` in your default browser.

### Step 4: Configure Connection in Inspector

1. Click **"New Connection"** button
2. Select **"Command"** connection type
3. Enter command: `python server.py`
4. Set working directory: `c:\Users\Aditya Jain\Desktop\crud api and database`
5. Click **"Connect"**

### Step 5: Test CRUD Operations

Once connected, you'll see all available tools in the left sidebar:

#### Test 1: Create a User
1. Select **create_user** tool
2. Enter parameters:
   ```json
   {
     "name": "Alice Johnson",
     "email": "alice@example.com"
   }
   ```
3. Click **"Call Tool"**
4. Observe the response with the created user

#### Test 2: Read the User
1. Select **read_user** tool
2. Enter parameters:
   ```json
   {
     "user_id": 1
   }
   ```
3. Click **"Call Tool"**

#### Test 3: Read All Users
1. Select **read_all_users** tool
2. Use default parameters (limit: 100, offset: 0)
3. Click **"Call Tool"**

#### Test 4: Update User
1. Select **update_user** tool
2. Enter parameters:
   ```json
   {
     "user_id": 1,
     "email": "alice.new@example.com"
   }
   ```
3. Click **"Call Tool"**

#### Test 5: Delete User
1. Select **delete_user** tool
2. Enter parameters:
   ```json
   {
     "user_id": 1
   }
   ```
3. Click **"Call Tool"**

### Step 6: Verify Database Changes

Check the database file directly:

```bash
# SQLite CLI (if installed)
sqlite3 users.db "SELECT * FROM users;"

# Or use Python
python -c "
import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM users')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

## Response Format

All tools return structured JSON responses:

### Success Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15 10:30:45"
  },
  "message": "User created successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Email already exists"
}
```

### List Response with Pagination
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "User 1",
      "email": "user1@example.com",
      "created_at": "2024-01-15 10:30:45"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 100,
    "offset": 0
  }
}
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'mcp'"
**Solution**: Ensure MCP is installed
```bash
pip install -r requirements.txt
# or
pip install mcp>=0.1.0
```

### Issue: "Database is locked"
**Solution**: SQLite locks occur with concurrent writes. This POC uses single connections. For production, implement connection pooling or use PostgreSQL.

### Issue: "Email already exists" on create
**Solution**: The UNIQUE constraint on email prevents duplicates. Try a different email or delete the record first.

### Issue: MCP Inspector can't connect to server
**Solution**: Ensure:
1. Server is running (`python server.py`)
2. No firewall blocking connections
3. Correct command path in Inspector settings
4. Server hasn't crashed (check terminal for errors)

## Production Considerations

For deploying this beyond a POC:

1. **Database**: Migrate to PostgreSQL for production workloads
2. **Connection Pooling**: Use `sqlalchemy` or `psycopg2` with connection pools
3. **Soft Deletes**: Add `deleted_at` column instead of hard deletes
4. **Transactions**: Wrap multi-step operations in explicit transactions
5. **Indexing**: Add indexes on `email` and frequently-queried fields
6. **Monitoring**: Add metrics (query times, error rates)
7. **Authentication**: Add MCP authentication layer
8. **Rate Limiting**: Prevent abuse with request limits
9. **Caching**: Cache read operations for frequently-accessed records
10. **Logging**: Structured logging with audit trails

## Project Structure

```
crud-mcp-server/
├── server.py              # Main MCP server and database manager
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── users.db              # SQLite database (auto-created)
```

## Key Design Decisions

### Why SQLite for POC?
- Zero setup, file-based persistence
- Sufficient for single-user testing
- Easy to inspect with command-line tools

### Why Parameterized Queries?
- Prevents SQL injection attacks
- Forces proper type handling
- Standard best practice across all databases

### Why DatabaseManager Class?
- Encapsulates all database logic
- Easy to unit test independently
- Simple to migrate to ORM (SQLAlchemy) later

### Why Input Validation Before DB?
- Fast failure for bad input
- Prevents wasted database calls
- Better error messages for users



