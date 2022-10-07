# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon CloudWatch to create
and manage custom metrics and alarms.
"""

from datetime import datetime, timedelta
import logging
from pprint import pprint
import random
import time
import boto3
import json
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)



class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""
    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource

    def list_metrics(self, namespace, name, recent=False):
        """
        Gets the metrics within a namespace that have the specified name.
        If the metric has no dimensions, a single metric is returned.
        Otherwise, metrics for all dimensions are returned.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param recent: When True, only metrics that have been active in the last
                       three hours are returned.
        :return: An iterator that yields the retrieved metrics.
        """
        try:
            kwargs = {'Namespace': namespace, 'MetricName': name}
            if recent:
                kwargs['RecentlyActive'] = 'PT3H'  # List past 3 hours only
            metric_iter = self.cloudwatch_resource.metrics.filter(**kwargs)
            logger.info("Got metrics for %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't get metrics for %s.%s.", namespace, name)
            raise
        else:
            return metric_iter

    def get_metric_statistics(self, namespace, name, dimensions, start, end, period, stat_types):
        """
        Gets statistics for a metric within a specified time span. Metrics are grouped
        into the specified period.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param start: The UTC start time of the time span to retrieve.
        :param end: The UTC end time of the time span to retrieve.
        :param period: The period, in seconds, in which to group metrics. The period
                       must match the granularity of the metric, which depends on
                       the metric's age. For example, metrics that are older than
                       three hours have a one-minute granularity, so the period must
                       be at least 60 and must be a multiple of 60.
        :param stat_types: The type of statistics to retrieve, such as average value
                           or maximum value.
        :return: The retrieved statistics for the metric.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            stats = metric.get_statistics(
                Dimensions=dimensions, StartTime=start, EndTime=end, Period=period, Statistics=stat_types)
            logger.info(
                "Got %s statistics for %s.", len(stats['Datapoints']), stats['Label'])
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", namespace, name)
            raise
        else:
            return stats

def find_resource_by_name(name, dict):
    i = 0

    for resource in dict['resources']:
        for key, value in resource.items():
            if key == 'name':
                if value == name:
                    return dict['resources'][i]
        i = i + 1

def show_results():
    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    period = 60 * 60 * 24

    f = open('../terraform-aws-flask/terraform.tfstate.backup', 'r')
    data = f.read()
    dict = json.loads(data)

    load_balancer_id = find_resource_by_name('load-balancer', dict)['instances'][0]['attributes']['arn_suffix']
    load_balancer_dimension = {'Name': 'LoadBalancer', 'Value': load_balancer_id}

    cluster1 = find_resource_by_name('attachments-cluster1-m4', dict)['instances']
    cluster1_id = find_resource_by_name('cluster1-target', dict)['instances'][0]['attributes']['arn_suffix']

    cluster2 = find_resource_by_name('attachments-cluster2-t2', dict)['instances']
    cluster2_id = find_resource_by_name('cluster2-target', dict)['instances'][0]['attributes']['arn_suffix']

    cluster1_instances_id = []
    for instance in cluster1:
        cluster1_instances_id.append(instance['attributes']['target_id'])

    cluster2_instances_id = []
    for instance in cluster2:
        cluster2_instances_id.append(instance['attributes']['target_id'])

    cw_wrapper = CloudWatchWrapper(boto3.resource('cloudwatch'))

    print('='*88)
    print("Benchmark results")
    print('='*88)
    print('\n')

    print('-'*80)
    print("Cluster 1 results")
    print('-'*80)
    print('\n')

    request_count1 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'RequestCount', [{'Name': 'TargetGroup', 'Value': cluster1_id}, load_balancer_dimension], start, end, period, ['Sum'])
    print("Request for cluster 1")
    print(f"Total: {request_count1['Datapoints'][0]['Sum']}")

    request_2xx_1 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_2XX_Count', [{'Name': 'TargetGroup', 'Value': cluster1_id}, load_balancer_dimension], start, end, period, ['Sum'])
    nbr_2xx_1 = 0 if len(request_2xx_1['Datapoints']) == 0 else request_2xx_1['Datapoints'][0]['Sum']
    print(f"Succesful: {nbr_2xx_1}")

    request_4xx_1 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_4XX_Count', [{'Name': 'TargetGroup', 'Value': cluster1_id}, load_balancer_dimension], start, end, period, ['Sum'])
    request_5xx_1 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_5XX_Count', [{'Name': 'TargetGroup', 'Value': cluster1_id}, load_balancer_dimension], start, end, period, ['Sum'])
    nbr_4xx_1 = 0 if len(request_4xx_1['Datapoints']) == 0 else request_4xx_1['Datapoints'][0]['Sum']
    nbr_5xx_1 = 0 if len(request_5xx_1['Datapoints']) == 0 else request_5xx_1['Datapoints'][0]['Sum']
    nbr_request_failed1 = nbr_4xx_1 + nbr_5xx_1
    print(f"Failed: {nbr_request_failed1}\n")

    response_time1 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'TargetResponseTime', [{'Name': 'TargetGroup', 'Value': cluster1_id}, load_balancer_dimension], start, end, period, ['Average'])
    response_time_avg1 = "Unavailabe" if len(response_time1['Datapoints']) == 0 else str(response_time1['Datapoints'][0]['Average'])
    print(f"Response time for cluster 1: {response_time_avg1}\n")


    for id in cluster1_instances_id:
        cpu_utilization = cw_wrapper.get_metric_statistics('AWS/EC2', 'CPUUtilization', [{'Name': 'InstanceId', 'Value': id}], start, end, period, ['Minimum', 'Maximum', 'Average'])
        print(f"CPU Utilization for machine: {id}")
        print(f"Minimum: {cpu_utilization['Datapoints'][0]['Minimum']}")
        print(f"Maximum: {cpu_utilization['Datapoints'][0]['Maximum']}")
        print(f"Average: {cpu_utilization['Datapoints'][0]['Average']}\n")
        
    print('-'*80)
    print("Cluster 2 results")
    print('-'*80)
    print('\n')

    request_count2 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'RequestCount', [{'Name': 'TargetGroup', 'Value': cluster2_id}, load_balancer_dimension], start, end, period, ['Sum'])
    print("Request for cluster 2")
    print(f"Total: {request_count2['Datapoints'][0]['Sum']}")

    request_2xx_2 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_2XX_Count', [{'Name': 'TargetGroup', 'Value': cluster2_id}, load_balancer_dimension], start, end, period, ['Sum'])
    nbr_2xx_2 = 0 if len(request_2xx_2['Datapoints']) == 0 else request_2xx_2['Datapoints'][0]['Sum']
    print(f"Succesful: {nbr_2xx_2}")

    request_4xx_2 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_4XX_Count', [{'Name': 'TargetGroup', 'Value': cluster2_id}, load_balancer_dimension], start, end, period, ['Sum'])
    request_5xx_2 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'HTTPCode_Target_5XX_Count', [{'Name': 'TargetGroup', 'Value': cluster2_id}, load_balancer_dimension], start, end, period, ['Sum'])
    nbr_4xx_2 = 0 if len(request_4xx_2['Datapoints']) == 0 else request_4xx_2['Datapoints'][0]['Sum']
    nbr_5xx_2 = 0 if len(request_5xx_2['Datapoints']) == 0 else request_5xx_2['Datapoints'][0]['Sum']
    nbr_request_failed2 = nbr_4xx_2 + nbr_5xx_2
    print(f"Failed: {nbr_request_failed2}\n")

    response_time2 = cw_wrapper.get_metric_statistics('AWS/ApplicationELB', 'TargetResponseTime', [{'Name': 'TargetGroup', 'Value': cluster2_id}, load_balancer_dimension], start, end, period, ['Average'])
    response_time_avg2 = "Unavailabe" if len(response_time2['Datapoints']) == 0 else str(response_time2['Datapoints'][0]['Average'])
    print(f"Response time for cluster 2: {response_time_avg2}\n")

    for id in cluster2_instances_id:
        cpu_utilization = cw_wrapper.get_metric_statistics('AWS/EC2', 'CPUUtilization', [{'Name': 'InstanceId', 'Value': id}], datetime.utcnow() - timedelta(days=1), datetime.utcnow(), 600, ['Minimum', 'Maximum', 'Average'])
        print(f"CPU Utilization for machine: {id}")
        print(f"Minimum: {cpu_utilization['Datapoints'][0]['Minimum']}")
        print(f"Maximum: {cpu_utilization['Datapoints'][0]['Maximum']}")
        print(f"Average: {cpu_utilization['Datapoints'][0]['Average']}\n")

if __name__ == '__main__':
    show_results()
