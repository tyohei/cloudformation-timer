import argparse
import collections
import pprint

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stack-name', '-s', required=True)
    args = parser.parse_args()

    client = boto3.client('cloudformation')
    paginator = client.get_paginator('describe_stack_events')
    kwargs = {
        'StackName': args.stack_name
    }

    stack_events = []
    for page in paginator.paginate(**kwargs):
        stack_events += page['StackEvents']

    merged_with_logical_resource_id = collections.defaultdict(lambda: [])
    # logical_resource_id
    # resource_type
    # resource_status
    # duration

    for event in stack_events:
        logical_resource_id = event['LogicalResourceId']
        resource_type = event['ResourceType']
        resource_status = event['ResourceStatus']
        timestamp = event['Timestamp']
        merged_with_logical_resource_id[logical_resource_id].append({
            'resource_type': resource_type,
            'resource_status': resource_status,
            'timestamp': timestamp
        })

    resource_creatation_times = {}
    for logical_resource_id in merged_with_logical_resource_id:
        events = merged_with_logical_resource_id[logical_resource_id]
        assert len(events)
        if events[0]['timestamp'] > events[1]['timestamp']:
            events[0], events[1] = events[1], events[0]

        resource_creatation_times[logical_resource_id] = \
            str(events[1]['timestamp'] - events[0]['timestamp'])
    pprint.pprint(resource_creatation_times)


if __name__ == '__main__':
    main()
