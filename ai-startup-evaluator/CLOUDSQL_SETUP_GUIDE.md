# CloudSQL Setup Guide for AI Interview Agent

## CloudSQL Configuration

The AI Interview Agent is configured to use the following CloudSQL instance:

- **Instance**: `startup-evaluator-db`
- **Database**: `startup_evaluator`
- **User**: `app-user`
- **Password**: `aianalyst`

## Environment Configuration

The system automatically detects the environment and uses the appropriate connection method:

1. **Google Cloud Environment** (Agent Engine, Cloud Run, etc.): Uses Unix socket connection
2. **Local with Cloud SQL Proxy**: Uses Unix socket connection
3. **Local Development**: Falls back to SQLite

## Connection Strings

### For Agent Engine Deployment
```
postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db
```

### For Local Development with Cloud SQL Proxy
```bash
# Install Cloud SQL Proxy
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
chmod +x cloud_sql_proxy

# Start proxy
./cloud_sql_proxy -instances=startup-evaluator-db=tcp:5432
```

### For Direct Connection (if needed)
```
postgresql://app-user:aianalyst@startup-evaluator-db/startup_evaluator
```

## Testing Connection

Run the connection test:
```bash
python test_cloudsql_connection.py
```

## Environment Variables

Create a `.env` file with:
```env
DATABASE_URL=postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db
GCS_BUCKET_NAME=startup-evaluator-storage
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```