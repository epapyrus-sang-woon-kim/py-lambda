import boto3
import json
import logging

# CodeDeploy 성공 후, 해당 ASG의 Launch Template을 최신 AMI로 업데이트하는 Lambda Script

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
asg_client = boto3.client('autoscaling')


def lambda_handler(event, context):
    # SNS 메시지 파싱
    message = json.loads(event['Records'][0]['Sns']['Message'])
    deployment_group_name = message['deploymentGroupName']
    deployment_status = message['status']

    logger.info("Deployment Group Name: %s", deployment_group_name)
    logger.info("Deployment Status: %s", deployment_status)
    logger.info("message: %s", message)

    if deployment_status == 'SUCCEEDED':
        # codeDeploy 의 ASG 이름
        code_deploy_asg = f"CodeDeploy_{deployment_group_name}_{message['deploymentId']}"
        logger.info("code_deploy_asg: %s", code_deploy_asg)

        try:
            # Auto Scaling 그룹의 인스턴스 정보 조회
            asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[code_deploy_asg])
            logger.info("asg_response: %s", asg_response)

            instance_id = asg_response['AutoScalingGroups'][0]['Instances'][0]['InstanceId']
            logger.info("Instance ID: %s", instance_id)

            launch_template_name = asg_response['AutoScalingGroups'][0]['LaunchTemplate']['LaunchTemplateName']
            logger.info("Launch Template Name: %s", launch_template_name)

        except Exception as e:
            logger.error("Error fetching instance from ASG: %s", e)
            return {'statusCode': 500, 'body': json.dumps("Error fetching instance.")}

        # 새로운 AMI 생성
        try:
            ami_response = ec2_client.create_image(
                InstanceId=instance_id,
                Name='New_AMI_from_Deployment_' + message['deploymentId'],
                NoReboot=True
            )
            ami_id = ami_response['ImageId']
            logger.info("AMI Created: %s", ami_id)
        except Exception as e:
            logger.error("Error creating AMI: %s", e)
            return {'statusCode': 500, 'body': json.dumps("Error creating AMI.")}

        # Launch Template 업데이트
        try:
            lt_response = ec2_client.create_launch_template_version(
                LaunchTemplateName=str(launch_template_name),
                SourceVersion='$Latest',
                LaunchTemplateData={
                    'ImageId': ami_id
                }
            )
            new_version_number = lt_response['LaunchTemplateVersion']['VersionNumber']
            logger.info("Launch Template Updated. New Version Number: %s", new_version_number)

            # Launch Template의 기본 버전 설정
            modify_lt_response = ec2_client.modify_launch_template(
                LaunchTemplateName='PdfCo-Net-AMI-ASG-template',
                DefaultVersion=str(new_version_number)
            )

        except Exception as e:
            logger.error("Error updating Launch Template: %s", e)
            return {'statusCode': 500, 'body': json.dumps("Error updating Launch Template.")}

        return {
            'statusCode': 200,
            'body': json.dumps(f"AMI Created: {ami_id}, Launch Template Updated Response: {modify_lt_response}")
        }
    else:
        logger.info("Deployment did not succeed. No action taken.")
        return {
            'statusCode': 200,
            'body': json.dumps("Deployment did not succeed. No action taken.")
        }
