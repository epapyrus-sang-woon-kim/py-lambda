# Increase Launch Template Version

## Overview

The `increase_launch_template_version` script is designed to automate the process of updating the Amazon Machine Image (AMI) in an Auto Scaling Group's (ASG) Launch Template to the latest version following a successful AWS CodeDeploy deployment. This ensures that any new instances launched by the ASG will be based on the most recent, stable system configuration.

## Features

- **Automated AMI Creation**: Generates a new AMI from the instance used in the latest successful deployment.
- **Dynamic Launch Template Update**: Retrieves and updates the Launch Template associated with the deployed ASG dynamically, ensuring that the latest AMI is utilized.
- **Error Handling**: Implements robust logging and error handling for troubleshooting and audit trails.

## Prerequisites

- AWS CLI and Boto3 library installed.
- Proper AWS credentials and permissions to access EC2, Auto Scaling, and CodeDeploy services.

## Usage

1. **Deployment**: Trigger this script as a response to a successful CodeDeploy deployment event.
2. **Execution**: The script performs the following actions:
   - Checks the deployment status.
   - If successful, it creates a new AMI from the deployed instance.
   - Dynamically retrieves the name of the Launch Template used by the ASG.
   - Creates a new version of the Launch Template with the new AMI.
   - Sets this version as the default for future ASG activities.

## Logging

Detailed logging is provided to track the progress and troubleshoot any issues during the execution.
