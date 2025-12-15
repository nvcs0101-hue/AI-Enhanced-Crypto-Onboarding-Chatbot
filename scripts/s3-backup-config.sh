#!/bin/bash

# S3 Backup Configuration
# Run this after setting up AWS account

set -e

echo "🪣 S3 Backup Configuration"
echo "=========================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed"
    echo "   Install: pip install awscli"
    exit 1
fi

echo "📝 S3 Bucket Setup Steps:"
echo ""
echo "1. Create S3 bucket:"
read -p "   Enter bucket name (e.g., myapp-backups-prod): " BUCKET_NAME

echo ""
echo "2. Creating bucket..."
aws s3 mb "s3://$BUCKET_NAME" --region us-east-1

echo ""
echo "3. Configuring bucket versioning..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

echo ""
echo "4. Configuring lifecycle rules (delete after 90 days)..."
cat > /tmp/lifecycle.json <<LIFECYCLE
{
    "Rules": [
        {
            "Id": "DeleteOldBackups",
            "Status": "Enabled",
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
LIFECYCLE

aws s3api put-bucket-lifecycle-configuration \
    --bucket "$BUCKET_NAME" \
    --lifecycle-configuration file:///tmp/lifecycle.json

echo ""
echo "5. Enabling encryption..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

echo ""
echo "✅ S3 bucket configured successfully!"
echo ""
echo "📝 Add to your .env.secrets:"
echo "   S3_BUCKET=$BUCKET_NAME"
echo "   AWS_ACCESS_KEY_ID=your_access_key"
echo "   AWS_SECRET_ACCESS_KEY=your_secret_key"
echo ""
echo "🧪 Test upload:"
echo "   echo 'test' > test.txt"
echo "   aws s3 cp test.txt s3://$BUCKET_NAME/test/"
echo ""
