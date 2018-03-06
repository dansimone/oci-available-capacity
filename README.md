# OCI Available Capacity Tools 

This repo contains tools to help display OCI available capacity in a tenancy and randomly choose 
available shapes.

## Prerequisites
- Install [Python](https://www.python.org/downloads) 2.7 or later.
- Install required Python packages:

```
pip install -r requirements.txt
```

- Details (OCID, private key, fingerprint) for a user in the "Auditors" or "Administrators" OCI group.

## Config File

Create a config file containing tenancy and user details in the "OCI" section, for example:

```
[OCI]
user: ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
tenancy: ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
key_file: /tmp/my_api_key.pem
fingerprint: aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa
```

And sections for the service limits of each region: a list of compute shapes, and their capacities _per-AD_, for example:
 
```
[us-phoenix-1]
VM.Standard1.1: 5
VM.Standard1.2: 5
VM.Standard1.4: 5
VM.Standard1.8: 5

[us-ashburn-1]
VM.Standard1.1: 3
VM.Standard1.2: 2
VM.Standard1.4: 5
VM.Standard1.8: 1
```

Currently, these limits must be manually retrieved from the OCI Console: Region->Manage Regions->Service Limits.  Once
OCI exposes a REST API to retrieve these, this tool can be changed to use that, thus eliminating the need for the above 
sections of the config file. 

## Available Compute Capacity Tool

This tool prints out the currently available compute capacity for each shape:

```
python compute_capacity.py --config /tmp/my_config
```

The output is something like this, showing the available capacity for each region/shape/AD:

```
************************************************
Available shapes in us-ashburn-1
************************************************
VM.Standard1.1: AD1: 3, AD2: 1, AD3: 1
VM.Standard1.2: AD1: 0, AD2: 1, AD3: 1
VM.Standard1.4: AD1: 5, AD2: 1, AD3: 4
VM.Standard1.8: AD1: 0, AD2: 0, AD3: 1
************************************************
Available shapes in us-phoenix-1
************************************************
VM.Standard1.1: AD1: 3, AD2: 1, AD3: 1
VM.Standard1.2: AD1: 0, AD2: 1, AD3: 2
VM.Standard1.4: AD1: 4, AD2: 2, AD3: 2
VM.Standard1.8: AD1: 0, AD2: 1, AD3: 1
```

## Compute Randomizer Tool

This tool randomly picks a region and set of shapes/ADs that satisfy a set of compute "requests".  A compute request
is defined as a logical name, and a list of compute instances required in separate ADs.  The user-specified "requests" 
is then of the following form: `"<request1_name>:<comma_separated_instances_per_ad> <request2_name:<comma_separated_instances_per_ad> ..."`.
Any region able to satify all requests has equal chance of being chosen.  And any shape/ad_list within the region that is
able to satisfy a given request has equal chance of being chosen, with the most demanding requests satisfied first.

A couple of examples for "requests":
- `--requests "logging:2"` will choose a shape for "logging" with 2 instances in one AD.
- `--requests "logging:2,1,3"` will choose a shape for "logging" with 2 instances in one AD, 1 instance in another, and 3 in another.
- `--requests "master:1,2 worker:2,1,3"` will chose:
  - A shape for "master" with 1 instance in one AD and 2 instances in another.
  - A shape for "worker" with 2 instances in one AD, 1 instance in another, and 3 in yet another.

```
python compute_capacity.py --config /tmp/my_config --requests "master:1,2 worker:2,1,3"
```

The output of the tool shows the chosen region, and for each request, the chosen shape and AD list that satisfy the request.
For example:

```
REGION=us-ashburn-1
MASTER_SHAPE=VM.Standard1.4
MASTER_AD1=1
MASTER_AD2=3
MASTER_ADS=1,3
WORKER_SHAPE=VM.Standard1.8
WORKER_AD1=3
WORKER_AD2=1
MASTER_AD3=2
MASTER_ADS=3,1,2
```