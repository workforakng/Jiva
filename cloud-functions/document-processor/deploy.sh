#!/bin/bash

# Deployment script for document processor Cloud Function

PROJECT_ID="your-project-id"
REGION="us-central1"
FUNCTION_NAME="process-medical-document"
RUNTIME="python311"
MEMORY="512MB"
TIMEOUT="540s"
MAX_INSTANCES="10"

# Deploy the Cloud Function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=. \
  --entry-point=process_document \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=your-storage-bucket" \
  --memory=$MEMORY \
  --timeout=$TIMEOUT \
  --max-instances=$MAX_INSTANCES \
  --service-account=your-service-account@your-project-id.iam.gserviceaccount.com \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

echo "Cloud Function deployed successfully!"
