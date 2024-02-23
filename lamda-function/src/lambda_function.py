import sys, os

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)

import logging, datetime, json
from voluptuous import MultipleInvalid, Invalid
from cfn_lambda_handler import Handler
import boto3

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

ec2_client = boto3.client('ec2')


def format_json(data):
    return json.dumps(data, default=lambda d: d.isoformat() if isinstance(d, datetime.datetime) else str(d))


# Set handler as the entry point for Lambda
handler = Handler()


def create_prefix_list(prefix_list_name, max_entries, entries, address_family, tags):
    log.info('Create Prefix list')
    return ec2_client.create_managed_prefix_list(
        PrefixListName=prefix_list_name,
        Entries=entries,
        MaxEntries=int(max_entries),
        TagSpecifications=[
            {
                'ResourceType': 'prefix-list',
                'Tags': tags
            },
        ],
        AddressFamily=address_family
    )


def delete_prefix_list(prefix_list_id):
    return ec2_client.delete_managed_prefix_list(
        PrefixListId=prefix_list_id
    )


def list_prefix_lists(filters=[]):
    log.info('List prefix lists')
    if not filters:
        return ec2_client.describe_managed_prefix_lists()
    else:
        return ec2_client.describe_managed_prefix_lists(
            Filters=filters
        )


def error_handler(func):
    def handle_task_result(event, context):
        try:
            event = func(event, context)
        except (Invalid, MultipleInvalid) as e:
            event['Status'] = "FAILED"
            event['Reason'] = "One or more invalid event properties: %s" % e
        if event.get('Status') == "FAILED":
            log.error(event['Reason'])
        return event

    return handle_task_result


def get_cidr_entries(entries):
    cidr_entries = []
    if entries is not None:
        for cidr in entries:
            cidr_entries.append(
                {
                    "Cidr": cidr,
                    "Description": "prefix list"

                }
            )
    return cidr_entries


# Create requests
@handler.create
@error_handler
def handle_create(event, context):
    log.info("Received create event: %s" % format_json(event))
    resource_props = event.get('ResourceProperties')
    if resource_props is None:
        raise Exception("Resource Properties cannot be empty")
    log.info('Received properties %s' % format_json(resource_props))
    prefix_list_name = resource_props["PrefixListName"]
    max_entries = resource_props["MaxEntries"]
    entries = resource_props["Entries"]
    cidr_list = get_cidr_entries(entries)
    print(cidr_list)
    address_family = resource_props["AddressFamily"]
    tags = resource_props["Tags"]
    response = create_prefix_list(prefix_list_name, max_entries, cidr_list, address_family, tags)
    log.info('Response')
    log.info(response)
    if response is not None:
        event['PhysicalResourceId'] = response["PrefixList"]["PrefixListId"]
    return event


# Update requests
@handler.update
@error_handler
def handle_update(event, context):
    log.info("Received update event: %s" % format_json(event))
    resource_props = event.get('ResourceProperties')
    if resource_props is None:
        raise Exception("Resource Properties cannot be empty")
    log.info('Received properties %s' % format_json(resource_props))
    prefix_list_name = resource_props["PrefixListName"]
    max_entries = resource_props["MaxEntries"]
    entries = resource_props["Entries"]
    cidr_list = get_cidr_entries(entries)
    print(cidr_list)
    address_family = resource_props["AddressFamily"]
    tags = resource_props["Tags"]
    response = create_prefix_list(prefix_list_name, max_entries, cidr_list, address_family, tags)
    log.info('Response')
    log.info(response)
    if response is not None:
        event['PhysicalResourceId'] = response["PrefixList"]["PrefixListId"]
    return event


# Delete requests
@handler.delete
@error_handler
def handle_delete(event, context):
    log.info("Received delete event: %s" % format_json(event))
    resource_props = event.get('ResourceProperties')
    if resource_props is None:
        raise Exception("Resource Properties cannot be empty")
    log.info('Received properties %s' % format_json(resource_props))
    prefix_list_name = resource_props["PrefixListName"]
    filters = [
        {
            'Name': 'prefix-list-name',
            'Values': [
                prefix_list_name,
            ]
        }
    ]
    response = list_prefix_lists(filters)
    print(response)
    if response is not None:
        prefix_lists = response["PrefixLists"]
        prefix_list = prefix_lists[0]
        print(prefix_list)
        prefix_list_id = prefix_list["PrefixListId"]
        print('Prefix List Id to be deleted ' + prefix_list_id)
        delete_response = delete_prefix_list(prefix_list_id)
        print(delete_response)
    return event
