import boto3

# PARSING FLAGS
# --region -r
# --profile -p
# --secret-key
# --access-key

# SERVICES
# VPC: VPCs, Subnets, Route Tables, Internet Gateways, NAT Gateways
# EC2: Instances, Autoscaling Groups, Launch Configurations, Security Groups
# ELB: Network Load Balancers, Application Load Balancers
# SQS: Queues
# S3: Buckets

aws_region = 'eu-west-1'
aws_profile = 'deals'
tag_filter = [{'Name': 'tag-key', 'Values': ['aws:cloudformation:logical-id']}]
tag_search = '{}[].[Tags[?Key==`aws:cloudformation:logical-id`]]'
session = boto3.session.Session(region_name=aws_region, profile_name=aws_profile)


def coverage(session):
    vpc(session)
    ec2(session)


def vpc(session):
    print('VPC (Virtual Private Cloud)')
    print('===============================')
    aws = session.resource('ec2')

    # VPCs
    all_vpcs = list(aws.vpcs.all())
    cfn_vpcs = list(aws.vpcs.filter(Filters=tag_filter))
    vpc_coverage = percentage(all_vpcs, cfn_vpcs)
    print('VPCs:\t\t{}/{} ({}%)'.format(len(cfn_vpcs), len(all_vpcs), vpc_coverage))

    # Subnets
    all_subnets = list(aws.subnets.all())
    cfn_subnets = list(aws.subnets.filter(Filters=tag_filter))
    subnet_coverage = percentage(all_subnets, cfn_subnets)
    print('Subnets:\t{}/{} ({}%)'.format(len(cfn_subnets), len(all_subnets), subnet_coverage))

    # Route Tables
    all_route_tables = list(aws.route_tables.all())
    cfn_route_tables = list(aws.route_tables.filter(Filters=tag_filter))
    route_table_coverage = percentage(all_route_tables, cfn_route_tables)
    print('Route Tables:\t{}/{} ({}%)'.format(len(cfn_route_tables), len(all_route_tables), route_table_coverage))

    # Internet Gateways
    all_net_gateways = list(aws.internet_gateways.all())
    cfn_net_gateways = list(aws.internet_gateways.filter(Filters=tag_filter))
    net_gateway_coverage = percentage(all_net_gateways, cfn_net_gateways)
    print('Net Gateways:\t{}/{} ({}%)'.format(len(cfn_net_gateways), len(all_net_gateways), net_gateway_coverage))

    # NAT Gateways
    aws = session.client('ec2')
    all_nat_gateways = aws.describe_nat_gateways().get('NatGateways')
    cfn_nat_gateways = aws.describe_nat_gateways(Filters=tag_filter).get('NatGateways')
    nat_gateway_coverage = percentage(all_nat_gateways, cfn_nat_gateways)
    print('NAT Gateways:\t{}/{} ({}%)'.format(len(cfn_nat_gateways), len(all_nat_gateways), nat_gateway_coverage))

    # Average Coverage
    avg = average([vpc_coverage, subnet_coverage, route_table_coverage, net_gateway_coverage, nat_gateway_coverage])
    print('-------------------------------')
    print('VPC Average:\t{}%\n'.format(avg))
    return avg


def ec2(session):
    print('EC2 (Elastic Compute Cloud)')
    print('=======================================')
    aws = session.resource('ec2')

    # Instances
    all_instances = list(aws.instances.all())
    cfn_instances = list(aws.instances.filter(Filters=tag_filter))
    instance_coverage = percentage(all_instances, cfn_instances)
    print('Instances:\t\t{}/{} ({}%)'.format(len(cfn_instances), len(all_instances), instance_coverage))

    # Security Groups
    all_security_groups = list(aws.security_groups.all())
    cfn_security_groups = list(aws.security_groups.filter(Filters=tag_filter))
    security_group_coverage = percentage(all_security_groups, cfn_security_groups)
    print('Security Groups:\t{}/{} ({}%)'.format(len(cfn_security_groups), len(all_security_groups), security_group_coverage))

    # Autoscaling Groups
    aws = session.client('autoscaling')
    paginator = aws.get_paginator('describe_auto_scaling_groups')
    page_iterator = paginator.paginate(PaginationConfig={'PageSize': 100})
    all_autoscaling_groups = aws.describe_auto_scaling_groups().get('AutoScalingGroups')
    cfn_autoscaling_groups = list(page_iterator.search(tag_search.format('AutoScalingGroups')))
    autoscaling_group_coverage = percentage(all_autoscaling_groups, cfn_autoscaling_groups)
    print('Autoscaling Groups:\t{}/{} ({}%)'.format(len(cfn_autoscaling_groups), len(all_autoscaling_groups), autoscaling_group_coverage))

    # Launch Configurations
    paginator = aws.get_paginator('describe_launch_configurations')
    page_iterator = paginator.paginate(PaginationConfig={'PageSize': 100})
    all_launch_config = aws.describe_launch_configurations().get('LaunchConfigurations')
    cfn_launch_config = list(page_iterator.search(tag_search.format('LaunchConfigurations')))
    launch_config_coverage = percentage(all_launch_config, cfn_launch_config)
    print('Launch Configurations:\t{}/{} ({}%)'.format(len(cfn_launch_config), len(all_launch_config), launch_config_coverage))

    # Load Balancers

    # Average Coverage
    avg = average([instance_coverage, security_group_coverage, autoscaling_group_coverage, launch_config_coverage])
    print('---------------------------------------')
    print('EC2 Average:\t\t{}%\n'.format(avg))
    return avg


def cfn():
    resources = 0
    return resources


def average(numbers):
    result = sum(numbers) / max(len(numbers), 1)
    return round(result, 1)


def percentage(total, count):
    result = 100 * len(count) / max(len(total), 1)
    return round(result, 1)


coverage(session)
